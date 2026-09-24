import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, Wand2, BookOpen, AlertCircle, ArrowRight, Flame } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { DailyGoal } from '../components/learning/DailyGoal';
import { LessonCard } from '../components/learning/LessonCard';
import { AiQuizGeneratorModal } from '../components/learning/AiQuizGeneratorModal';
import { listQuizzes } from '../lib/api/quizzes';
import { getWeaknesses } from '../lib/api/progress';
import { Quiz, WeakAreaItem } from '../types';

export const LearnPage: React.FC = () => {
  const { currentUser } = useAuth();
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [weaknesses, setWeaknesses] = useState<WeakAreaItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGeneratorOpen, setIsGeneratorOpen] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState(
    currentUser?.learningLanguage || 'Spanish'
  );

  useEffect(() => {
    async function loadData() {
      try {
        const [quizList, weakList] = await Promise.all([
          listQuizzes(),
          getWeaknesses(),
        ]);
        setQuizzes(quizList);
        setWeaknesses(weakList);
      } catch {
        // Fallback
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const userName = currentUser?.name || 'Learner';

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 pb-24 md:pb-16">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 pt-6 sm:pt-10 flex flex-col gap-8">
        {/* Top Greeting & Language Switcher */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white font-display">
              {getGreeting()}, {userName}
            </h1>
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 dark:text-slate-400 mt-1">
              <span>{selectedLanguage}</span>
              <span aria-hidden="true">·</span>
              <span>Level {currentUser?.currentLevel || 'A1'}</span>
              <span aria-hidden="true">·</span>
              <span className="text-teal-600 dark:text-teal-400 font-bold">
                {currentUser?.totalXp || 380} Total XP
              </span>
            </div>
          </div>

          {/* AI Generator Action Button */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsGeneratorOpen(true)}
              className="py-2.5 px-4 rounded-2xl bg-teal-600 hover:bg-teal-500 active:bg-teal-700 text-white font-bold text-xs sm:text-sm flex items-center gap-2 shadow-md shadow-teal-600/20 border-b-4 border-teal-700 active:border-b-0 active:translate-y-1 transition-all cursor-pointer"
            >
              <Wand2 className="w-4 h-4" />
              <span>Create Practice Quiz</span>
            </button>
          </div>
        </div>

        {/* Dashboard Grid: Daily Goal & Continue Hero */}
        <div className="grid md:grid-cols-3 gap-6">
          {/* Daily Goal Card */}
          <div className="md:col-span-1">
            <DailyGoal
              todayXp={currentUser?.todayXp || 12}
              goalXp={currentUser?.dailyGoalXp || 20}
              streakDays={currentUser?.streakDays || 6}
            />
          </div>

          {/* Featured / Continue Learning Banner */}
          <div className="md:col-span-2 bg-gradient-to-br from-teal-700 via-teal-600 to-emerald-600 rounded-3xl p-6 sm:p-7 text-white shadow-lg flex flex-col justify-between relative overflow-hidden">
            <div className="absolute -right-6 -bottom-6 w-36 h-36 bg-white/10 rounded-full blur-xl pointer-events-none" />

            <div className="relative z-10">
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-white/20 text-xs font-bold mb-3 backdrop-blur-sm">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Next Recommended Lesson</span>
              </div>
              <h2 className="text-2xl sm:text-3xl font-extrabold font-display mb-1.5">
                Food & Drinks
              </h2>
              <p className="text-xs sm:text-sm text-teal-100 max-w-md mb-4 leading-relaxed">
                Learn to express food preferences, order dishes at cafes, and master -er verb conjugations.
              </p>
            </div>

            <div className="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-2 border-t border-white/20">
              <div className="flex items-center gap-2 text-xs font-medium text-teal-100">
                <span>Progress: 75% complete</span>
                <span aria-hidden="true">·</span>
                <span>+40 XP</span>
              </div>
              <Link
                to="/quiz/food-and-drinks"
                className="px-6 py-2.5 rounded-xl bg-white text-teal-800 font-bold text-sm hover:bg-teal-50 transition-all text-center shadow-md active:scale-95"
              >
                CONTINUE
              </Link>
            </div>
          </div>
        </div>

        {/* Weak Areas Banner / Quick Practice */}
        {weaknesses.length > 0 && (
          <div className="bg-amber-50/70 dark:bg-amber-950/20 border border-amber-200/80 dark:border-amber-900/40 rounded-3xl p-5 sm:p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="p-2.5 bg-amber-100 dark:bg-amber-900/60 text-amber-700 dark:text-amber-300 rounded-2xl shrink-0 mt-0.5">
                <AlertCircle className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                  Review Weak Areas ({weaknesses.length} concepts)
                </h3>
                <p className="text-xs text-slate-600 dark:text-slate-400 mt-0.5">
                  Recent challenge:{' '}
                  <span className="font-semibold text-amber-800 dark:text-amber-300">
                    {weaknesses[0].concept}
                  </span>{' '}
                  ({weaknesses[0].accuracyRate}% accuracy)
                </p>
              </div>
            </div>

            <Link
              to="/review/attempt-sample-1"
              className="px-4 py-2 bg-white dark:bg-slate-900 text-amber-800 dark:text-amber-300 border border-amber-300 dark:border-amber-800 font-bold text-xs rounded-xl hover:bg-amber-100/50 transition-colors text-center shrink-0"
            >
              Review Mistakes
            </Link>
          </div>
        )}

        {/* Lessons Section */}
        <section id="practice">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-slate-900 dark:text-white font-display">
              Lessons & Quizzes
            </h3>
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">
              {quizzes.length} available
            </span>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {quizzes.map((quiz, idx) => (
              <LessonCard
                key={quiz.id}
                id={quiz.id}
                title={quiz.title}
                topic={quiz.topic}
                level={quiz.level}
                description={quiz.description}
                progressPercentage={idx === 0 ? 75 : idx === 1 ? 25 : 0}
                totalXp={quiz.totalXp}
                estimatedMinutes={quiz.estimatedMinutes}
                isActive={idx === 0}
                isCompleted={idx === 1}
              />
            ))}
          </div>
        </section>
      </div>

      {/* AI Quiz Generator Dialog */}
      <AiQuizGeneratorModal
        isOpen={isGeneratorOpen}
        onClose={() => setIsGeneratorOpen(false)}
        defaultLanguage={selectedLanguage}
      />
    </div>
  );
};
