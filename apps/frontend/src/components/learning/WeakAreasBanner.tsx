import React from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle } from 'lucide-react';
import { WeakAreaItem } from '../../types';

interface WeakAreasBannerProps {
  weaknesses: WeakAreaItem[];
  reviewPath?: string;
}

export const WeakAreasBanner: React.FC<WeakAreasBannerProps> = ({
  weaknesses,
  reviewPath = '/review/attempt-sample-1',
}) => {
  if (!weaknesses || weaknesses.length === 0) return null;

  const topWeakness = weaknesses[0];

  return (
    <div className="bg-amber-50/70 dark:bg-amber-950/20 border border-amber-200/80 dark:border-amber-900/40 rounded-3xl p-5 sm:p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div className="flex items-start gap-3">
        <div className="p-2.5 bg-amber-100 dark:bg-amber-900/60 text-amber-700 dark:text-amber-300 rounded-2xl shrink-0 mt-0.5">
          <AlertCircle className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-slate-900 dark:text-white">
            Review Weak Areas ({weaknesses.length} concepts)
          </h3>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-0.5">
            Recent challenge:{' '}
            <span className="font-semibold text-amber-800 dark:text-amber-300">
              {topWeakness.concept}
            </span>{' '}
            ({topWeakness.accuracyRate}% accuracy)
          </p>
        </div>
      </div>

      <Link
        to={reviewPath}
        className="px-4 py-2 bg-white dark:bg-slate-900 text-amber-800 dark:text-amber-300 border border-amber-300 dark:border-amber-800 font-bold text-xs rounded-xl hover:bg-amber-100/50 transition-colors text-center shrink-0"
      >
        Review Mistakes
      </Link>
    </div>
  );
};
