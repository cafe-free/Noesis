import React, { useState, useEffect, useCallback } from 'react';
import { UploadCloud, Globe, BookMarked, CheckCircle2, AlertCircle, X } from 'lucide-react';
import { Button } from '../components/ui/Button';
import {
  AddWebsiteDialog,
  UploadDocumentDialog,
  ReferenceSearchSection,
  ReferenceSourceList,
} from '../components/references';
import { ReferenceDocument, listReferences, deleteReference } from '../api/references';
import { useAuth } from '../context/AuthContext';

interface ToastMessage {
  id: string;
  type: 'success' | 'error';
  text: string;
}

export const ReferencesPage: React.FC = () => {
  const { isAuthenticated } = useAuth();

  const [references, setReferences] = useState<ReferenceDocument[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAddWebsiteOpen, setIsAddWebsiteOpen] = useState(false);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [toast, setToast] = useState<ToastMessage | null>(null);

  const showToast = (type: 'success' | 'error', text: string) => {
    const id = String(Date.now());
    setToast({ id, type, text });
    setTimeout(() => {
      setToast((prev) => (prev?.id === id ? null : prev));
    }, 4000);
  };

  const loadReferences = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await listReferences();
      setReferences(data || []);
    } catch {
      // Fallback
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadReferences();
  }, [loadReferences]);

  const handleDelete = async (id: string) => {
    try {
      await deleteReference(id);
      setReferences((prev) => prev.filter((r) => r.id !== id));
      showToast('success', 'Reference deleted successfully.');
    } catch (err: unknown) {
      showToast(
        'error',
        err instanceof Error ? err.message : 'Failed to delete reference.'
      );
    }
  };

  const handleWebsiteAdded = () => {
    loadReferences();
    showToast('success', 'Website reference added and indexed successfully.');
  };

  const handleDocumentUploaded = () => {
    loadReferences();
    showToast('success', 'Document reference uploaded and indexed successfully.');
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 pb-24 md:pb-16">
      {/* Toast Notification Banner */}
      {toast && (
        <div className="fixed top-20 right-4 z-50 animate-in slide-in-from-top duration-300">
          <div
            className={`px-4 py-3 rounded-2xl shadow-lg border flex items-center gap-3 text-sm font-semibold ${
              toast.type === 'success'
                ? 'bg-emerald-50 dark:bg-emerald-950/90 border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-200'
                : 'bg-rose-50 dark:bg-rose-950/90 border-rose-200 dark:border-rose-800 text-rose-800 dark:text-rose-200'
            }`}
          >
            {toast.type === 'success' ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0" />
            ) : (
              <AlertCircle className="w-5 h-5 text-rose-600 dark:text-rose-400 shrink-0" />
            )}
            <span>{toast.text}</span>
            <button
              onClick={() => setToast(null)}
              className="p-1 hover:opacity-75 transition-opacity"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      <div className="max-w-4xl mx-auto px-4 sm:px-6 pt-6 sm:pt-10 flex flex-col gap-8">
        {/* Top Header & Actions */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-teal-50 dark:bg-teal-950/40 text-teal-600 dark:text-teal-400 flex items-center justify-center shrink-0">
              <BookMarked className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white font-display">
                References
              </h1>
              <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-0.5">
                Manage your private knowledge base from uploaded documents and websites
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2.5 flex-wrap sm:flex-nowrap">
            <Button
              variant="outline"
              size="md"
              onClick={() => setIsUploadOpen(true)}
              leftIcon={<UploadCloud className="w-4 h-4" />}
              className="flex-1 sm:flex-initial"
            >
              Upload Document
            </Button>
            <Button
              variant="primary"
              size="md"
              onClick={() => setIsAddWebsiteOpen(true)}
              leftIcon={<Globe className="w-4 h-4" />}
              className="flex-1 sm:flex-initial"
            >
              Add Website
            </Button>
          </div>
        </div>

        {/* Semantic RAG Retrieval Search Interface */}
        <ReferenceSearchSection />

        {/* Section Divider */}
        <div className="relative">
          <div className="absolute inset-0 flex items-center" aria-hidden="true">
            <div className="w-full border-t border-slate-200 dark:border-slate-800" />
          </div>
          <div className="relative flex justify-start">
            <span className="bg-slate-50 dark:bg-slate-950 pr-3 text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
              Source List
            </span>
          </div>
        </div>

        {/* Source List */}
        <div>
          <ReferenceSourceList
            references={references}
            isLoading={isLoading}
            onDelete={handleDelete}
            onOpenUpload={() => setIsUploadOpen(true)}
            onOpenAddWebsite={() => setIsAddWebsiteOpen(true)}
          />
        </div>
      </div>

      {/* Dialogs */}
      <AddWebsiteDialog
        isOpen={isAddWebsiteOpen}
        onClose={() => setIsAddWebsiteOpen(false)}
        onAdded={handleWebsiteAdded}
      />

      <UploadDocumentDialog
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onUploaded={handleDocumentUploaded}
      />
    </div>
  );
};
