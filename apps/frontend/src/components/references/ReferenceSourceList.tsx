import React, { useState } from 'react';
import {
  FileText,
  Globe,
  Trash2,
  Loader2,
  ExternalLink,
  BookOpen,
  Calendar,
  Layers,
} from 'lucide-react';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { ReferenceDocument } from '../../api/references';

interface Props {
  references: ReferenceDocument[];
  isLoading: boolean;
  onDelete: (id: string) => Promise<void>;
  onOpenUpload: () => void;
  onOpenAddWebsite: () => void;
}

export const ReferenceSourceList: React.FC<Props> = ({
  references,
  isLoading,
  onDelete,
  onOpenUpload,
  onOpenAddWebsite,
}) => {
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to remove this reference and its indexed knowledge?')) {
      return;
    }
    setDeletingId(id);
    try {
      await onDelete(id);
    } finally {
      setDeletingId(null);
    }
  };

  const getSourceIcon = (type: string) => {
    switch (type) {
      case 'url':
        return (
          <div className="w-10 h-10 rounded-2xl bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 flex items-center justify-center shrink-0">
            <Globe className="w-5 h-5" />
          </div>
        );
      case 'pdf':
        return (
          <div className="w-10 h-10 rounded-2xl bg-rose-50 dark:bg-rose-950/40 text-rose-600 dark:text-rose-400 flex items-center justify-center shrink-0">
            <FileText className="w-5 h-5" />
          </div>
        );
      default:
        return (
          <div className="w-10 h-10 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
            <FileText className="w-5 h-5" />
          </div>
        );
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'url':
        return 'Website';
      case 'pdf':
        return 'PDF';
      case 'md':
        return 'Markdown';
      case 'txt':
        return 'Text';
      default:
        return type.toUpperCase();
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'ready':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100/70 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Ready
          </span>
        );
      case 'processing':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-100/70 dark:bg-amber-950/50 text-amber-700 dark:text-amber-300">
            <Loader2 className="w-3 h-3 animate-spin" />
            Processing
          </span>
        );
      case 'failed':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-100/70 dark:bg-rose-950/50 text-rose-700 dark:text-rose-300">
            Failed
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
            {status}
          </span>
        );
    }
  };

  if (isLoading) {
    return (
      <div className="py-16 flex flex-col items-center justify-center text-center gap-3">
        <Loader2 className="w-8 h-8 animate-spin text-teal-600 dark:text-teal-400" />
        <p className="text-sm font-semibold text-slate-500 dark:text-slate-400">
          Loading your reference materials...
        </p>
      </div>
    );
  }

  if (references.length === 0) {
    return (
      <Card className="py-12 px-6 flex flex-col items-center justify-center text-center bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl">
        <div className="w-16 h-16 rounded-3xl bg-teal-50 dark:bg-teal-950/40 text-teal-600 dark:text-teal-400 flex items-center justify-center mb-4">
          <BookOpen className="w-8 h-8" />
        </div>
        <h3 className="text-lg font-bold text-slate-900 dark:text-white font-display mb-1">
          No reference materials yet
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mb-6">
          Upload grammar PDFs, notes, or add articles from the web. They will become your private knowledge base for quizzes and AI review.
        </p>
        <div className="flex items-center gap-3">
          <Button variant="primary" size="sm" onClick={onOpenUpload}>
            Upload Document
          </Button>
          <Button variant="outline" size="sm" onClick={onOpenAddWebsite}>
            Add Website
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      {references.map((doc) => (
        <Card
          key={doc.id}
          className="p-4 sm:p-5 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl hover:border-slate-300 dark:hover:border-slate-700 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4"
        >
          {/* Left: Icon & Info */}
          <div className="flex items-start gap-3.5 min-w-0">
            {getSourceIcon(doc.source_type)}
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 flex-wrap">
                <h4 className="text-sm sm:text-base font-bold text-slate-900 dark:text-white truncate">
                  {doc.title}
                </h4>
                {getStatusBadge(doc.status)}
              </div>

              {/* Source Type & Meta */}
              <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400 mt-1 flex-wrap">
                <span className="font-semibold text-slate-600 dark:text-slate-300">
                  {getTypeLabel(doc.source_type)}
                </span>
                <span>·</span>
                <span className="flex items-center gap-1">
                  <Layers className="w-3.5 h-3.5 text-slate-400" />
                  {doc.chunk_count} {doc.chunk_count === 1 ? 'chunk' : 'chunks'}
                </span>
                {doc.source_url && (
                  <>
                    <span>·</span>
                    <a
                      href={doc.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 hover:text-teal-600 dark:hover:text-teal-400 hover:underline truncate max-w-[200px]"
                    >
                      <ExternalLink className="w-3 h-3 shrink-0" />
                      <span className="truncate">{new URL(doc.source_url).hostname}</span>
                    </a>
                  </>
                )}
                <span>·</span>
                <span className="flex items-center gap-1 text-[11px]">
                  <Calendar className="w-3 h-3 text-slate-400" />
                  {new Date(doc.created_at).toLocaleDateString()}
                </span>
              </div>

              {doc.error_message && (
                <p className="text-xs text-rose-600 dark:text-rose-400 mt-1.5 font-medium">
                  Error: {doc.error_message}
                </p>
              )}
            </div>
          </div>

          {/* Right: Actions */}
          <div className="flex items-center justify-end gap-2 shrink-0 border-t sm:border-t-0 pt-2 sm:pt-0 border-slate-100 dark:border-slate-800">
            <Button
              variant="ghost"
              size="sm"
              isLoading={deletingId === doc.id}
              onClick={() => handleDelete(doc.id)}
              leftIcon={<Trash2 className="w-4 h-4 text-rose-500" />}
              className="text-rose-600 hover:text-rose-700 hover:bg-rose-50 dark:hover:bg-rose-950/40"
            >
              Delete
            </Button>
          </div>
        </Card>
      ))}
    </div>
  );
};
