import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { QuizAttemptResult } from '../../types';

interface ReviewHeaderProps {
  attempt: QuizAttemptResult | null;
}

export const ReviewHeader: React.FC<ReviewHeaderProps> = ({ attempt }) => {
  return (
    <>
      {/* Top Back Nav */}
      <div className="flex items-center justify-between">
        <Link
          to="/learn"
          className="inline-flex items-center gap-2 text-xs font-bold text-slate-600 dark:text-slate-300 hover:text-teal-600 dark:hover:text-teal-400 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Dashboard</span>
        </Link>

        {attempt && (
          <span className="text-xs font-semibold text-slate-400">
            Score: {attempt.score} / {attempt.totalQuestions} ({attempt.accuracyPercentage}%)
          </span>
        )}
      </div>

      {/* Title & Introduction */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white font-display mb-1">
          Review Weak Areas
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
          Mistakes are how our brains cement patterns. Study the grammatical rules below to retain them next time.
        </p>
      </div>
    </>
  );
};
