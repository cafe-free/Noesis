import React from 'react';
import { Wand2 } from 'lucide-react';

interface LearnHeaderProps {
  userName: string;
  selectedLanguage: string;
  currentLevel?: string;
  totalXp?: number;
  onOpenGenerator: () => void;
}

export const LearnHeader: React.FC<LearnHeaderProps> = ({
  userName,
  selectedLanguage,
  currentLevel = 'A1',
  totalXp = 380,
  onOpenGenerator,
}) => {
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white font-display">
          {getGreeting()}, {userName}
        </h1>
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 dark:text-slate-400 mt-1">
          <span>{selectedLanguage}</span>
          <span aria-hidden="true">·</span>
          <span>Level {currentLevel}</span>
          <span aria-hidden="true">·</span>
          <span className="text-teal-600 dark:text-teal-400 font-bold">
            {totalXp} Total XP
          </span>
        </div>
      </div>

      {/* AI Generator Action Button */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onOpenGenerator}
          className="py-2.5 px-4 rounded-2xl bg-teal-600 hover:bg-teal-500 active:bg-teal-700 text-white font-bold text-xs sm:text-sm flex items-center gap-2 shadow-md shadow-teal-600/20 border-b-4 border-teal-700 active:border-b-0 active:translate-y-1 transition-all cursor-pointer"
        >
          <Wand2 className="w-4 h-4" />
          <span>Create Practice Quiz</span>
        </button>
      </div>
    </div>
  );
};
