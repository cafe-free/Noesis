import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { getWeaknesses } from '../api/progress';
import { listUserAttempts } from '../api/attempts';
import { QuizAttemptResult, WeakAreaItem } from '../types';
import {
  ProgressStatsGrid,
  WeakAreasBreakdown,
  QuizHistorySection,
} from '../components/progress';

export const ProgressPage: React.FC = () => {
  const { currentUser } = useAuth();
  const [weaknesses, setWeaknesses] = useState<WeakAreaItem[]>([]);
  const [attempts, setAttempts] = useState<QuizAttemptResult[]>([]);
  const [isLoadingAttempts, setIsLoadingAttempts] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [weaknessData, attemptData] = await Promise.all([
          getWeaknesses(),
          listUserAttempts(),
        ]);
        setWeaknesses(weaknessData);
        setAttempts(attemptData);
      } catch {
        // Fallback
      } finally {
        setIsLoadingAttempts(false);
      }
    }
    loadData();
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
        <ProgressStatsGrid
          currentUser={currentUser}
          completedQuizzes={attempts.length || 1}
        />

        {/* Completed Quiz Records & Review */}
        <QuizHistorySection
          attempts={attempts}
          isLoading={isLoadingAttempts}
        />

        {/* Weak Areas Breakdown */}
        <WeakAreasBreakdown weaknesses={weaknesses} />
      </div>
    </div>
  );
};
