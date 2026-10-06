from typing import Any
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from apps.api.core.auth import get_current_user
from apps.api.core.db import get_supabase
from apps.api.schemas.rag import (
    JapaneseVocabImportRequest,
    JapaneseVocabLookupResponse,
    RAGSearchRequest,
    RAGSearchResponse,
    ReferenceDocumentResponse,
    ReferenceDocumentSummaryResponse,
    SourceType,
    UrlReferenceCreate,
)
from apps.api.services.content_extractor import (
    extract_clean_text_from_html,
    extract_text_from_document,
    fetch_web_page,
    validate_url,
)
from apps.api.services.japanese_vocab import japanese_vocab_service
from apps.api.services.rag_service import RAGService
from supabase import Client

router = APIRouter(
    prefix="/references",
    tags=["references"],
    dependencies=[Depends(get_current_user)],
)


def get_rag_service(db: Client = Depends(get_supabase)) -> RAGService:
    return RAGService(db=db)


@router.post(
    "/url",
    response_model=ReferenceDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a web page reference material by URL",
)
async def add_url_reference(
    payload: UrlReferenceCreate,
    current_user: dict[str, Any] = Depends(get_current_user),
    rag_service: RAGService = Depends(get_rag_service),
):
    """
    Validates URL, fetches the web page, cleans boilerplate/navigation HTML,
    extracts textual content, chunks text, generates embeddings, and saves
    to the user's private knowledge base.
    """
    user_id = UUID(str(current_user["id"]))

    # 1. Validate URL & Prevent SSRF
    validated_url = validate_url(payload.url)

    # 2. Fetch Page
    html_content, final_url, fetch_meta = await fetch_web_page(validated_url)

    # 3. Clean and Extract Meaningful Textual Content
    clean_text, extracted_title, doc_meta = extract_clean_text_from_html(
        html_content, fallback_url=final_url
    )

    title = payload.title.strip() if payload.title else extracted_title
    combined_meta = {**fetch_meta, **doc_meta}

    # 4. Ingest, Chunk, Generate Embeddings, and Store in Vector DB
    document = await rag_service.ingest_reference(
        user_id=user_id,
        source_type="url",
        title=title,
        content=clean_text,
        source_url=final_url,
        file_name=None,
        content_type=fetch_meta.get("content_type", "text/html"),
        metadata=combined_meta,
        chunk_size=payload.chunk_size,
        chunk_overlap=payload.chunk_overlap,
    )

    return document


