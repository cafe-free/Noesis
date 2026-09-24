import React from 'react';

interface ExerciseTypeFeature {
  number: string;
  title: string;
  description: string;
}

const EXERCISE_FEATURES: ExerciseTypeFeature[] = [
  {
    number: 'Exercise 01',
    title: 'Multiple Choice',
    description: 'Large accessible tap cards with audio playback and keyboard number triggers.',
  },
  {
    number: 'Exercise 02',
    title: 'Fill-in-the-Blank',
    description: 'Inline input boxes with contextual hint callouts and seamless Enter submission.',
  },
  {
    number: 'Exercise 03',
    title: 'Word Ordering',
    description: 'Clickable word tiles to construct natural grammatical sentence structures.',
  },
  {
    number: 'Exercise 04',
    title: 'Vocabulary Matching',
    description: 'Connect source terms to target definitions with responsive column pairing.',
  },
];

export const ExerciseTypesSection: React.FC = () => {
  return (
    <section className="py-16 sm:py-20 bg-slate-100/60 dark:bg-slate-900/40 border-b border-slate-200 dark:border-slate-800">
      <div className="max-w-5xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-extrabold text-slate-900 dark:text-white font-display">
            Four Engaging Exercise Types
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
            Designed for quick taps, mobile keyboards, and deep sentence mechanics
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {EXERCISE_FEATURES.map((item) => (
            <div
              key={item.number}
              className="p-5 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm"
            >
              <span className="text-xs font-bold text-teal-600 dark:text-teal-400">
                {item.number}
              </span>
              <h3 className="text-base font-bold text-slate-900 dark:text-white mt-1 mb-2">
                {item.title}
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                {item.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
