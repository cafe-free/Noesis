import React from 'react';
import { Clock, Sparkles, Target } from 'lucide-react';

interface QuizResultStatsProps {
  accuracyPercentage: number;
  score: number;
  totalQuestions: number;
  xpGained: number;
  timeSpentSeconds: number;
}

export const QuizResultStats: React.FC<QuizResultStatsProps> = ({
  accuracyPercentage,
  score,
  totalQuestions,
  xpGained,
  timeSpentSeconds,
}) => {
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  return (
    <div className="w-full grid grid-cols-3 gap-3 mb-8">
      {/* Accuracy */}
      <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col items-center">
        <div className="flex items-center gap-1 text-slate-400 mb-1">
          <Target className="w-4 h-4 text-teal-500" />
          <span className="text-xs font-semibold">Accuracy</span>
        </div>
        <span className="text-2xl font-extrabold text-teal-600 dark:text-teal-400 tabular-nums">
          {accuracyPercentage}%
        </span>
        <span className="text-[11px] font-medium text-slate-400 mt-0.5">
          {score} / {totalQuestions}
        </span>
      </div>

      {/* XP Gained */}
      <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col items-center">
        <div className="flex items-center gap-1 text-slate-400 mb-1">
          <Sparkles className="w-4 h-4 text-amber-500 fill-amber-500" />
          <span className="text-xs font-semibold">Total XP</span>
        </div>
        <span className="text-2xl font-extrabold text-amber-600 dark:text-amber-400 tabular-nums">
          +{xpGained}
        </span>
        <span className="text-[11px] font-medium text-slate-400 mt-0.5">XP earned</span>
      </div>

      {/* Time */}
      <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col items-center">
        <div className="flex items-center gap-1 text-slate-400 mb-1">
          <Clock className="w-4 h-4 text-indigo-500" />
          <span className="text-xs font-semibold">Time</span>
        </div>
        <span className="text-2xl font-extrabold text-slate-800 dark:text-slate-200 tabular-nums">
          {formatTime(timeSpentSeconds)}
        </span>
        <span className="text-[11px] font-medium text-slate-400 mt-0.5">Duration</span>
      </div>
    </div>
  );
};
