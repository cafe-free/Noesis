import React from 'react';
import { Flame, Sparkles } from 'lucide-react';
import { ProgressBar } from '../ui/ProgressBar';

interface DailyGoalProps {
  todayXp: number;
  goalXp: number;
  streakDays: number;
}

export const DailyGoal: React.FC<DailyGoalProps> = ({
  todayXp,
  goalXp,
  streakDays,
}) => {
  const isGoalReached = todayXp >= goalXp;

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-5 sm:p-6 shadow-sm flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-amber-50 dark:bg-amber-950/40 text-amber-500 flex items-center justify-center">
            <Sparkles className="w-4 h-4 fill-amber-500" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white">
              Daily Goal
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {isGoalReached ? 'Daily goal accomplished!' : 'Keep momentum going!'}
            </p>
          </div>
        </div>

        {/* Streak indicator */}
        <div className="flex items-center gap-1.5 px-3 py-1 bg-amber-50 dark:bg-amber-950/40 border border-amber-200/60 dark:border-amber-900/60 rounded-full text-xs font-bold text-amber-700 dark:text-amber-400">
          <Flame className="w-3.5 h-3.5 fill-amber-500 text-amber-500 animate-pulse" />
          <span>{streakDays} Day Streak</span>
        </div>
      </div>

      <div>
        <div className="flex justify-between items-center text-xs font-semibold mb-2">
          <span className="text-slate-500 dark:text-slate-400">XP Progress</span>
          <span className="text-slate-800 dark:text-slate-200 tabular-nums">
            {todayXp} / {goalXp} XP
          </span>
        </div>
        <ProgressBar
          value={todayXp}
          max={goalXp}
          height="md"
          color={isGoalReached ? 'emerald' : 'amber'}
        />
      </div>
    </div>
  );
};
