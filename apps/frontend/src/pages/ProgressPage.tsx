import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Flame, Sparkles, Target, Trophy, Clock, CheckCircle, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { getWeaknesses } from '../lib/api/progress';
import { WeakAreaItem } from '../types';
import { ProgressBar } from '../components/ui/ProgressBar';

export const ProgressPage: React.FC = () => {
  const { currentUser } = useAuth();
  const [weaknesses, setWeaknesses] = useState<WeakAreaItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

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
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
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

          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-5 shadow-sm flex flex-col gap-2">
            <div className="flex items-center gap-2 text-indigo-500">
              <Target className="w-5 h-5" />
              <span className="text-xs font-bold text-slate-500 dark:text-slate-400">Accuracy</span>
            </div>
            <span className="text-3xl font-extrabold text-slate-900 dark:text-white tabular-nums">
              88%
            </span>
            <span className="text-xs text-slate-400">Overall quiz rate</span>
          </div>

          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-5 shadow-sm flex flex-col gap-2">
            <div className="flex items-center gap-2 text-emerald-500">
              <Trophy className="w-5 h-5 fill-emerald-500" />
              <span className="text-xs font-bold text-slate-500 dark:text-slate-400">Quizzes</span>
            </div>
            <span className="text-3xl font-extrabold text-slate-900 dark:text-white tabular-nums">
              14
            </span>
            <span className="text-xs text-slate-400">Completed sessions</span>
          </div>
        </div>

        {/* Weak Areas Breakdown */}
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
              to="/review/attempt-sample-1"
              className="text-xs font-bold text-teal-600 dark:text-teal-400 hover:underline flex items-center gap-1"
            >
              <span>View mistake cards</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

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
        </div>
      </div>
    </div>
  );
};
