import React from 'react';
import { Quiz } from '../../types';
import { LessonCard } from './LessonCard';

interface LessonGridProps {
  quizzes: Quiz[];
}

export const LessonGrid: React.FC<LessonGridProps> = ({ quizzes }) => {
  return (
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
  );
};
