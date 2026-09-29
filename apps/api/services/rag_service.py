import logging
import uuid
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from apps.api.core.db import get_supabase
from apps.api.schemas.rag import (
    ChunkSearchResult,
    DocumentChunkResponse,
    ReferenceDocumentResponse,
    ReferenceDocumentSummaryResponse,
    SourceType,
)
from apps.api.services.chunker import chunk_text
from apps.api.services.embedding import EmbeddingService, cosine_similarity

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self, db: Client | None = None, embedding_service: EmbeddingService | None = None):
        self.db = db or get_supabase()
        self.embedding_service = embedding_service or EmbeddingService()

    async def ingest_reference(
        self,
        user_id: UUID,
        source_type: SourceType,
        title: str,
        content: str,
        source_url: str | None = None,
        file_name: str | None = None,
        content_type: str | None = None,
        metadata: dict[str, Any] | None = None,
        chunk_size: int = 800,
        chunk_overlap: int = 150,
    ) -> ReferenceDocumentResponse:
        """
        Ingests a reference document: records metadata, chunks text,
        generates embeddings, and stores chunks in the vector database.
        """
        now_str = datetime.now(UTC).isoformat()
        meta = metadata or {}
        doc_id = str(uuid.uuid4())

        # 1. Chunk the content
        chunks = chunk_text(content, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Document content is empty or could not be chunked.",
            )

        # 2. Insert Reference Document Record
        doc_payload = {
            "id": doc_id,
            "user_id": str(user_id),
            "source_type": source_type,
            "title": title[:255] if title else "Untitled Reference",
            "source_url": source_url,
            "file_name": file_name,
            "content_type": content_type,
            "char_count": len(content),
            "chunk_count": len(chunks),
            "metadata": meta,
            "status": "ready",
            "error_message": None,
            "created_at": now_str,
            "updated_at": now_str,
        }

        res = self.db.table("reference_documents").insert(doc_payload).execute()
        if not res.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save reference document to database.",
            )
        created_doc = res.data[0]

        # 3. Generate embeddings in batch
        chunk_texts = [c.content for c in chunks]
        embeddings = await self.embedding_service.get_embeddings(chunk_texts)

        # 4. Insert Document Chunks
        chunk_records = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_records.append(
                {
                    "id": str(uuid.uuid4()),
                    "document_id": doc_id,
                    "user_id": str(user_id),
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "embedding": embedding,
                    "metadata": {
                        **chunk.metadata,
                        "start_char": chunk.start_char,
                        "end_char": chunk.end_char,
                        "token_count": chunk.token_count,
                    },
                    "created_at": now_str,
                }
            )

        chunk_res = self.db.table("document_chunks").insert(chunk_records).execute()
        stored_chunks = chunk_res.data or chunk_records

        chunk_responses = [
            DocumentChunkResponse(
                id=c["id"],
                document_id=c["document_id"],
                chunk_index=c["chunk_index"],
                content=c["content"],
                metadata=c.get("metadata", {}),
                created_at=c.get("created_at") or now_str,
            )
            for c in stored_chunks
        ]

        return ReferenceDocumentResponse(
            id=created_doc["id"],
            user_id=created_doc["user_id"],
            source_type=created_doc["source_type"],
            title=created_doc["title"],
            source_url=created_doc.get("source_url"),
            file_name=created_doc.get("file_name"),
            content_type=created_doc.get("content_type"),
            char_count=created_doc["char_count"],
            chunk_count=created_doc["chunk_count"],
            metadata=created_doc.get("metadata", {}),
            status=created_doc.get("status", "ready"),
            error_message=created_doc.get("error_message"),
            created_at=created_doc["created_at"],
            updated_at=created_doc["updated_at"],
            chunks=chunk_responses,
        )

    async def list_user_references(
        self,
        user_id: UUID,
        source_type: SourceType | None = None,
    ) -> list[ReferenceDocumentSummaryResponse]:
        """Lists all reference documents owned by the authenticated user."""
        query = self.db.table("reference_documents").select("*").eq("user_id", str(user_id))
        if source_type:
            query = query.eq("source_type", source_type)
        query = query.order("created_at", desc=True)
        res = query.execute()

        return [ReferenceDocumentSummaryResponse(**item) for item in (res.data or [])]

    async def get_user_reference(
        self,
        user_id: UUID,
        document_id: UUID,
    ) -> ReferenceDocumentResponse:
        """Retrieves a single reference document with its chunks, enforcing user ownership."""
        doc_res = (
            self.db.table("reference_documents")
            .select("*")
            .eq("id", str(document_id))
            .eq("user_id", str(user_id))
            .execute()
        )
        if not doc_res.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reference document not found or access denied.",
            )

        doc = doc_res.data[0]

        chunks_res = (
            self.db.table("document_chunks")
            .select("id, document_id, chunk_index, content, metadata, created_at")
            .eq("document_id", str(document_id))
            .eq("user_id", str(user_id))
            .order("chunk_index")
            .execute()
        )
        chunks = [DocumentChunkResponse(**c) for c in (chunks_res.data or [])]

        return ReferenceDocumentResponse(
            id=doc["id"],
            user_id=doc["user_id"],
            source_type=doc["source_type"],
            title=doc["title"],
            source_url=doc.get("source_url"),
            file_name=doc.get("file_name"),
            content_type=doc.get("content_type"),
            char_count=doc["char_count"],
            chunk_count=doc["chunk_count"],
            metadata=doc.get("metadata", {}),
            status=doc.get("status", "ready"),
            error_message=doc.get("error_message"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
            chunks=chunks,
        )

    async def delete_user_reference(
        self,
        user_id: UUID,
        document_id: UUID,
    ) -> dict[str, Any]:
        """Deletes a reference document and all associated chunks for the user."""
        # Check ownership first
        doc_res = (
            self.db.table("reference_documents")
            .select("id")
            .eq("id", str(document_id))
            .eq("user_id", str(user_id))
            .execute()
        )
        if not doc_res.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reference document not found or access denied.",
            )

        # Delete chunks first (in case foreign key cascade is not enabled in mock)
        self.db.table("document_chunks").delete().eq("document_id", str(document_id)).execute()
        # Delete document
        self.db.table("reference_documents").delete().eq("id", str(document_id)).execute()

        return {"message": "Reference document deleted successfully", "id": str(document_id)}

    async def search_user_knowledge(
        self,
        user_id: UUID,
        query: str,
        top_k: int = 4,
        match_threshold: float = 0.0,
        document_id: UUID | None = None,
    ) -> list[ChunkSearchResult]:
        """
        Semantically searches the user's private knowledge base using vector similarity.
        """
        clean_query = query.strip()
        if not clean_query:
            return []

        # 1. Generate query embedding
        query_embedding = await self.embedding_service.get_embedding(clean_query)

        # 2. Fetch candidate chunks for this user (privacy enforced by user_id filter)
        chunk_query = (
            self.db.table("document_chunks")
            .select("*")
            .eq("user_id", str(user_id))
        )
        if document_id:
            chunk_query = chunk_query.eq("document_id", str(document_id))

        res = chunk_query.execute()
        raw_chunks = res.data or []
        if not raw_chunks:
            return []

        # 3. Fetch reference document info map to enrich search results
        doc_ids = list({str(c["document_id"]) for c in raw_chunks if c.get("document_id")})
        doc_map = {}
        if doc_ids:
            doc_res = (
                self.db.table("reference_documents")
                .select("id, title, source_type, source_url, file_name")
                .in_("id", doc_ids)
                .execute()
            )
            for d in doc_res.data or []:
                doc_map[str(d["id"])] = d

        # 4. Calculate cosine similarity
        scored_results: list[tuple[float, dict[str, Any]]] = []
        for c in raw_chunks:
            chunk_emb = c.get("embedding")
            if isinstance(chunk_emb, list) and chunk_emb:
                sim = cosine_similarity(query_embedding, chunk_emb)
                if sim >= match_threshold:
                    scored_results.append((sim, c))

        # 5. Sort by similarity descending
        scored_results.sort(key=lambda x: x[0], reverse=True)
        top_results = scored_results[:top_k]

        output: list[ChunkSearchResult] = []
        for sim, c in top_results:
            doc = doc_map.get(str(c["document_id"]), {})
            output.append(
                ChunkSearchResult(
                    id=c["id"],
                    document_id=c["document_id"],
                    document_title=doc.get("title", "Reference"),
                    source_type=doc.get("source_type", "txt"),
                    source_url=doc.get("source_url"),
                    file_name=doc.get("file_name"),
                    chunk_index=c["chunk_index"],
                    content=c["content"],
                    similarity=round(sim, 4),
                    metadata=c.get("metadata", {}),
                )
            )

        return output