@router.post(
    "/upload",
    response_model=ReferenceDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a reference document (pdf, txt, md)",
)
async def upload_document_reference(
    file: UploadFile = File(...),
    title: str | None = Form(None),
    chunk_size: int = Form(800),
    chunk_overlap: int = Form(150),
    current_user: dict[str, Any] = Depends(get_current_user),
    rag_service: RAGService = Depends(get_rag_service),
):
    """
    Uploads a reference document (.pdf, .txt, .md), extracts textual content,
    chunks text, generates embeddings, and saves to user's private knowledge base.
    """
    user_id = UUID(str(current_user["id"]))

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a filename.",
        )

    # 1. Read file bytes
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    # 2. Determine source type
    fname_lower = file.filename.lower()
    source_type: SourceType = "txt"
    if fname_lower.endswith(".pdf"):
        source_type = "pdf"
    elif fname_lower.endswith((".md", ".markdown")):
        source_type = "md"
    elif fname_lower.endswith(".txt"):
        source_type = "txt"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{file.filename}'. Allowed formats: .pdf, .txt, .md",
        )

    # 3. Extract text from document
    clean_text, extracted_title, doc_meta = extract_text_from_document(
        file_bytes=file_bytes,
        file_name=file.filename,
        content_type=file.content_type,
    )

    doc_title = title.strip() if title else extracted_title

    # 4. Ingest, Chunk, Generate Embeddings, and Store in Vector DB
    document = await rag_service.ingest_reference(
        user_id=user_id,
        source_type=source_type,
        title=doc_title,
        content=clean_text,
        source_url=None,
        file_name=file.filename,
        content_type=file.content_type or f"application/{source_type}",
        metadata=doc_meta,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    return document


@router.get(
    "",
    response_model=list[ReferenceDocumentSummaryResponse],
    summary="List all reference materials owned by the authenticated user",
)
async def list_references(
    source_type: SourceType | None = None,
    current_user: dict[str, Any] = Depends(get_current_user),
    rag_service: RAGService = Depends(get_rag_service),
):
    """Lists reference documents in the user's private knowledge base."""
    user_id = UUID(str(current_user["id"]))
    return await rag_service.list_user_references(user_id=user_id, source_type=source_type)


@router.get(
    "/{reference_id}",
    response_model=ReferenceDocumentResponse,
    summary="Get details and chunks of a specific reference document",
)
async def get_reference(
    reference_id: UUID,
    current_user: dict[str, Any] = Depends(get_current_user),
    rag_service: RAGService = Depends(get_rag_service),
):
    """Retrieves a single reference document with all its chunks."""
    user_id = UUID(str(current_user["id"]))
    return await rag_service.get_user_reference(user_id=user_id, document_id=reference_id)


@router.delete(
    "/{reference_id}",
    summary="Delete a reference document and all its chunks",
)
async def delete_reference(
    reference_id: UUID,
    current_user: dict[str, Any] = Depends(get_current_user),
    rag_service: RAGService = Depends(get_rag_service),
):
    """Deletes a reference material from the user's private knowledge base."""
    user_id = UUID(str(current_user["id"]))
    return await rag_service.delete_user_reference(user_id=user_id, document_id=reference_id)


@router.post(
    "/search",
    response_model=RAGSearchResponse,
    summary="Semantic vector search across the user's private knowledge base",
)
async def search_references(
    request: RAGSearchRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    rag_service: RAGService = Depends(get_rag_service),
):
    """
    Embeds the user's query and finds the most relevant knowledge chunks
    belonging exclusively to the authenticated user.
    """
    user_id = UUID(str(current_user["id"]))
    results = await rag_service.search_user_knowledge(
        user_id=user_id,
        query=request.query,
        top_k=request.top_k,
        match_threshold=request.match_threshold,
        document_id=request.document_id,
    )

    return RAGSearchResponse(
        query=request.query,
        results=results,
        total_matches=len(results),
    )


@router.get(
    "/japanese/vocab",
    response_model=JapaneseVocabLookupResponse,
    summary="Lookup Japanese vocabulary from Jisho and Wiktionary APIs",
)
async def lookup_japanese_vocab(
    word: str,
    _current_user: dict[str, Any] = Depends(get_current_user),
):
    """
    Queries Jisho.org and English Wiktionary APIs to fetch authoritative Kanji,
    Furigana readings, meanings, JLPT levels, and contextual sentences.
    """
    clean_word = word.strip()
    if not clean_word:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Word query parameter cannot be empty.",
        )

    entry = await japanese_vocab_service.get_vocab_knowledge(clean_word)
    return JapaneseVocabLookupResponse(
        word=entry.word,
        kanji=entry.kanji,
        reading=entry.reading,
        romaji=entry.romaji,
        meanings=entry.meanings,
        parts_of_speech=entry.parts_of_speech,
        jlpt_level=entry.jlpt_level,
        is_common=entry.is_common,
        usage_examples=entry.usage_examples,
        wiktionary_summary=entry.wiktionary_summary,
        source_urls=entry.source_urls,
    )


@router.post(
    "/japanese/vocab",
    response_model=ReferenceDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest Japanese vocabulary reference from Jisho and Wiktionary into private knowledge base",
)
async def ingest_japanese_vocab(
    payload: JapaneseVocabImportRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    rag_service: RAGService = Depends(get_rag_service),
):
    """
    Fetches vocabulary from Jisho.org and English Wiktionary APIs, constructs
    structured textual knowledge, chunks it, generates embeddings, and saves
    it to the user's private knowledge base.
    """
    user_id = UUID(str(current_user["id"]))
    clean_word = payload.word.strip()

    entry = await japanese_vocab_service.get_vocab_knowledge(clean_word)

    # Format authoritative reference content
    lines = [
        f"# Japanese Vocabulary: {entry.kanji} ({entry.reading})",
        f"- Target Word: {entry.kanji}",
        f"- Furigana Reading: {entry.reading}",
    ]
    if entry.jlpt_level:
        lines.append(f"- JLPT Level: {entry.jlpt_level}")
    if entry.parts_of_speech:
        lines.append(f"- Part of Speech: {', '.join(entry.parts_of_speech)}")
    if entry.meanings:
        lines.append(f"- English Meanings: {', '.join(entry.meanings)}")

    if entry.usage_examples:
        lines.append("\n## Example Usage Sentences:")
        for ex in entry.usage_examples:
            lines.append(f"- {ex}")

    if entry.wiktionary_summary:
        lines.append("\n## Wiktionary Etymology & Notes:")
        lines.append(entry.wiktionary_summary)

    content = "\n".join(lines)
    primary_url = entry.source_urls[0] if entry.source_urls else None

    metadata = {
        "word": entry.word,
        "kanji": entry.kanji,
        "reading": entry.reading,
        "jlpt_level": entry.jlpt_level,
        "source_urls": entry.source_urls,
        "source_apis": ["jisho.org", "en.wiktionary.org"],
    }

    doc = await rag_service.ingest_reference(
        user_id=user_id,
        source_type="url",
        title=f"Japanese Vocab: {entry.kanji} ({entry.reading})",
        content=content,
        source_url=primary_url,
        file_name=None,
        content_type="text/markdown",
        metadata=metadata,
        chunk_size=payload.chunk_size,
        chunk_overlap=payload.chunk_overlap,
    )

    return doc
