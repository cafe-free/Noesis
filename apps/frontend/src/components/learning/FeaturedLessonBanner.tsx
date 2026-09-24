import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles } from 'lucide-react';

interface FeaturedLessonBannerProps {
  badgeText?: string;
  title?: string;
  description?: string;
  progressText?: string;
  xpReward?: string;
  quizId?: string;
}

export const FeaturedLessonBanner: React.FC<FeaturedLessonBannerProps> = ({
  badgeText = 'Next Recommended Lesson',
  title = 'Food & Drinks',
  description = 'Learn to express food preferences, order dishes at cafes, and master -er verb conjugations.',
  progressText = 'Progress: 75% complete',
  xpReward = '+40 XP',
  quizId = 'food-and-drinks',
}) => {
  return (
    <div className="bg-gradient-to-br from-teal-700 via-teal-600 to-emerald-600 rounded-3xl p-6 sm:p-7 text-white shadow-lg flex flex-col justify-between relative overflow-hidden">
      <div className="absolute -right-6 -bottom-6 w-36 h-36 bg-white/10 rounded-full blur-xl pointer-events-none" />

      <div className="relative z-10">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-white/20 text-xs font-bold mb-3 backdrop-blur-sm">
          <Sparkles className="w-3.5 h-3.5" />
          <span>{badgeText}</span>
        </div>
        <h2 className="text-2xl sm:text-3xl font-extrabold font-display mb-1.5">
          {title}
        </h2>
        <p className="text-xs sm:text-sm text-teal-100 max-w-md mb-4 leading-relaxed">
          {description}
        </p>
      </div>

      <div className="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-2 border-t border-white/20">
        <div className="flex items-center gap-2 text-xs font-medium text-teal-100">
          <span>{progressText}</span>
          <span aria-hidden="true">·</span>
          <span>{xpReward}</span>
        </div>
        <Link
          to={`/quiz/${quizId}`}
          className="px-6 py-2.5 rounded-xl bg-white text-teal-800 font-bold text-sm hover:bg-teal-50 transition-all text-center shadow-md active:scale-95"
        >
          CONTINUE
        </Link>
      </div>
    </div>
  );
};
