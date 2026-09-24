import React from 'react';
import { Link } from 'react-router-dom';
import { CheckCircle } from 'lucide-react';
import { Button } from '../ui/Button';

export const MistakeEmptyState: React.FC = () => {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-8 text-center flex flex-col items-center gap-4 shadow-sm">
      <div className="w-14 h-14 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-500 flex items-center justify-center">
        <CheckCircle className="w-8 h-8" />
      </div>
      <div>
        <h3 className="text-lg font-bold text-slate-900 dark:text-white font-display">
          No mistakes in this attempt!
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-sm">
          You aced every exercise with 100% precision. Keep practicing new lessons to expand your vocabulary.
        </p>
      </div>
      <Link to="/learn" className="mt-2">
        <Button size="md" variant="primary">
          Return to Dashboard
        </Button>
      </Link>
    </div>
  );
};
