import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from apps.api.services.generation import QuizGenerationService
from apps.api.services.japanese_vocab import (
    JapaneseVocabEntry,
    JapaneseVocabService,
    japanese_vocab_service,
)


@pytest.fixture
def auth_headers(client):
    reg_payload = {"email": "jp_user@example.com", "username": "jpuser", "password": "Password123!"}
    res = client.post("/auth/register", json=reg_payload)
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_jisho_api_parsing():
    async def _run():
        service = JapaneseVocabService()
        mock_jisho_json = {
            "data": [
                {
                    "slug": "猫",
                    "is_common": True,
                    "jlpt": ["jlpt-n5"],
                    "japanese": [{"word": "猫", "reading": "ねこ"}],
                    "senses": [
                        {
                            "english_definitions": ["cat", "feline"],
                            "parts_of_speech": ["Noun"],
                        }
                    ],
                }
            ]
        }

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_jisho_json

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp

            data = await service.fetch_jisho("猫")
            assert data is not None
            assert data["kanji"] == "猫"
            assert data["reading"] == "ねこ"
            assert "cat" in data["meanings"]
            assert data["jlpt_level"] == "N5"
            assert data["is_common"] is True

    asyncio.run(_run())


def test_wiktionary_api_parsing():
    async def _run():
        service = JapaneseVocabService()
        mock_wiktionary_html = """
        <!DOCTYPE html>
        <html>
        <body>
            <section data-mw-section-id="0">
                <h2 id="Japanese">Japanese</h2>
                <section>
                    <h3>Kanji</h3>
                    <p>猫 (Jōyō kanji)</p>
                    <p>Kun: ねこ (neko)</p>
                    <p>On: びょう (byō)</p>
                    <h3>Noun</h3>
                    <ol>
                        <li>a cat (domestic feline)</li>
                        <li>
                            <span>吾輩は猫である ― Wagahai wa neko de aru ― I am a cat</span>
                        </li>
                    </ol>
                </section>
            </section>
            <section>
                <h2 id="Chinese">Chinese</h2>
                <p>Non-Japanese section</p>
            </section>
        </body>
        </html>
        """

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = mock_wiktionary_html

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp

            data = await service.fetch_wiktionary("猫")
            assert data is not None
            assert "吾輩は猫である" in data["examples"][0]
            assert "Kun: ねこ" in data["wiktionary_summary"]

    asyncio.run(_run())


def test_get_vocab_knowledge_combines_both():
    async def _run():
        service = JapaneseVocabService()
        mock_jisho = {
            "word": "食べる",
            "kanji": "食べる",
            "reading": "たべる",
            "meanings": ["to eat"],
            "parts_of_speech": ["Ichidan verb", "Transitive verb"],
            "jlpt_level": "N5",
            "is_common": True,
            "jisho_url": "https://jisho.org/search/食べる",
        }
        mock_wik = {
            "word": "食べる",
            "wiktionary_summary": "Verb: to eat (ichidan)\nConjugation: 食べます",
            "examples": ["ご飯を食べる ― gohan o taberu ― to eat a meal"],
            "wiktionary_url": "https://en.wiktionary.org/wiki/食べる#Japanese",
        }

        with patch.object(service, "fetch_jisho", return_value=mock_jisho), patch.object(
            service, "fetch_wiktionary", return_value=mock_wik
        ):
            entry = await service.get_vocab_knowledge("食べる")
            assert entry.kanji == "食べる"
            assert entry.reading == "たべる"
            assert "to eat" in entry.meanings
            assert entry.jlpt_level == "N5"
            assert len(entry.usage_examples) == 1
            assert "gohan o taberu" in entry.usage_examples[0]
            assert len(entry.source_urls) == 2

    asyncio.run(_run())


def test_format_knowledge_for_quiz_prompt():
    service = JapaneseVocabService()
    entry = JapaneseVocabEntry(
        word="駅",
        kanji="駅",
        reading="えき",
        meanings=["train station"],
        parts_of_speech=["Noun"],
        jlpt_level="N5",
        is_common=True,
        usage_examples=["駅に行く ― eki ni iku ― go to the station"],
        wiktionary_summary="Noun: station",
        source_urls=["https://jisho.org/search/駅"],
    )

    prompt_context = service.format_knowledge_for_quiz_prompt([entry])
    assert "Jisho.org & Wiktionary APIs" in prompt_context
    assert "Word: 駅 | Reading: えき (JLPT N5)" in prompt_context
    assert "train station" in prompt_context
    assert "eki ni iku" in prompt_context


