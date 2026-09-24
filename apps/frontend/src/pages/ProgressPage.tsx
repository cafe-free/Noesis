import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { getWeaknesses } from '../lib/api/progress';
import { WeakAreaItem } from '../types';
import { ProgressStatsGrid, WeakAreasBreakdown } from '../components/progress';

export const ProgressPage: React.FC = () => {
  const { currentUser } = useAuth();
  const [weaknesses, setWeaknesses] = useState<WeakAreaItem[]>([]);
  const [, setIsLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await getWeaknesses();
        setWeaknesses(data);
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 pb-24 md:pb-16">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 pt-6 sm:pt-10 flex flex-col gap-8">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white font-display">
            Learning Progress
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Track your weekly consistency, grammar milestones, and vocabulary mastery
          </p>
        </div>

        {/* Highlight Stats Grid */}
        <ProgressStatsGrid currentUser={currentUser} />

        {/* Weak Areas Breakdown */}
        <WeakAreasBreakdown weaknesses={weaknesses} />
      </div>
    </div>
  );
};
