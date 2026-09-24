import React from 'react';
import { Flame, Sparkles, Target, Trophy } from 'lucide-react';
import { UserProfile } from '../../types';

interface ProgressStatsGridProps {
  currentUser: UserProfile | null;
  accuracyRate?: number;
  completedQuizzes?: number;
}

export const ProgressStatsGrid: React.FC<ProgressStatsGridProps> = ({
  currentUser,
  accuracyRate = 88,
  completedQuizzes = 14,
}) => {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      {/* Streak */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-5 shadow-sm flex flex-col gap-2">
        <div className="flex items-center gap-2 text-amber-500">
          <Flame className="w-5 h-5 fill-amber-500" />
          <span className="text-xs font-bold text-slate-500 dark:text-slate-400">Streak</span>
        </div>
        <span className="text-3xl font-extrabold text-slate-900 dark:text-white tabular-nums">
          {currentUser?.streakDays || 6}
        </span>
        <span className="text-xs text-slate-400">Consecutive days</span>
      </div>

      {/* Total XP */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-5 shadow-sm flex flex-col gap-2">
        <div className="flex items-center gap-2 text-teal-500">
          <Sparkles className="w-5 h-5 fill-teal-500" />
          <span className="text-xs font-bold text-slate-500 dark:text-slate-400">Total XP</span>
        </div>
        <span className="text-3xl font-extrabold text-teal-600 dark:text-teal-400 tabular-nums">
          {currentUser?.totalXp || 380}
        </span>
        <span className="text-xs text-slate-400">Experience points</span>
      </div>

      {/* Accuracy */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-5 shadow-sm flex flex-col gap-2">
        <div className="flex items-center gap-2 text-indigo-500">
          <Target className="w-5 h-5" />
          <span className="text-xs font-bold text-slate-500 dark:text-slate-400">Accuracy</span>
        </div>
        <span className="text-3xl font-extrabold text-slate-900 dark:text-white tabular-nums">
          {accuracyRate}%
        </span>
        <span className="text-xs text-slate-400">Overall quiz rate</span>
      </div>

      {/* Quizzes */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-5 shadow-sm flex flex-col gap-2">
        <div className="flex items-center gap-2 text-emerald-500">
          <Trophy className="w-5 h-5 fill-emerald-500" />
          <span className="text-xs font-bold text-slate-500 dark:text-slate-400">Quizzes</span>
        </div>
        <span className="text-3xl font-extrabold text-slate-900 dark:text-white tabular-nums">
          {completedQuizzes}
        </span>
        <span className="text-xs text-slate-400">Completed sessions</span>
      </div>
    </div>
  );
};