def test_lookup_japanese_vocab_endpoint(client, auth_headers):
    mock_entry = JapaneseVocabEntry(
        word="猫",
        kanji="猫",
        reading="ねこ",
        meanings=["cat", "feline"],
        parts_of_speech=["Noun"],
        jlpt_level="N5",
        is_common=True,
        usage_examples=["吾輩は猫である"],
        wiktionary_summary="Kanji: 猫\nKun: ねこ",
        source_urls=["https://jisho.org/search/猫", "https://en.wiktionary.org/wiki/猫#Japanese"],
    )

    with patch.object(japanese_vocab_service, "get_vocab_knowledge", return_value=mock_entry):
        res = client.get("/references/japanese/vocab?word=猫", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["word"] == "猫"
        assert data["kanji"] == "猫"
        assert data["reading"] == "ねこ"
        assert "cat" in data["meanings"]
        assert data["jlpt_level"] == "N5"
        assert len(data["source_urls"]) == 2


def test_ingest_japanese_vocab_endpoint(client, auth_headers):
    mock_entry = JapaneseVocabEntry(
        word="コーヒー",
        kanji="珈琲",
        reading="コーヒー",
        meanings=["coffee"],
        parts_of_speech=["Noun"],
        jlpt_level="N5",
        is_common=True,
        usage_examples=["コーヒーを飲む ― to drink coffee"],
        wiktionary_summary="Loanword from Dutch koffie / Arabic qahwah",
        source_urls=["https://jisho.org/search/コーヒー"],
    )

    with patch.object(japanese_vocab_service, "get_vocab_knowledge", return_value=mock_entry):
        res = client.post(
            "/references/japanese/vocab",
            json={"word": "コーヒー"},
            headers=auth_headers,
        )
        assert res.status_code == 201
        data = res.json()
        assert "Japanese Vocab: 珈琲" in data["title"]
        assert data["chunk_count"] >= 1

        # Search should find the ingested Japanese reference
        search_res = client.post(
            "/references/search",
            json={"query": "coffee drink"},
            headers=auth_headers,
        )
        assert search_res.status_code == 200
        results = search_res.json()["results"]
        assert len(results) >= 1
        assert any("珈琲" in r["document_title"] for r in results)


def test_quiz_generation_injects_japanese_knowledge(mock_db):
    async def _run():
        service = QuizGenerationService(db=mock_db)

        mock_entry = JapaneseVocabEntry(
            word="水",
            kanji="水",
            reading="みず",
            meanings=["water"],
            parts_of_speech=["Noun"],
            jlpt_level="N5",
            is_common=True,
            usage_examples=["水をください ― water please"],
            source_urls=["https://jisho.org/search/水"],
        )

        with patch.object(
            japanese_vocab_service, "get_topic_knowledge", return_value=[mock_entry]
        ) as mock_get_topic, patch.object(
            service, "is_ai_available", return_value=True
        ), patch.object(
            service, "client"
        ) as mock_client:
            mock_response = AsyncMock()
            mock_response.text = '{"title": "Japanese Food Practice", "multiple_choice_exercises": [], "fill_in_blank_exercises": [], "word_order_exercises": [], "matching_exercises": []}'

            # Ensure model call receives prompt containing Wiktionary / Jisho context
            captured_prompt = None

            def fake_generate_content(*args, **kwargs):
                nonlocal captured_prompt
                captured_prompt = kwargs.get("contents") or (args[0] if args else "")
                return mock_response

            mock_client.models.generate_content.side_effect = fake_generate_content

            await service.generate_with_gemini(
                language="Japanese", level="A1", topic="Food & Dining", count=4
            )

            mock_get_topic.assert_called_once()
            assert captured_prompt is not None
            assert "Jisho.org & Wiktionary" in captured_prompt
            assert "Word: 水 | Reading: みず" in captured_prompt

    asyncio.run(_run())
