import React from 'react';
import { MistakeReviewItem } from '../../types';

interface MistakeCardProps {
  item: MistakeReviewItem;
  index: number;
}

export const MistakeCard: React.FC<MistakeCardProps> = ({ item, index }) => {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm flex flex-col gap-4">
      {/* Concept Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
        <span className="text-xs font-bold text-rose-600 dark:text-rose-400">
          {index + 1}. {item.concept}
        </span>
        <span className="text-xs text-slate-400">Practice Card</span>
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

      {/* Comparison Box */}
      <div className="grid sm:grid-cols-2 gap-3 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-200/60 dark:border-slate-700/60">
        <div>
          <span className="text-xs font-bold text-rose-600 dark:text-rose-400 block mb-1">
            You answered:
          </span>
          <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 font-mono">
            {item.userAnswer || '(blank)'}
          </p>
        </div>
        <div>
          <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 block mb-1">
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
