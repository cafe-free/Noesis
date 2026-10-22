import json
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

import httpx

from apps.api.core.auth import (
    hash_password,
    issue_tokens,
    verify_password,
)
from apps.api.core.db import get_supabase
from apps.api.routes.exercise_attempts import (
    CheckAnswerRequest,
    check_exercise_answer as direct_check_answer,
)
from apps.api.schemas.exercise import ExerciseInDB, ExerciseResponse
from apps.api.services.content_extractor import (
    extract_clean_text_from_html,
    extract_text_from_document,
    fetch_web_page,
    validate_url,
)
from apps.api.services.generation import QuizGenerationService
from apps.api.services.rag_service import RAGService


SESSION_DIR = Path.home() / ".config" / "noesis"
SESSION_FILE = SESSION_DIR / "session.json"


class TUIClient:
    """
    Client for Noesis TUI. Connects to FastAPI backend via HTTP if available,
    or falls back to direct Supabase database and internal services seamlessly.
    Supports persistent local sessions to allow pre-authenticating before launching the TUI.
    """

    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or os.environ.get("API_URL") or "http://localhost:8000").rstrip("/")
        self.token: str | None = None
        self.current_user: dict[str, Any] | None = None
        self.db = get_supabase()
        self.rag_service = RAGService(db=self.db)
        self.gen_service = QuizGenerationService(db=self.db)
        self._load_saved_session()

    def _load_saved_session(self) -> None:
        """Loads credentials from disk if previously authenticated."""
        if not SESSION_FILE.exists():
            return
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.token = data.get("token")
            self.current_user = data.get("user")
        except Exception:
            self.token = None
            self.current_user = None

    def save_session(self, token: str, user: dict[str, Any]) -> None:
        """Persists session credentials to disk."""
        try:
            SESSION_DIR.mkdir(parents=True, exist_ok=True)
            payload = {
                "token": token,
                "user": user,
                "created_at": datetime.now(UTC).isoformat(),
            }
            with open(SESSION_FILE, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            os.chmod(SESSION_FILE, 0o600)
        except Exception:
            pass

    def clear_saved_session(self) -> None:
        """Removes saved session from disk."""
        try:
            if SESSION_FILE.exists():
                SESSION_FILE.unlink()
        except Exception:
            pass

    def has_saved_session(self) -> bool:
        """Checks if a valid user session is stored."""
        return bool(self.token and self.current_user)

    def _auth_headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def login(self, email: str, password: str) -> dict[str, Any]:
        """Authenticates user with email and password."""
        clean_email = email.strip().lower()
        # 1. Try HTTP server
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.post(
                    f"{self.base_url}/auth/login",
                    json={"email": clean_email, "password": password},
                )
                if res.status_code == 200:
                    data = res.json()
                    self.token = data.get("access_token")
                    user_res = await client.get(
                        f"{self.base_url}/progress/me",
                        headers=self._auth_headers(),
                    )
                    if user_res.status_code == 200:
                        self.current_user = user_res.json()
                    else:
                        self.current_user = {"email": clean_email, "name": clean_email.split("@")[0]}
                    self.save_session(self.token, self.current_user)
                    return {"token": self.token, "user": self.current_user}
                elif res.status_code == 401:
                    raise Exception("Invalid email or password.")
        except httpx.ConnectError:
            pass
        except Exception as e:
            if "Invalid email" in str(e):
                raise

        # 2. Fallback to direct DB
        result = self.db.table("users").select("*").eq("email", clean_email).execute()
        user = result.data[0] if result.data else None
        if not user or not user.get("password_hash") or not verify_password(password, user["password_hash"]):
            raise Exception("Invalid email or password.")

        tokens = issue_tokens(self.db, str(user["id"]))
        self.token = tokens["access_token"] if isinstance(tokens, dict) else tokens.access_token
        self.current_user = await self.get_profile(user_id=str(user["id"]))
        self.save_session(self.token, self.current_user)
        return {"token": self.token, "user": self.current_user}

    async def register(
        self, email: str, password: str, username: str = "", learning_language: str = "Spanish"
    ) -> dict[str, Any]:
        """Registers a new user account."""
        clean_email = email.strip().lower()
        clean_user = username.strip() or clean_email.split("@")[0]

        # 1. Try HTTP server
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.post(
                    f"{self.base_url}/auth/register",
                    json={"email": clean_email, "password": password, "username": clean_user},
                )
                if res.status_code in (200, 201):
                    data = res.json()
                    self.token = data.get("access_token")
                    self.current_user = await self.get_profile()
                    self.save_session(self.token, self.current_user)
                    return {"token": self.token, "user": self.current_user}
                elif res.status_code == 409:
                    raise Exception("An account with this email already exists.")
                elif res.status_code == 422:
                    raise Exception("Password must be at least 8 characters.")
        except httpx.ConnectError:
            pass
        except Exception as e:
            if "already exists" in str(e) or "Password must be" in str(e):
                raise

        # 2. Fallback to direct DB
        existing = self.db.table("users").select("id").eq("email", clean_email).execute()
        if existing.data:
            raise Exception("An account with this email already exists.")

        result = (
            self.db.table("users")
            .insert(
                {
                    "email": clean_email,
                    "username": clean_user,
                    "password_hash": hash_password(password),
                    "auth_provider": "password",
                }
            )
            .execute()
        )
        if not result.data:
            raise Exception("Failed to create user account.")

        user_id = str(result.data[0]["id"])
        tokens = issue_tokens(self.db, user_id)
        self.token = tokens["access_token"] if isinstance(tokens, dict) else tokens.access_token
        self.current_user = await self.get_profile(user_id=user_id)
        self.save_session(self.token, self.current_user)
        return {"token": self.token, "user": self.current_user}

    async def demo_login(self) -> dict[str, Any]:
        """Fast-logins using a demo account or creates one if non-existent."""
        try:
            return await self.login("alex@example.com", "password123")
        except Exception:
            try:
                return await self.register("alex@example.com", "password123", username="Alex")
            except Exception:
                # If password differs, create a random demo account
                demo_id = str(uuid.uuid4())[:6]
                return await self.register(
                    f"demo_{demo_id}@example.com", "password123", username=f"Demo_{demo_id}"
                )

    def logout(self) -> None:
        """Clears local session tokens and saved session on disk."""
        self.clear_saved_session()
        self.token = None
        self.current_user = None

    async def get_profile(self, user_id: str | None = None) -> dict[str, Any]:
        """Retrieves aggregated user progress and profile metrics."""
        # Try HTTP
        if self.token:
            try:
                async with httpx.AsyncClient(timeout=4.0) as client:
                    res = await client.get(f"{self.base_url}/progress/me", headers=self._auth_headers())
                    if res.status_code == 200:
                        return res.json()
            except Exception:
                pass

        uid = user_id or (self.current_user.get("id") if self.current_user else None)
        if not uid:
            return {
                "name": "Learner",
                "email": "learner@example.com",
                "learningLanguage": "Spanish",
                "currentLevel": "A1",
                "streakDays": 1,
                "totalXp": 0,
                "todayXp": 0,
                "dailyGoalXp": 50,
                "hearts": 5,
                "maxHearts": 5,
            }

        # Calculate from DB
        attempts = self.db.table("quiz_attempts").select("*").eq("user_id", str(uid)).execute().data or []
        total_correct = sum(int(a.get("correct_answers") or 0) for a in attempts)
        total_xp = total_correct * 10

        user_info = self.db.table("users").select("*").eq("id", str(uid)).execute().data
        username = user_info[0].get("username") if user_info else "Learner"
        email = user_info[0].get("email") if user_info else "learner@example.com"

        streak = max(1, len({a.get("completed_at", "")[:10] for a in attempts if a.get("completed_at")}))

        profile = {
            "id": uid,
            "name": username or email.split("@")[0],
            "email": email,
            "learningLanguage": "Spanish",
            "currentLevel": "A1",
            "streakDays": streak,
            "totalXp": total_xp,
            "todayXp": min(50, total_xp % 50),
            "dailyGoalXp": 50,
            "hearts": 5,
            "maxHearts": 5,
        }
        self.current_user = profile
        return profile

    async def get_weaknesses(self) -> list[dict[str, Any]]:
        """Retrieves weak area concepts needing reinforcement."""
        if self.token:
            try:
                async with httpx.AsyncClient(timeout=4.0) as client:
                    res = await client.get(
                        f"{self.base_url}/progress/me/weaknesses", headers=self._auth_headers()
                    )
                    if res.status_code == 200:
                        return res.json()
            except Exception:
                pass

        uid = self.current_user.get("id") if self.current_user else None
        if not uid:
            return []

        attempts = self.db.table("quiz_attempts").select("id").eq("user_id", str(uid)).execute().data or []
        att_ids = [str(a["id"]) for a in attempts]
        if not att_ids:
            return []

        mistakes = (
            self.db.table("exercise_attempts")
            .select("*")
            .in_("quiz_attempt_id", att_ids)
            .eq("is_correct", False)
            .execute()
            .data
            or []
        )

        output = []
        for i, m in enumerate(mistakes[:5]):
            output.append(
                {
                    "id": str(m["id"]),
                    "topic": "Grammar & Conjugation",
                    "concept": f"Exercise {m.get('exercise_id', '')[:8]}",
                    "accuracyRate": 50,
                    "mistakeCount": 1,
                    "lastPracticed": "Recently",
                }
            )
        return output

    async def list_quizzes(self) -> list[dict[str, Any]]:
        """Fetches available quizzes."""
        if self.token:
            try:
                async with httpx.AsyncClient(timeout=4.0) as client:
                    res = await client.get(f"{self.base_url}/quizzes", headers=self._auth_headers())
                    if res.status_code == 200:
                        return res.json()
            except Exception:
                pass

        res = self.db.table("quizzes").select("*").order("created_at", desc=True).execute()
        quizzes = res.data or []
        for q in quizzes:
            # Get exercise count
            ex_res = (
                self.db.table("exercises")
                .select("id")
                .eq("quiz_id", str(q["id"]))
                .execute()
            )
            q["exercise_count"] = len(ex_res.data or [])
        return quizzes

    async def get_quiz(self, quiz_id: str) -> dict[str, Any]:
        """Retrieves quiz details and sanitized interactive exercises."""
        if self.token:
            try:
                async with httpx.AsyncClient(timeout=4.0) as client:
                    res = await client.get(
                        f"{self.base_url}/quizzes/{quiz_id}", headers=self._auth_headers()
                    )
                    if res.status_code == 200:
                        return res.json()
            except Exception:
                pass

        q_res = self.db.table("quizzes").select("*").eq("id", str(quiz_id)).execute()
        if not q_res.data:
            raise Exception("Quiz not found.")
        quiz = q_res.data[0]

        ex_res = (
            self.db.table("exercises")
            .select("*")
            .eq("quiz_id", str(quiz_id))
            .order("position")
            .execute()
        )
        raw_exercises = ex_res.data or []
        sanitized = [ExerciseResponse.sanitize(ExerciseInDB(**ex)).model_dump(mode="json") for ex in raw_exercises]
        quiz["exercises"] = sanitized
        return quiz

    async def check_answer(self, quiz_id: str, exercise_id: str, user_answer: Any) -> dict[str, Any]:
        """Submits an answer for server-side evaluation."""
        if self.token:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    res = await client.post(
                        f"{self.base_url}/exercise-attempts/check",
                        json={
                            "quiz_id": quiz_id,
                            "exercise_id": exercise_id,
                            "user_answer": user_answer,
                        },
                        headers=self._auth_headers(),
                    )
                    if res.status_code == 200:
                        return res.json()
            except Exception:
                pass

        # Direct DB evaluation
        req = CheckAnswerRequest(
            quiz_id=UUID(quiz_id),
            exercise_id=UUID(exercise_id),
            user_answer=user_answer,
        )
        checked = await direct_check_answer(req, db=self.db)
        return checked.model_dump(mode="json")

    async def submit_quiz_attempt(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Submits completed quiz session with answers and mistakes."""
        if self.token:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    res = await client.post(
                        f"{self.base_url}/quiz-attempts",
                        json=payload,
                        headers=self._auth_headers(),
                    )
                    if res.status_code in (200, 201):
                        return res.json()
            except Exception:
                pass

        uid = self.current_user.get("id") if self.current_user else str(uuid.uuid4())
        record = {
            "id": str(uuid.uuid4()),
            "user_id": str(uid),
            "quiz_id": str(payload.get("quiz_id")),
            "score": payload.get("score", 0),
            "total_questions": payload.get("total_questions", 1),
            "correct_answers": payload.get("score", 0),
            "completed_at": datetime.now(UTC).isoformat(),
        }
        res = self.db.table("quiz_attempts").insert(record).execute()
        return res.data[0] if res.data else record

    async def generate_quiz_job(
        self, language: str, level: str, topic: str, count: int = 4
    ) -> str | None:
        """Triggers AI synthesis of a dynamic practice quiz."""
        if self.token:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    res = await client.post(
                        f"{self.base_url}/generation-jobs",
                        json={"language": language, "level": level, "topic": topic, "count": count},
                        headers=self._auth_headers(),
                    )
                    if res.status_code in (200, 201):
                        job = res.json()
                        return job.get("quiz_id")
            except Exception:
                pass

        job_id = str(uuid.uuid4())
        quiz_id = await self.gen_service.execute_job(
            job_id=job_id,
            language=language,
            level=level,
            topic=topic,
            count=count,
        )
        return quiz_id

    async def list_references(self) -> list[dict[str, Any]]:
        """Lists user's private knowledge base reference materials."""
        if self.token:
            try:
                async with httpx.AsyncClient(timeout=4.0) as client:
                    res = await client.get(f"{self.base_url}/references", headers=self._auth_headers())
                    if res.status_code == 200:
                        return res.json()
            except Exception:
                pass

        uid = self.current_user.get("id") if self.current_user else None
        if not uid:
            return []
        refs = await self.rag_service.list_user_references(user_id=UUID(str(uid)))
        return [r.model_dump(mode="json") for r in refs]

    async def add_url_reference(self, url: str, title: str | None = None) -> dict[str, Any]:
        """Ingests and indexes a website reference."""
        if self.token:
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    res = await client.post(
                        f"{self.base_url}/references/url",
                        json={"url": url, "title": title},
                        headers=self._auth_headers(),
                    )
                    if res.status_code in (200, 201):
                        return res.json()
                    elif res.status_code >= 400:
                        raise Exception(res.json().get("detail", "Failed to add website."))
            except httpx.ConnectError:
                pass
            except Exception as e:
                if "Failed" in str(e) or "URL" in str(e):
                    raise

        uid = self.current_user.get("id") if self.current_user else str(uuid.uuid4())
        val_url = validate_url(url)
        html, final_url, meta = await fetch_web_page(val_url)
        clean_text, ext_title, doc_meta = extract_clean_text_from_html(html, fallback_url=final_url)
        doc = await self.rag_service.ingest_reference(
            user_id=UUID(str(uid)),
            source_type="url",
            title=title or ext_title,
            content=clean_text,
            source_url=final_url,
            metadata={**meta, **doc_meta},
        )
        return doc.model_dump(mode="json")

    async def upload_file_reference(self, file_path: str, title: str | None = None) -> dict[str, Any]:
        """Ingests and indexes a local document reference (.pdf, .txt, .md)."""
        if not os.path.exists(file_path):
            raise Exception(f"File not found: {file_path}")

        file_name = os.path.basename(file_path)
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        clean_text, ext_title, meta = extract_text_from_document(file_bytes, file_name=file_name)
        fname_lower = file_name.lower()
        stype = "pdf" if fname_lower.endswith(".pdf") else ("md" if fname_lower.endswith((".md", ".markdown")) else "txt")

        uid = self.current_user.get("id") if self.current_user else str(uuid.uuid4())
        doc = await self.rag_service.ingest_reference(
            user_id=UUID(str(uid)),
            source_type=stype,
            title=title or ext_title,
            content=clean_text,
            file_name=file_name,
            metadata=meta,
        )
        return doc.model_dump(mode="json")

    async def search_references(self, query: str, top_k: int = 4) -> list[dict[str, Any]]:
        """Performs semantic vector search across user's private knowledge base."""
        if self.token:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    res = await client.post(
                        f"{self.base_url}/references/search",
                        json={"query": query, "top_k": top_k},
                        headers=self._auth_headers(),
                    )
                    if res.status_code == 200:
                        return res.json().get("results", [])
            except Exception:
                pass

        uid = self.current_user.get("id") if self.current_user else None
        if not uid:
            return []
        results = await self.rag_service.search_user_knowledge(user_id=UUID(str(uid)), query=query, top_k=top_k)
        return [r.model_dump(mode="json") for r in results]

    async def delete_reference(self, doc_id: str) -> None:
        """Deletes a reference material and its vector embeddings."""
        if self.token:
            try:
                async with httpx.AsyncClient(timeout=4.0) as client:
                    await client.delete(f"{self.base_url}/references/{doc_id}", headers=self._auth_headers())
                    return
            except Exception:
                pass

        uid = self.current_user.get("id") if self.current_user else None
        if uid:
            await self.rag_service.delete_user_reference(user_id=UUID(str(uid)), document_id=UUID(doc_id))
