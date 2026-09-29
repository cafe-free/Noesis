import io
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from pypdf import PdfWriter

from apps.api.services.chunker import chunk_text
from apps.api.services.content_extractor import (
    extract_clean_text_from_html,
    extract_text_from_document,
    validate_url,
)
from apps.api.services.embedding import (
    cosine_similarity,
    generate_fallback_embedding,
)


def create_sample_pdf(text_pages: list[str]) -> bytes:
    """Helper to generate a minimal valid PDF in memory using pypdf."""
    from pypdf import PageObject
    from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

    # Create PDF writer
    writer = PdfWriter()
    for text in text_pages:
        # Create a page and inject text content stream
        page = PageObject.create_blank_page(width=612, height=792)
        # Format a simple PDF content stream with text: BT /F1 12 Tf 50 700 Td (text) Tj ET
        safe_text = text.replace("(", "\\(").replace(")", "\\)")
        stream_data = f"BT /F1 12 Tf 50 700 Td ({safe_text}) Tj ET".encode("latin-1")
        stream_obj = DecodedStreamObject()
        stream_obj.set_data(stream_data)

        font_dict = DictionaryObject(
            {
                NameObject("/Type"): NameObject("/Font"),
                NameObject("/Subtype"): NameObject("/Type1"),
                NameObject("/BaseFont"): NameObject("/Helvetica"),
            }
        )
        res_dict = DictionaryObject(
            {NameObject("/Font"): DictionaryObject({NameObject("/F1"): font_dict})}
        )
        page[NameObject("/Resources")] = res_dict
        page[NameObject("/Contents")] = stream_obj

        writer.add_page(page)

    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


# -------------------------------------------------------------
# 1. URL Validation Tests
# -------------------------------------------------------------


def test_url_validation_valid():
    assert validate_url("https://en.wikipedia.org/wiki/Spanish_grammar") == "https://en.wikipedia.org/wiki/Spanish_grammar"
    assert validate_url("http://example.com/notes?topic=verbs") == "http://example.com/notes?topic=verbs"


def test_url_validation_invalid_scheme():
    with pytest.raises(HTTPException) as exc_info:
        validate_url("ftp://example.com/file.txt")
    assert exc_info.value.status_code == 400
    assert "Invalid URL scheme" in exc_info.value.detail


def test_url_validation_ssrf_blocked():
    # Localhost
    with pytest.raises(HTTPException) as exc1:
        validate_url("http://localhost:8000/internal")
    assert exc1.value.status_code == 400
    assert "forbidden" in exc1.value.detail.lower()

    # Loopback IP
    with pytest.raises(HTTPException) as exc2:
        validate_url("http://127.0.0.1:8080/secret")
    assert exc2.value.status_code == 400

    # Private IP range
    with pytest.raises(HTTPException) as exc3:
        validate_url("http://192.168.1.1/admin")
    assert exc3.value.status_code == 400

    with pytest.raises(HTTPException) as exc4:
        validate_url("http://10.0.0.5/api")
    assert exc4.value.status_code == 400


# -------------------------------------------------------------
# 2. HTML Cleaning & Text Extraction Tests
# -------------------------------------------------------------


