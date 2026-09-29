import React, { useState, useRef } from 'react';
import { UploadCloud, X, FileText, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { Button } from '../ui/Button';
import { ProgressBar } from '../ui/ProgressBar';
import { uploadDocumentReference } from '../../api/references';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onUploaded: () => void;
}

type UploadState = 'idle' | 'selected' | 'uploading' | 'processing' | 'ready' | 'failed';

export const UploadDocumentDialog: React.FC<Props> = ({ isOpen, onClose, onUploaded }) => {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [state, setState] = useState<UploadState>('idle');
  const [progress, setProgress] = useState(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleClose = () => {
    if (state === 'uploading' || state === 'processing') return;
    setFile(null);
    setTitle('');
    setState('idle');
    setProgress(0);
    setErrorMessage(null);
    onClose();
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const handleFileSelect = (selectedFile: File) => {
    setErrorMessage(null);
    const fname = selectedFile.name.toLowerCase();
    const isSupported =
      fname.endsWith('.pdf') ||
      fname.endsWith('.txt') ||
      fname.endsWith('.md') ||
      fname.endsWith('.markdown');

    if (!isSupported) {
      setErrorMessage('Unsupported file format. Please upload a PDF, TXT, or Markdown document.');
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setErrorMessage('File exceeds maximum allowed size (10 MB).');
      return;
    }

    setFile(selectedFile);
    setState('selected');
    if (!title) {
      // Auto-populate default title from filename without extension
      const baseName = selectedFile.name.replace(/\.[^/.]+$/, '');
      setTitle(baseName);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setErrorMessage('Please select a file to upload.');
      return;
    }

    try {
      setErrorMessage(null);
      setState('uploading');
      setProgress(25);

      await new Promise((r) => setTimeout(r, 300));
      setProgress(60);

      setState('processing');
      setProgress(85);

      await uploadDocumentReference(file, title.trim() || undefined);

      setProgress(100);
      setState('ready');
      await new Promise((r) => setTimeout(r, 600));

      onUploaded();
      handleClose();
    } catch (err: unknown) {
      setState('failed');
      setErrorMessage(
        err instanceof Error ? err.message : 'Upload failed. Please check the file and try again.'
      );
    }
  };

  const isBusy = state === 'uploading' || state === 'processing';

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
            <UploadCloud className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white font-display">
              Upload Document
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Supported formats: PDF, TXT, Markdown
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

        {/* Processing / Progress State */}
        {isBusy || state === 'ready' ? (
          <div className="py-8 flex flex-col items-center text-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-teal-500/10 text-teal-600 dark:text-teal-400 flex items-center justify-center">
              {state === 'ready' ? (
                <CheckCircle2 className="w-8 h-8 text-emerald-500" />
              ) : (
                <Loader2 className="w-7 h-7 animate-spin" />
              )}
            </div>
            <div className="w-full">
              <p className="text-base font-bold text-slate-800 dark:text-slate-100 font-display">
                {state === 'uploading' && 'Uploading document...'}
                {state === 'processing' && 'Extracting text and chunking...'}
                {state === 'ready' && 'Document ready!'}
              </p>
              {file && (
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  {file.name} ({formatFileSize(file.size)})
                </p>
              )}
              <div className="mt-4 w-full">
                <ProgressBar value={progress} height="sm" color="teal" />
              </div>
            </div>
          </div>
        ) : (
          <form onSubmit={handleUpload} className="flex flex-col gap-4">
            {/* Drag & Drop Zone */}
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragOver(true);
              }}
              onDragLeave={() => setIsDragOver(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-2xl p-6 flex flex-col items-center justify-center text-center cursor-pointer transition-all ${
                isDragOver
                  ? 'border-teal-500 bg-teal-50/50 dark:bg-teal-950/30 ring-2 ring-teal-500/20'
                  : 'border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 hover:border-teal-400 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.txt,.md,.markdown"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files && e.target.files.length > 0) {
                    handleFileSelect(e.target.files[0]);
                  }
                }}
              />

              <div className="w-12 h-12 rounded-2xl bg-teal-100/60 dark:bg-teal-950/60 text-teal-600 dark:text-teal-400 flex items-center justify-center mb-3">
                <FileText className="w-6 h-6" />
              </div>
              <p className="text-sm font-bold text-slate-800 dark:text-slate-200">
                Drag and drop a file
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                or <span className="text-teal-600 dark:text-teal-400 font-semibold underline">Choose File</span>
              </p>
              <p className="text-[11px] text-slate-400 dark:text-slate-500 mt-2">
                Supported: PDF, TXT, Markdown (up to 10 MB)
              </p>
            </div>

            {/* Selected File Details */}
            {file && (
              <div className="p-3.5 rounded-2xl bg-teal-50/60 dark:bg-teal-950/30 border border-teal-200 dark:border-teal-900/40 flex items-center justify-between">
                <div className="flex items-center gap-2.5 min-w-0">
                  <FileText className="w-5 h-5 text-teal-600 dark:text-teal-400 shrink-0" />
                  <div className="min-w-0">
                    <p className="text-xs font-bold text-slate-800 dark:text-slate-200 truncate">
                      {file.name}
                    </p>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400">
                      {formatFileSize(file.size)}
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setFile(null);
                    setState('idle');
                  }}
                  className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            )}

            {/* Title override */}
            {file && (
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                  Reference Title
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g., Spanish Grammar Notes"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-800 dark:text-slate-100 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-teal-500 transition-all"
                />
              </div>
            )}

            {/* Actions */}
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
                disabled={!file}
                leftIcon={<UploadCloud className="w-4 h-4" />}
              >
                Upload
              </Button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
