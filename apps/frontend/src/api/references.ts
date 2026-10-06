import { apiClient, getAccessToken } from './client';

export interface ReferenceDocument {
  id: string;
  user_id: string;
  source_type: 'url' | 'pdf' | 'txt' | 'md';
  title: string;
  source_url?: string;
  file_name?: string;
  content_type?: string;
  char_count: number;
  chunk_count: number;
  metadata: Record<string, any>;
  status: 'processing' | 'ready' | 'failed';
  error_message?: string;
  created_at: string;
  updated_at: string;
  chunks?: DocumentChunk[];
}

export interface DocumentChunk {
  id: string;
  document_id: string;
  chunk_index: number;
  content: string;
  metadata: Record<string, any>;
  created_at: string;
}

export interface ChunkSearchResult {
  id: string;
  document_id: string;
  document_title: string;
  source_type: 'url' | 'pdf' | 'txt' | 'md';
  source_url?: string;
  file_name?: string;
  chunk_index: number;
  content: string;
  similarity: number;
  metadata: Record<string, any>;
}

export interface RAGSearchResponse {
  query: string;
  results: ChunkSearchResult[];
  total_matches: number;
}

export async function addUrlReference(payload: {
  url: string;
  title?: string;
  chunk_size?: number;
  chunk_overlap?: number;
}): Promise<ReferenceDocument> {
  return apiClient.post<ReferenceDocument>('/references/url', payload);
}

export async function uploadDocumentReference(
  file: File,
  title?: string,
  chunk_size?: number,
  chunk_overlap?: number
): Promise<ReferenceDocument> {
  const formData = new FormData();
  formData.append('file', file);
  if (title) formData.append('title', title);
  if (chunk_size) formData.append('chunk_size', String(chunk_size));
  if (chunk_overlap) formData.append('chunk_overlap', String(chunk_overlap));

  const baseUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '');
  const token = getAccessToken();
  const headers: Record<string, string> = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${baseUrl}/references/upload`, {
    method: 'POST',
    headers,
    body: formData,
  });

  if (!response.ok) {
    let errorDetail = `HTTP ${response.status} ${response.statusText}`;
    try {
      const err = await response.json();
      if (err?.detail) errorDetail = typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail);
    } catch {
      // Ignore json parse error
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export async function listReferences(source_type?: string): Promise<ReferenceDocument[]> {
  return apiClient.get<ReferenceDocument[]>('/references', {
    params: source_type ? { source_type } : undefined,
  });
}

export async function getReference(id: string): Promise<ReferenceDocument> {
  return apiClient.get<ReferenceDocument>(`/references/${id}`);
}

export async function deleteReference(id: string): Promise<{ message: string; id: string }> {
  return apiClient.delete<{ message: string; id: string }>(`/references/${id}`);
}

export async function searchReferences(payload: {
  query: string;
  top_k?: number;
  match_threshold?: number;
  document_id?: string;
}): Promise<RAGSearchResponse> {
  return apiClient.post<RAGSearchResponse>('/references/search', payload);
}

export interface JapaneseVocabKnowledge {
  word: string;
  kanji: string;
  reading: string;
  romaji?: string;
  meanings: string[];
  parts_of_speech: string[];
  jlpt_level?: string;
  is_common: boolean;
  usage_examples: string[];
  wiktionary_summary: string;
  source_urls: string[];
}

export async function lookupJapaneseVocab(word: string): Promise<JapaneseVocabKnowledge> {
  return apiClient.get<JapaneseVocabKnowledge>('/references/japanese/vocab', {
    params: { word },
  });
}

export async function importJapaneseVocab(word: string): Promise<ReferenceDocument> {
  return apiClient.post<ReferenceDocument>('/references/japanese/vocab', { word });
}
