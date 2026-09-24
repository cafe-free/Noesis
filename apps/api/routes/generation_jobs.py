from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from apps.api.core.db import get_supabase
from apps.api.core.auth import get_current_user
from apps.api.schemas.generation_job import (
    GenerationJobCreate,
    GenerationJobResponse,
    GenerationJobUpdate,
)

router = APIRouter(prefix="/generation-jobs", tags=["generation-jobs"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=List[GenerationJobResponse])
async def get_generation_jobs(
    status_filter: Optional[str] = None,
    quiz_id: Optional[UUID] = None,
    db: Client = Depends(get_supabase),
):
    query = db.table("generation_jobs").select("*")
    if status_filter:
        query = query.eq("status", status_filter)
    if quiz_id:
        query = query.eq("quiz_id", str(quiz_id))
    res = query.execute()
    return res.data or []


@router.get("/{job_id}", response_model=GenerationJobResponse)
async def get_generation_job(
    job_id: UUID,
    db: Client = Depends(get_supabase),
):
    res = db.table("generation_jobs").select("*").eq("id", str(job_id)).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation job not found")
    return res.data[0]


from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from apps.api.core.db import get_supabase
from apps.api.core.auth import get_current_user
from apps.api.schemas.generation_job import (
    GenerationJobCreate,
    GenerationJobResponse,
    GenerationJobUpdate,
)

router = APIRouter(prefix="/generation-jobs", tags=["generation-jobs"], dependencies=[Depends(get_current_user)])


def _generate_exercises_for_topic(language: str, level: str, topic: str):
    """Generate tailored exercises for the specified language, level, and topic."""
    lang = language.capitalize()
    t = topic.lower()

    if "coffee" in t or "cafe" in t:
        mcq_prompt = f"How do you order a coffee in {lang}?"
        mcq_options = ["Un café, por favor.", "Una cerveza, gracias.", "Una manzana, por favor."] if lang == "Spanish" else [
            "Un café, s'il vous plaît.", "Une bière, merci.", "Une pomme, s'il vous plaît."
        ]
        mcq_answer = mcq_options[0]

        fib_prompt = "Complete the phrase: \"Una mesa para dos, por _____\"" if lang == "Spanish" else "Complete the phrase: \"Une table pour deux, s'il vous _____\""
        fib_answer = "favor" if lang == "Spanish" else "plaît"
        fib_hint = "Spanish for please" if lang == "Spanish" else "French for please"

        wo_prompt = "Arrange the sentence: 'The check, please.'"
        wo_tokens = ["La", "cuenta", "por", "favor", "el", "menú"] if lang == "Spanish" else ["L'addition", "s'il", "vous", "plaît", "le", "menu"]
        wo_order = ["La", "cuenta", "por", "favor"] if lang == "Spanish" else ["L'addition", "s'il", "vous", "plaît"]

        matching_pairs = [
            {"left": "Coffee", "right": "El café" if lang == "Spanish" else "Le café"},
            {"left": "Bill / Check", "right": "La cuenta" if lang == "Spanish" else "L'addition"},
            {"left": "Water", "right": "El agua" if lang == "Spanish" else "L'eau"},
            {"left": "Menu", "right": "El menú" if lang == "Spanish" else "Le menu"},
        ]
    elif "food" in t or "din" in t or "restaurant" in t:
        mcq_prompt = f"How do you say 'I want to order food' in {lang}?"
        mcq_options = ["Quiero ordenar la comida.", "Voy a dormir ahora.", "Me gusta el carro."] if lang == "Spanish" else [
            "Je voudrais commander.", "Je vais dormir.", "J'aime la voiture."
        ]
        mcq_answer = mcq_options[0]

        fib_prompt = "Complete the phrase: \"El plato del _____ (day)\"" if lang == "Spanish" else "Complete the phrase: \"Le plat du _____ (day)\""
        fib_answer = "día" if lang == "Spanish" else "jour"
        fib_hint = "Word for day"

        wo_prompt = "Arrange the sentence: 'The food is very delicious.'"
        wo_tokens = ["La", "comida", "está", "muy", "deliciosa", "ayer"] if lang == "Spanish" else ["La", "nourriture", "est", "très", "délicieuse", "hier"]
        wo_order = ["La", "comida", "está", "muy", "deliciosa"] if lang == "Spanish" else ["La", "nourriture", "est", "très", "délicieuse"]

        matching_pairs = [
            {"left": "Bread", "right": "El pan" if lang == "Spanish" else "Le pain"},
            {"left": "Delicious", "right": "Delicioso" if lang == "Spanish" else "Délicieux"},
            {"left": "Table", "right": "La mesa" if lang == "Spanish" else "La table"},
            {"left": "Glass", "right": "El vaso" if lang == "Spanish" else "Le verre"},
        ]
    elif "travel" in t or "direction" in t:
        mcq_prompt = f"How do you ask 'Where is the train station?' in {lang}?"
        mcq_options = ["¿Dónde está la estación de tren?", "¿Cuándo comemos hoy?", "¿Cómo te llamas?"] if lang == "Spanish" else [
            "Où est la gare?", "Quand mangeons-nous?", "Comment vous appelez-vous?"
        ]
        mcq_answer = mcq_options[0]

        fib_prompt = "Complete the phrase: \"Gire a la _____ (right)\"" if lang == "Spanish" else "Complete the phrase: \"Tournez à _____ (right)\""
        fib_answer = "derecha" if lang == "Spanish" else "droite"
        fib_hint = "Direction opposite of left"

        wo_prompt = "Arrange the sentence: 'A ticket to Madrid, please.'"
        wo_tokens = ["Un", "billete", "para", "Madrid", "por", "favor"] if lang == "Spanish" else ["Un", "billet", "pour", "Paris", "s'il", "vous", "plaît"]
        wo_order = ["Un", "billete", "para", "Madrid", "por", "favor"] if lang == "Spanish" else ["Un", "billet", "pour", "Paris", "s'il", "vous", "plaît"]

        matching_pairs = [
            {"left": "Airport", "right": "El aeropuerto" if lang == "Spanish" else "L'aéroport"},
            {"left": "Train", "right": "El tren" if lang == "Spanish" else "Le train"},
            {"left": "Ticket", "right": "El billete" if lang == "Spanish" else "Le billet"},
            {"left": "Hotel", "right": "El hotel" if lang == "Spanish" else "L'hôtel"},
        ]
    else:
        # Everyday Life / General
        mcq_prompt = f"How do you say 'Good morning, how are you?' in {lang}?"
        mcq_options = ["Buenos días, ¿cómo estás?", "Buenas noches, adiós.", "Hasta luego, gracias."] if lang == "Spanish" else [
            "Bonjour, comment allez-vous?", "Bonne nuit, au revoir.", "À bientôt, merci."
        ]
        mcq_answer = mcq_options[0]

        fib_prompt = "Complete the phrase: \"Mucho _____ (nice to meet you)\"" if lang == "Spanish" else "Complete the phrase: \"Enchanté de faire votre _____\""
        fib_answer = "gusto" if lang == "Spanish" else "connaissance"
        fib_hint = "Common polite greeting"

        wo_prompt = "Arrange the sentence: 'I speak a little Spanish.'" if lang == "Spanish" else "Arrange the sentence: 'I speak a little French.'"
        wo_tokens = ["Hablo", "un", "poco", "de", "español", "mucho"] if lang == "Spanish" else ["Je", "parle", "un", "peu", "français", "beaucoup"]
        wo_order = ["Hablo", "un", "poco", "de", "español"] if lang == "Spanish" else ["Je", "parle", "un", "peu", "français"]

        matching_pairs = [
            {"left": "Friend", "right": "El amigo" if lang == "Spanish" else "L'ami"},
            {"left": "House", "right": "La casa" if lang == "Spanish" else "La maison"},
            {"left": "Today", "right": "Hoy" if lang == "Spanish" else "Aujourd'hui"},
            {"left": "Thank you", "right": "Gracias" if lang == "Spanish" else "Merci"},
        ]

    return [
        {
            "type": "multiple_choice",
            "position": 1,
            "prompt": mcq_prompt,
            "payload": {
                "options": mcq_options,
                "correct_answer": mcq_answer,
            },
        },
        {
            "type": "fill_in_blank",
            "position": 2,
            "prompt": fib_prompt,
            "payload": {
                "hint": fib_hint,
                "correct_answer": fib_answer,
            },
        },
        {
            "type": "word_order",
            "position": 3,
            "prompt": wo_prompt,
            "payload": {
                "tokens": wo_tokens,
                "correct_order": wo_order,
            },
        },
        {
            "type": "matching",
            "position": 4,
            "prompt": f"Match {lang} vocabulary terms:",
            "payload": {
                "pairs": matching_pairs,
            },
        },
    ]


@router.post("", response_model=GenerationJobResponse, status_code=status.HTTP_201_CREATED)
async def create_generation_job(
    job_in: GenerationJobCreate,
    db: Client = Depends(get_supabase),
):
    payload = job_in.model_dump(mode="json")
    payload["status"] = "in_progress"
    payload["started_at"] = datetime.now(timezone.utc).isoformat()
    
    # 1. Create the job entry
    res = db.table("generation_jobs").insert(payload).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create generation job")
    job = res.data[0]
    job_id = job["id"]

    try:
        # 2. Create the generated quiz
        quiz_res = db.table("quizzes").insert({
            "title": f"{job_in.topic} Essentials",
            "topic": job_in.topic,
            "language": job_in.language,
            "level": job_in.level,
        }).execute()
        
        if quiz_res.data:
            new_quiz_id = quiz_res.data[0]["id"]
            
            # 3. Create the exercises
            exercises = _generate_exercises_for_topic(job_in.language, job_in.level, job_in.topic)
            for ex in exercises:
                ex["quiz_id"] = str(new_quiz_id)
                db.table("exercises").insert(ex).execute()
                
            # 4. Mark job completed
            completed_at = datetime.now(timezone.utc).isoformat()
            up_res = db.table("generation_jobs").update({
                "status": "completed",
                "quiz_id": str(new_quiz_id),
                "completed_at": completed_at,
            }).eq("id", str(job_id)).execute()
            
            if up_res.data:
                return up_res.data[0]
    except Exception as exc:
        db.table("generation_jobs").update({
            "status": "failed",
            "error": str(exc),
        }).eq("id", str(job_id)).execute()

    return job


@router.put("/{job_id}", response_model=GenerationJobResponse)
async def update_generation_job(
    job_id: UUID,
    job_in: GenerationJobUpdate,
    db: Client = Depends(get_supabase),
):
    payload = job_in.model_dump(exclude_unset=True, mode="json")
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")
    res = db.table("generation_jobs").update(payload).eq("id", str(job_id)).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation job not found or update failed")
    return res.data[0]


@router.delete("/{job_id}")
async def delete_generation_job(
    job_id: UUID,
    db: Client = Depends(get_supabase),
):
    res = db.table("generation_jobs").delete().eq("id", str(job_id)).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation job not found or delete failed")
    return {"message": "Generation job deleted successfully", "id": str(job_id)}
