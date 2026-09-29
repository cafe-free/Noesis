import React, { useState } from 'react';
import { Search, Loader2, Sparkles, FileText, Globe, CornerDownRight } from 'lucide-react';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { ChunkSearchResult, searchReferences } from '../../api/references';

export const ReferenceSearchSection: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<ChunkSearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanQuery = query.trim();
    if (!cleanQuery) return;

    setIsSearching(true);
    setErrorMessage(null);
    try {
      const response = await searchReferences({
        query: cleanQuery,
        top_k: 4,
        match_threshold: 0.1,
      });
      setResults(response.results || []);
      setHasSearched(true);
    } catch (err: unknown) {
      setErrorMessage(
        err instanceof Error ? err.message : 'Search failed. Please try again.'
      );
    } finally {
      setIsSearching(false);
    }
  };

  const getSourceIcon = (type: string) => {
    switch (type) {
      case 'url':
        return <Globe className="w-4 h-4 text-blue-500" />;
      case 'pdf':
        return <FileText className="w-4 h-4 text-rose-500" />;
      default:
        return <FileText className="w-4 h-4 text-emerald-500" />;
    }
  };

  const getSectionOrPageInfo = (result: ChunkSearchResult) => {
    const meta = result.metadata || {};
    if (meta.page_number) return `Page ${meta.page_number}`;
    if (meta.page_count) return `Page 1 of ${meta.page_count}`;
    if (meta.section_title) return `Section: ${meta.section_title}`;
    const similarityPercent = Math.round(result.similarity * 100);
    return `Chunk #${result.chunk_index + 1} · ${similarityPercent}% Match`;
  };

  return (
    <Card className="p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl shadow-sm">
      <div className="flex items-center gap-2.5 mb-4">
        <div className="w-8 h-8 rounded-xl bg-teal-50 dark:bg-teal-950/40 text-teal-600 dark:text-teal-400 flex items-center justify-center">
          <Sparkles className="w-4 h-4" />
        </div>
        <div>
          <h2 className="text-base font-bold text-slate-900 dark:text-white font-display">
            Search your references
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Verify semantic RAG retrieval across your private knowledge base
          </p>
        </div>
      </div>

      <form onSubmit={handleSearch} className="flex flex-col sm:flex-row items-center gap-2.5">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="What are Spanish reflexive verbs?"
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-800 dark:text-slate-100 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-teal-500 transition-all placeholder:text-slate-400"
          />
        </div>
        <Button
          type="submit"
          variant="primary"
          size="md"
          isLoading={isSearching}
          disabled={!query.trim()}
          className="w-full sm:w-auto"
        >
          Search
        </Button>
      </form>

      {errorMessage && (
        <p className="text-xs font-semibold text-rose-600 dark:text-rose-400 mt-3">
          {errorMessage}
        </p>
      )}

      {/* Results List */}
      {hasSearched && (
        <div className="mt-6 pt-5 border-t border-slate-100 dark:border-slate-800/80">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Search Results ({results.length})
            </span>
          </div>

          {results.length === 0 ? (
            <div className="py-6 text-center text-slate-500 dark:text-slate-400 text-xs">
              No matching reference content found. Try different search terms or add more references below.
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              {results.map((item, idx) => (
                <div
                  key={`${item.id}-${idx}`}
                  className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/60 transition-colors"
                >
                  <div className="flex items-center justify-between gap-2 mb-1.5">
                    <div className="flex items-center gap-2 min-w-0">
                      {getSourceIcon(item.source_type)}
                      <span className="text-sm font-bold text-slate-900 dark:text-white truncate">
                        {item.document_title}
                      </span>
                    </div>
                    <span className="text-xs font-semibold text-teal-600 dark:text-teal-400 shrink-0">
                      {getSectionOrPageInfo(item)}
                    </span>
                  </div>

                  <div className="flex items-start gap-2 mt-2">
                    <CornerDownRight className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
                    <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed italic">
                      "{item.content}"
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </Card>
  );
};
