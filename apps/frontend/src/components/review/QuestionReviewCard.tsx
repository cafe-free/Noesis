import React from 'react';
import { CheckCircle2, XCircle } from 'lucide-react';
import { ExerciseAttemptItem } from '../../types';

interface QuestionReviewCardProps {
  item: ExerciseAttemptItem;
  index: number;
}

export const QuestionReviewCard: React.FC<QuestionReviewCardProps> = ({ item, index }) => {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm flex flex-col gap-4">
      {/* Question Header & Status */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
        <span className="text-xs font-bold text-slate-500 dark:text-slate-400">
          Question {index + 1}
        </span>
        <div className="flex items-center gap-1.5">
          {item.isCorrect ? (
            <span className="inline-flex items-center gap-1 text-xs font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 px-2.5 py-1 rounded-full border border-emerald-200 dark:border-emerald-900/50">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Correct</span>
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 text-xs font-bold text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/40 px-2.5 py-1 rounded-full border border-rose-200 dark:border-rose-900/50">
              <XCircle className="w-3.5 h-3.5" />
              <span>Missed</span>
            </span>
          )}
        </div>
      </div>

      {/* Prompt */}
      <div>
        <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
          Question Prompt
        </span>
        <p className="text-base font-bold text-slate-800 dark:text-slate-100 mt-0.5">
          {item.prompt}
        </p>
      </div>

      {/* Answer Details */}
      <div className="grid sm:grid-cols-2 gap-3 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-200/60 dark:border-slate-700/60">
        <div>
          <span
            className={`text-xs font-bold block mb-1 ${
              item.isCorrect
                ? 'text-emerald-600 dark:text-emerald-400'
                : 'text-rose-600 dark:text-rose-400'
            }`}
          >
            You answered:
          </span>
          <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 font-mono">
            {item.userAnswer || '(blank)'}
          </p>
        </div>
        <div>
          <span className="text-xs font-bold text-teal-600 dark:text-teal-400 block mb-1">
            Correct answer:
          </span>
          <p className="text-sm font-bold text-slate-900 dark:text-white font-mono">
            {item.correctAnswer}
          </p>
        </div>
      </div>

      {/* Explanation */}
      {item.explanation && (
        <div className="p-3.5 bg-teal-50/70 dark:bg-teal-950/20 border border-teal-200/60 dark:border-teal-900/50 rounded-2xl">
          <span className="text-xs font-bold text-teal-800 dark:text-teal-300 block mb-1">
            Grammar & Vocabulary Note:
          </span>
          <p className="text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
            {item.explanation}
          </p>
        </div>
      )}
    </div>
  );
};
