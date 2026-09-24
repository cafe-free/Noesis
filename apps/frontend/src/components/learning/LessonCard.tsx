import React from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, CheckCircle, Clock, Sparkles, ArrowRight } from 'lucide-react';
import { ProgressBar } from '../ui/ProgressBar';

interface LessonCardProps {
  id: string;
  title: string;
  topic: string;
  level: string;
  description?: string;
  progressPercentage: number;
  totalXp: number;
  estimatedMinutes: number;
  isCompleted?: boolean;
  isActive?: boolean;
}

export const LessonCard: React.FC<LessonCardProps> = ({
  id,
  title,
  topic,
  level,
  description,
  progressPercentage,
  totalXp,
  estimatedMinutes,
  isCompleted = false,
  isActive = false,
}) => {
  return (
    <div
      className={`bg-white dark:bg-slate-900 border-2 rounded-3xl p-6 transition-all duration-200 shadow-sm flex flex-col justify-between gap-5 ${
        isActive
          ? 'border-teal-500 ring-2 ring-teal-500/10 dark:border-teal-400'
          : 'border-slate-200/80 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700'
      }`}
    >
      <div>
        {/* Unboxed Metadata Header */}
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 dark:text-slate-400 mb-2">
          <span>{level}</span>
          <span aria-hidden="true">·</span>
          <span>{topic}</span>
          <span aria-hidden="true">·</span>
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3 text-slate-400" />
            <span>{estimatedMinutes} min</span>
          </span>
          <span aria-hidden="true">·</span>
          <span className="flex items-center gap-1 text-teal-600 dark:text-teal-400">
            <Sparkles className="w-3 h-3" />
            <span>+{totalXp} XP</span>
          </span>
        </div>

        {/* Title */}
        <h3 className="text-xl font-bold text-slate-900 dark:text-white font-display mb-1.5 flex items-center justify-between">
          <span>{title}</span>
          {isCompleted && (
            <CheckCircle className="w-5 h-5 text-emerald-500 shrink-0" />
          )}
        </h3>

        {description && (
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 line-clamp-2">
            {description}
          </p>
        )}
      </div>

      <div>
        <div className="flex justify-between items-center text-xs font-semibold mb-1.5 text-slate-500 dark:text-slate-400">
          <span>Completion</span>
          <span className="tabular-nums">{progressPercentage}%</span>
        </div>
        <ProgressBar
          value={progressPercentage}
          height="sm"
          color={isCompleted ? 'emerald' : 'teal'}
          className="mb-4"
        />

        <Link
          to={`/quiz/${id}`}
          className={`w-full py-3 px-4 rounded-2xl font-bold text-sm flex items-center justify-center gap-2 transition-all duration-150 active:scale-[0.98] select-none ${
            isCompleted
              ? 'bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200'
              : 'bg-teal-600 hover:bg-teal-500 active:bg-teal-700 text-white shadow-md shadow-teal-600/20 border-b-4 border-teal-700 active:border-b-0 active:translate-y-1'
          }`}
        >
          <span>{isCompleted ? 'Practice Again' : isActive ? 'CONTINUE' : 'START'}</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
};