def test_html_cleaning_removes_boilerplate():
    raw_html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <title>Spanish Subjunctive Guide</title>
        <meta name="description" content="A complete guide to Spanish subjunctive mood.">
        <meta name="author" content="Professor Martinez">
        <style>body { font-family: sans-serif; }</style>
        <script>console.log("tracking code");</script>
    </head>
    <body>
        <header>
            <nav class="navbar-main">
                <a href="/home">Home</a>
                <a href="/lessons">Lessons</a>
            </nav>
        </header>

        <div class="cookie-banner-container">
            <p>Please accept our cookies to continue.</p>
            <button>Accept All</button>
        </div>

        <main>
            <h1>Understanding the Subjunctive in Spanish</h1>
            <p>The subjunctive mood expresses wishes, doubt, uncertainty, and hypothetical situations.</p>
            <p>For regular -ar verbs, take the yo form of the present indicative, drop the -o, and add opposite endings (-e, -es, -e, -emos, -en).</p>
            <ul>
                <li>Hablar becomes: hable, hables, hable, hablemos, hablen.</li>
                <li>Comer becomes: coma, comas, coma, comamos, coman.</li>
            </ul>
        </main>

        <aside class="sidebar-ads">
            <div class="ad-container">Buy cheap flights now!</div>
        </aside>

        <footer>
            <p>Copyright 2026 Language Academy. All rights reserved.</p>
        </footer>
    </body>
    </html>
    """

    cleaned_text, title, meta = extract_clean_text_from_html(raw_html, fallback_url="https://lingo.test/subjunctive")

    assert title == "Spanish Subjunctive Guide"
    assert meta["description"] == "A complete guide to Spanish subjunctive mood."
    assert meta["author"] == "Professor Martinez"
    assert meta["language"] == "es"

    # Confirm primary educational content is preserved
    assert "Understanding the Subjunctive in Spanish" in cleaned_text
    assert "The subjunctive mood expresses wishes" in cleaned_text
    assert "Hablar becomes: hable, hables" in cleaned_text

    # Confirm boilerplate elements are stripped
    assert "cookie" not in cleaned_text.lower()
    assert "buy cheap flights" not in cleaned_text.lower()
    assert "copyright 2026" not in cleaned_text.lower()
    assert "console.log" not in cleaned_text
    assert "<nav>" not in cleaned_text
    assert "<main>" not in cleaned_text


def test_html_cleaning_rejects_empty():
    empty_html = "<html><body><nav><p>Nav</p></nav></body></html>"
    with pytest.raises(HTTPException) as exc_info:
        extract_clean_text_from_html(empty_html)
    assert exc_info.value.status_code == 422


# -------------------------------------------------------------
# 3. Document (PDF, TXT, MD) Text Extraction Tests
# -------------------------------------------------------------


def test_document_extraction_txt():
    content = "French Greetings:\nBonjour means Hello.\nBonsoir means Good evening.\nAu revoir means Goodbye."
    clean_text, title, _meta = extract_text_from_document(content.encode("utf-8"), file_name="french_greetings.txt")
    assert title == "french_greetings.txt"
    assert "Bonjour means Hello." in clean_text


def test_document_extraction_markdown():
    content = "# Italian Past Tense (Passato Prossimo)\n\nFormed with auxiliary avere or essere plus past participle."
    clean_text, title, _meta = extract_text_from_document(content.encode("utf-8"), file_name="italian_verbs.md")
    assert title == "Italian Past Tense (Passato Prossimo)"
    assert "Formed with auxiliary avere or essere" in clean_text


def test_document_extraction_pdf():
    pdf_bytes = create_sample_pdf(["German Prepositions: mit, nach, von, zu take the dative case."])
    clean_text, _title, meta = extract_text_from_document(pdf_bytes, file_name="german_grammar.pdf")
    assert "German Prepositions" in clean_text
    assert meta.get("page_count") == 1


def test_document_extraction_invalid_format():
    with pytest.raises(HTTPException) as exc_info:
        extract_text_from_document(b"fake binary content", file_name="virus.exe")
    assert exc_info.value.status_code == 400
    assert "Allowed document formats: .pdf, .txt, .md" in exc_info.value.detail


# -------------------------------------------------------------
# 4. Chunking Tests
# -------------------------------------------------------------


def test_chunk_text_small():
    text = "Short text under chunk size."
    chunks = chunk_text(text, chunk_size=800, chunk_overlap=150)
    assert len(chunks) == 1
    assert chunks[0].content == text
    assert chunks[0].chunk_index == 0


def test_chunk_text_splits_and_overlaps():
    paragraphs = [
        f"Paragraph {i}: " + ("This is detailed knowledge about foreign vocabulary and sentence order. " * 4)
        for i in range(15)
    ]
    long_text = "\n\n".join(paragraphs)

    chunks = chunk_text(long_text, chunk_size=600, chunk_overlap=100)
    assert len(chunks) > 1

    for i, c in enumerate(chunks):
        assert c.chunk_index == i
        assert len(c.content) > 0
        assert c.start_char >= 0
        assert c.end_char > c.start_char


# -------------------------------------------------------------
# 5. Embedding & Cosine Similarity Tests
# -------------------------------------------------------------


def test_embedding_and_cosine_similarity():
    # Fallback embedding
    emb1 = generate_fallback_embedding("Spanish irregular subjunctive verbs")
    emb2 = generate_fallback_embedding("Spanish irregular subjunctive verbs")
    emb3 = generate_fallback_embedding("Quantum physics mechanics theory")

    assert len(emb1) == 768
    # Identical texts must have similarity ~ 1.0
    sim_same = cosine_similarity(emb1, emb2)
    assert pytest.approx(sim_same, abs=1e-3) == 1.0

    # Unrelated texts must have much lower similarity
    sim_diff = cosine_similarity(emb1, emb3)
    assert sim_diff < 0.6


# -------------------------------------------------------------
# 6. RAG API Routes & User Isolation Tests
# -------------------------------------------------------------


@pytest.fixture
def auth_headers_user1(client):
    reg_payload = {"email": "user1@example.com", "username": "user1", "password": "Password123!"}
    res = client.post("/auth/register", json=reg_payload)
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_user2(client):
    reg_payload = {"email": "user2@example.com", "username": "user2", "password": "Password123!"}
    res = client.post("/auth/register", json=reg_payload)
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_upload_txt_reference(client, auth_headers_user1):
    file_content = b"Japanese Particles Guide:\nWa marks the topic, Ga marks the grammatical subject."
    files = {"file": ("particles.txt", file_content, "text/plain")}
    data = {"title": "Japanese Particles"}

    res = client.post("/references/upload", files=files, data=data, headers=auth_headers_user1)
    assert res.status_code == 201
    json_data = res.json()
    assert json_data["title"] == "Japanese Particles"
    assert json_data["source_type"] == "txt"
    assert json_data["chunk_count"] >= 1
    assert len(json_data["chunks"]) >= 1
    assert "Wa marks the topic" in json_data["chunks"][0]["content"]


def test_upload_pdf_reference(client, auth_headers_user1):
    pdf_bytes = create_sample_pdf(["German Cases: Nominative, Accusative, Dative, Genitive."])
    files = {"file": ("german_cases.pdf", pdf_bytes, "application/pdf")}

    res = client.post("/references/upload", files=files, headers=auth_headers_user1)
    assert res.status_code == 201
    json_data = res.json()
    assert json_data["source_type"] == "pdf"
    assert json_data["file_name"] == "german_cases.pdf"


@patch("apps.api.routes.references.fetch_web_page")
def test_add_url_reference(mock_fetch, client, auth_headers_user1):
    mock_html = """
    <html>
        <head><title>French Verbs Reference</title></head>
        <body>
            <main>
                <h1>Être and Avoir Conjugations</h1>
                <p>Être is used for state of being, avoir is used for possession.</p>
            </main>
        </body>
    </html>
    """
    mock_fetch.return_value = (
        mock_html,
        "https://example.com/french-verbs",
        {"content_type": "text/html", "status_code": 200},
    )

    payload = {
        "url": "https://example.com/french-verbs",
        "title": "French Auxiliary Verbs",
        "chunk_size": 600,
        "chunk_overlap": 100,
    }

    res = client.post("/references/url", json=payload, headers=auth_headers_user1)
    assert res.status_code == 201
    json_data = res.json()
    assert json_data["title"] == "French Auxiliary Verbs"
    assert json_data["source_type"] == "url"
    assert json_data["source_url"] == "https://example.com/french-verbs"
    assert len(json_data["chunks"]) >= 1
    assert "Être is used for state of being" in json_data["chunks"][0]["content"]


def test_user_privacy_isolation(client, auth_headers_user1, auth_headers_user2):
    # User 1 uploads Reference 1
    res1 = client.post(
        "/references/upload",
        files={"file": ("spanish_notes.txt", b"Spanish notes: Por vs Para distinctions in depth.", "text/plain")},
        data={"title": "Por vs Para"},
        headers=auth_headers_user1,
    )
    assert res1.status_code == 201
    doc1_id = res1.json()["id"]

    # User 2 uploads Reference 2
    res2 = client.post(
        "/references/upload",
        files={"file": ("japanese_notes.txt", b"Japanese notes: Desu and Da politeness levels.", "text/plain")},
        data={"title": "Politeness in Japanese"},
        headers=auth_headers_user2,
    )
    assert res2.status_code == 201
    doc2_id = res2.json()["id"]

    # 1. User 1 lists references -> only doc1
    list1 = client.get("/references", headers=auth_headers_user1).json()
    doc_ids_user1 = [d["id"] for d in list1]
    assert doc1_id in doc_ids_user1
    assert doc2_id not in doc_ids_user1

    # 2. User 2 lists references -> only doc2
    list2 = client.get("/references", headers=auth_headers_user2).json()
    doc_ids_user2 = [d["id"] for d in list2]
    assert doc2_id in doc_ids_user2
    assert doc1_id not in doc_ids_user2

    # 3. User 1 cannot access User 2's document
    get_res = client.get(f"/references/{doc2_id}", headers=auth_headers_user1)
    assert get_res.status_code == 404

    # 4. User 1 cannot delete User 2's document
    del_res = client.delete(f"/references/{doc2_id}", headers=auth_headers_user1)
    assert del_res.status_code == 404

    # 5. Semantic Search isolation: User 1 searching returns only User 1's chunks
    search_res1 = client.post(
        "/references/search",
        json={"query": "politeness and particles in Japanese"},
        headers=auth_headers_user1,
    )
    assert search_res1.status_code == 200
    # Even though query matches Japanese, User 1 has no Japanese documents!
    for r in search_res1.json()["results"]:
        assert r["document_id"] != doc2_id

    # User 2 searching returns User 2's document
    search_res2 = client.post(
        "/references/search",
        json={"query": "politeness in Japanese"},
        headers=auth_headers_user2,
    )
    assert search_res2.status_code == 200
    matched_doc_ids = [r["document_id"] for r in search_res2.json()["results"]]
    assert doc2_id in matched_doc_ids
    assert doc1_id not in matched_doc_ids
