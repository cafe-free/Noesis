import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, ArrowRight } from 'lucide-react';
import { Button } from '../ui/Button';

export const HeroSection: React.FC = () => {
  return (
    <section className="relative pt-12 pb-16 sm:pt-20 sm:pb-24 overflow-hidden border-b border-slate-200 dark:border-slate-800">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-50 dark:bg-teal-950/40 border border-teal-200 dark:border-teal-800/60 text-xs font-bold text-teal-700 dark:text-teal-300 mb-6">
          <Sparkles className="w-3.5 h-3.5" />
          <span>AI-Powered Adaptive Language Learning</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold text-slate-900 dark:text-white font-display tracking-tight max-w-3xl mx-auto mb-6 text-balance leading-tight">
          Master languages with playful, bite-sized quizzes.
        </h1>

        <p className="text-base sm:text-xl text-slate-600 dark:text-slate-300 max-w-2xl mx-auto mb-10 leading-relaxed">
          Personalized practice engine tailored to your weak spots. Interactive word puzzles, instant feedback, and continuous momentum.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link to="/learn">
            <Button
              size="xl"
              variant="primary"
              rightIcon={<ArrowRight className="w-5 h-5" />}
              className="w-full sm:w-auto shadow-xl shadow-teal-600/20"
            >
              START LEARNING FREE
            </Button>
          </Link>
          <a href="#interactive-preview">
            <Button
              size="xl"
              variant="outline"
              className="w-full sm:w-auto"
            >
              TRY LIVE PREVIEW
            </Button>
          </a>
        </div>
      </div>
    </section>
  );
};
