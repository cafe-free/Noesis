import React, { useState } from 'react';
import { Globe, X, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { Button } from '../ui/Button';
import { addUrlReference } from '../../api/references';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onAdded: () => void;
}

type SubmissionState = 'idle' | 'adding' | 'processing' | 'ready' | 'failed';

export const AddWebsiteDialog: React.FC<Props> = ({ isOpen, onClose, onAdded }) => {
  const [url, setUrl] = useState('');
  const [title, setTitle] = useState('');
  const [state, setState] = useState<SubmissionState>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleClose = () => {
    if (state === 'adding' || state === 'processing') return;
    setUrl('');
    setTitle('');
    setState('idle');
    setErrorMessage(null);
    onClose();
  };

  const validateUrlClient = (raw: string): string | null => {
    const trimmed = raw.trim();
    if (!trimmed) {
      return 'Please enter a website URL.';
    }
    try {
      const parsed = new URL(trimmed);
      if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
        return 'URL must start with http:// or https://';
      }
      if (!parsed.hostname || !parsed.hostname.includes('.')) {
        return 'Please enter a valid domain name (e.g., https://example.com).';
      }
    } catch {
      return 'Please enter a valid URL (e.g., https://example.com/article).';
    }
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    // Client-side UX validation
    const clientErr = validateUrlClient(url);
    if (clientErr) {
      setErrorMessage(clientErr);
      return;
    }

    try {
      // 1. Adding...
      setState('adding');
      await new Promise((r) => setTimeout(r, 400));

      // 2. Processing
      setState('processing');

      // Call API
      await addUrlReference({
        url: url.trim(),
        title: title.trim() || undefined,
      });

      // 3. Ready
      setState('ready');
      await new Promise((r) => setTimeout(r, 600));

      onAdded();
      handleClose();
    } catch (err: unknown) {
      setState('failed');
      setErrorMessage(
        err instanceof Error ? err.message : 'Failed to ingest website. Please check the URL and try again.'
      );
    }
  };

  const isBusy = state === 'adding' || state === 'processing';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 max-w-md w-full border border-slate-200 dark:border-slate-800 shadow-2xl relative">
        {/* Close Button */}
        {!isBusy && (
          <button
            type="button"
            onClick={handleClose}
            aria-label="Close"
            className="absolute top-5 right-5 p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        )}

        {/* Dialog Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-2xl bg-teal-50 dark:bg-teal-950/40 text-teal-600 dark:text-teal-400 flex items-center justify-center">
            <Globe className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white font-display">
              Add Website
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Extract and embed reference knowledge from a web page
            </p>
          </div>
        </div>

        {/* Error message */}
        {errorMessage && (
          <div className="mb-4 p-3.5 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/50 rounded-2xl flex items-center gap-2.5 text-rose-700 dark:text-rose-300 text-xs font-semibold">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Status transitions */}
        {isBusy || state === 'ready' ? (
          <div className="py-8 flex flex-col items-center text-center gap-3">
            <div className="w-14 h-14 rounded-2xl bg-teal-500/10 text-teal-600 dark:text-teal-400 flex items-center justify-center">
              {state === 'ready' ? (
                <CheckCircle2 className="w-8 h-8 text-emerald-500" />
              ) : (
                <Loader2 className="w-7 h-7 animate-spin" />
              )}
            </div>
            <div>
              <p className="text-base font-bold text-slate-800 dark:text-slate-100 font-display">
                {state === 'adding' && 'Adding...'}
                {state === 'processing' && 'Processing'}
                {state === 'ready' && 'Ready'}
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                {state === 'adding' && 'Connecting to web server and fetching content...'}
                {state === 'processing' && 'Cleaning boilerplate, chunking text, and generating embeddings...'}
                {state === 'ready' && 'Knowledge indexed into your private reference library.'}
              </p>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                Website URL
              </label>
              <input
                type="text"
                value={url}
                onChange={(e) => {
                  setUrl(e.target.value);
                  if (errorMessage) setErrorMessage(null);
                }}
                placeholder="https://example.com/spanish-grammar"
                required
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-800 dark:text-slate-100 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-teal-500 transition-all placeholder:text-slate-400"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                Custom Title (Optional)
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Spanish Verbs Article"
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-800 dark:text-slate-100 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-teal-500 transition-all placeholder:text-slate-400"
              />
            </div>

            <div className="flex items-center justify-end gap-2.5 pt-2">
              <Button
                type="button"
                variant="ghost"
                size="md"
                onClick={handleClose}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                size="md"
                leftIcon={<Globe className="w-4 h-4" />}
              >
                Add Website
              </Button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
