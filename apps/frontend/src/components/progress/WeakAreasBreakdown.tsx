import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import { WeakAreaItem } from '../../types';
import { ProgressBar } from '../ui/ProgressBar';

interface WeakAreasBreakdownProps {
  weaknesses: WeakAreaItem[];
  reviewPath?: string;
}

export const WeakAreasBreakdown: React.FC<WeakAreasBreakdownProps> = ({
  weaknesses,
  reviewPath = '/review/attempt-sample-1',
}) => {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 sm:p-8 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-bold text-slate-900 dark:text-white font-display">
            Concepts Needing Reinforcement
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            AI algorithms identify patterns from missed quiz questions
          </p>
        </div>
        <Link
          to={reviewPath}
          className="text-xs font-bold text-teal-600 dark:text-teal-400 hover:underline flex items-center gap-1"
        >
          <span>View mistake cards</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      {weaknesses.length === 0 ? (
        <p className="text-xs text-slate-400 italic py-4 text-center">
          No weak areas logged yet. Keep practicing quizzes!
        </p>
      ) : (
        <div className="flex flex-col gap-4">
          {weaknesses.map((item) => (
            <div
              key={item.id}
              className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
            >
              <div className="flex-1">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 mb-1">
                  <span>{item.topic}</span>
                  <span aria-hidden="true">·</span>
                  <span>Last practiced: {item.lastPracticed}</span>
                  <span aria-hidden="true">·</span>
                  <span className="text-rose-500 font-bold">
                    {item.mistakeCount} mistakes logged
                  </span>
                </div>
                <h4 className="text-sm font-bold text-slate-800 dark:text-slate-100">
                  {item.concept}
                </h4>
                <div className="mt-2 max-w-xs">
                  <ProgressBar
                    value={item.accuracyRate}
                    height="sm"
                    color={item.accuracyRate >= 70 ? 'amber' : 'rose'}
                    showLabel
                  />
                </div>
              </div>

              <Link
                to="/quiz/food-and-drinks"
                className="px-4 py-2 bg-white dark:bg-slate-900 text-teal-700 dark:text-teal-300 border border-teal-200 dark:border-teal-800 font-bold text-xs rounded-xl hover:bg-teal-50 dark:hover:bg-teal-950/30 transition-colors text-center shrink-0"
              >
                Practice Topic
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
