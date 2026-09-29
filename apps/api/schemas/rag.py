from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

SourceType = Literal["url", "pdf", "txt", "md"]
DocumentStatus = Literal["processing", "ready", "failed"]


class UrlReferenceCreate(BaseModel):
    url: str = Field(..., description="The website / URL to fetch and ingest")
    title: str | None = Field(default=None, description="Optional custom title for the reference")
    chunk_size: int = Field(default=800, ge=100, le=4000, description="Target character count per chunk")
    chunk_overlap: int = Field(default=150, ge=0, le=1000, description="Character overlap between consecutive chunks")


class DocumentChunkResponse(BaseModel):
    id: UUID
    document_id: UUID
    chunk_index: int
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReferenceDocumentResponse(BaseModel):
    id: UUID
    user_id: UUID
    source_type: SourceType
    title: str
    source_url: str | None = None
    file_name: str | None = None
    content_type: str | None = None
    char_count: int = 0
    chunk_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    status: DocumentStatus = "ready"
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
    chunks: list[DocumentChunkResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ReferenceDocumentSummaryResponse(BaseModel):
    id: UUID
    user_id: UUID
    source_type: SourceType
    title: str
    source_url: str | None = None
    file_name: str | None = None
    content_type: str | None = None
    char_count: int = 0
    chunk_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    status: DocumentStatus = "ready"
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RAGSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language search query")
    top_k: int = Field(default=4, ge=1, le=50, description="Number of most similar chunks to return")
    match_threshold: float = Field(default=0.0, ge=-1.0, le=1.0, description="Minimum cosine similarity threshold")
    document_id: UUID | None = Field(default=None, description="Optional document filter")


class ChunkSearchResult(BaseModel):
    id: UUID
    document_id: UUID
    document_title: str
    source_type: SourceType
    source_url: str | None = None
    file_name: str | None = None
    chunk_index: int
    content: str
    similarity: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class RAGSearchResponse(BaseModel):
    query: str
    results: list[ChunkSearchResult]
    total_matches: int
