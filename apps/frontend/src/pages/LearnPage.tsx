import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { DailyGoal } from '../components/learning/DailyGoal';
import { AiQuizGeneratorModal } from '../components/learning/AiQuizGeneratorModal';
import { LearnHeader } from '../components/learning/LearnHeader';
import { FeaturedLessonBanner } from '../components/learning/FeaturedLessonBanner';
import { WeakAreasBanner } from '../components/learning/WeakAreasBanner';
import { LessonGrid } from '../components/learning/LessonGrid';
import { listQuizzes } from '../lib/api/quizzes';
import { getWeaknesses } from '../lib/api/progress';
import { Quiz, WeakAreaItem } from '../types';

export const LearnPage: React.FC = () => {
  const { currentUser } = useAuth();
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [weaknesses, setWeaknesses] = useState<WeakAreaItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGeneratorOpen, setIsGeneratorOpen] = useState(false);
  const selectedLanguage = currentUser?.learningLanguage || 'Spanish';

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

  const userName = currentUser?.name || 'Learner';

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 pb-24 md:pb-16">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 pt-6 sm:pt-10 flex flex-col gap-8">
        {/* Top Greeting & Language Info & AI Button */}
        <LearnHeader
          userName={userName}
          selectedLanguage={selectedLanguage}
          currentLevel={currentUser?.currentLevel || 'A1'}
          totalXp={currentUser?.totalXp || 380}
          onOpenGenerator={() => setIsGeneratorOpen(true)}
        />

        {/* Dashboard Grid: Daily Goal & Continue Hero */}
        <div className="grid md:grid-cols-3 gap-6">
          <div className="md:col-span-1">
            <DailyGoal
              todayXp={currentUser?.todayXp || 12}
              goalXp={currentUser?.dailyGoalXp || 20}
              streakDays={currentUser?.streakDays || 6}
            />
          </div>

          <div className="md:col-span-2">
            <FeaturedLessonBanner
              title="Food & Drinks"
              description="Learn to express food preferences, order dishes at cafes, and master -er verb conjugations."
              quizId="food-and-drinks"
            />
          </div>
        </div>

        {/* Weak Areas Banner / Quick Practice */}
        <WeakAreasBanner weaknesses={weaknesses} />

        {/* Lessons Section */}
        <LessonGrid quizzes={quizzes} />
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
