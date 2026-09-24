import React from 'react';
import { InteractiveCard } from './InteractiveCard';

export const InteractivePreviewSection: React.FC = () => {
  return (
    <section
      id="interactive-preview"
      className="py-16 sm:py-20 bg-white dark:bg-slate-900/60 border-b border-slate-200 dark:border-slate-800"
    >
      <div className="max-w-2xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-8">
          <span className="text-xs font-extrabold uppercase tracking-wider text-teal-600 dark:text-teal-400">
            Interactive Test Drive
          </span>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white font-display mt-1">
            Try a sample exercise right now
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Experience the instant tactile feedback that keeps learners engaged
          </p>
        </div>

        <InteractiveCard />
      </div>
    </section>
  );
};
