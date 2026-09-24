import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  ArrowRight,
  Brain,
  Repeat,
  Trophy,
  CheckCircle2,
  Volume2,
  Zap,
} from 'lucide-react';
import { Button } from '../components/ui/Button';
import { sound } from '../lib/sound';

export const LandingPage: React.FC = () => {
  // Interactive Mini Preview on Landing Page
  const [selectedDemoChoice, setSelectedDemoChoice] = useState<string | null>(null);
  const [demoChecked, setDemoChecked] = useState(false);
  const [demoIsCorrect, setDemoIsCorrect] = useState(false);

  const demoChoices = [
    { text: 'Yo como manzanas frescas.', isCorrect: true },
    { text: 'Yo come manzanas frescas.', isCorrect: false },
    { text: 'Yo comen manzanas frescas.', isCorrect: false },
  ];

  const handleDemoCheck = () => {
    if (!selectedDemoChoice) return;
    const choice = demoChoices.find((c) => c.text === selectedDemoChoice);
    const correct = !!choice?.isCorrect;
    setDemoIsCorrect(correct);
    setDemoChecked(true);
    if (correct) {
      sound.playCorrect();
    } else {
      sound.playIncorrect();
    }
  };

  const handleDemoReset = () => {
    setSelectedDemoChoice(null);
    setDemoChecked(false);
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col">
      {/* 1. Hero Section */}
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

      {/* 2. Interactive Quiz Preview Widget */}
      <section id="interactive-preview" className="py-16 sm:py-20 bg-white dark:bg-slate-900/60 border-b border-slate-200 dark:border-slate-800">
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

          {/* Interactive Card */}
          <div className="bg-slate-50 dark:bg-slate-900 border-2 border-slate-200 dark:border-slate-800 rounded-3xl p-6 sm:p-8 shadow-lg">
            {/* Header / Prompt */}
            <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-200 dark:border-slate-800">
              <div>
                <span className="text-xs font-semibold text-slate-400">Spanish A1 · Food</span>
                <p className="text-lg font-bold text-slate-900 dark:text-white mt-0.5">
                  Translate: "I eat fresh apples."
                </p>
              </div>
              <button
                type="button"
                onClick={() => sound.playTap()}
                aria-label="Sound demo"
                className="p-2.5 rounded-xl bg-teal-50 dark:bg-teal-950/40 text-teal-600 dark:text-teal-400 hover:bg-teal-100 transition-colors cursor-pointer"
              >
                <Volume2 className="w-5 h-5" />
              </button>
            </div>

            {/* Options */}
            <div className="flex flex-col gap-3 mb-6">
              {demoChoices.map((choice, i) => {
                const isSelected = selectedDemoChoice === choice.text;
                return (
                  <button
                    key={choice.text}
                    type="button"
                    disabled={demoChecked}
                    onClick={() => {
                      setSelectedDemoChoice(choice.text);
                      sound.playTap();
                    }}
                    className={`w-full text-left p-4 rounded-2xl border-2 font-medium text-sm sm:text-base flex items-center justify-between transition-all cursor-pointer ${
                      isSelected
                        ? 'border-teal-500 bg-teal-50/70 dark:bg-teal-950/30 text-teal-950 dark:text-teal-100 ring-2 ring-teal-500/20'
                        : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span className="w-6 h-6 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 flex items-center justify-center text-xs font-bold">
                        {i + 1}
                      </span>
                      <span>{choice.text}</span>
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Feedback / Check Action */}
            {demoChecked ? (
              <div
                className={`p-4 rounded-2xl border ${
                  demoIsCorrect
                    ? 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-300 text-emerald-800 dark:text-emerald-200'
                    : 'bg-rose-50 dark:bg-rose-950/40 border-rose-300 text-rose-800 dark:text-rose-200'
                } flex flex-col sm:flex-row sm:items-center justify-between gap-3`}
              >
                <div>
                  <h4 className="font-bold text-sm">
                    {demoIsCorrect ? '✓ Correct! +10 XP' : '✕ Not quite: Yo como manzanas frescas.'}
                  </h4>
                  <p className="text-xs opacity-90 mt-0.5">
                    {demoIsCorrect
                      ? '"Como" is the first-person singular form of the verb comer.'
                      : '"Come" is 3rd-person. For "yo" (I), use "-o" -> "como".'}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleDemoReset}
                  className="px-4 py-2 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-xl text-xs font-bold hover:opacity-90 shrink-0 cursor-pointer"
                >
                  Try Again
                </button>
              </div>
            ) : (
              <Button
                size="lg"
                variant="primary"
                onClick={handleDemoCheck}
                disabled={!selectedDemoChoice}
                className="w-full"
              >
                CHECK ANSWER
              </Button>
            )}
          </div>
        </div>
      </section>

      {/* 3. How It Works */}
      <section className="py-16 sm:py-20 border-b border-slate-200 dark:border-slate-800">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-extrabold text-slate-900 dark:text-white font-display">
              How Verba Works
            </h2>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
              Three core pillars engineered for long-term language retention
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col gap-3">
              <div className="w-12 h-12 rounded-2xl bg-teal-50 dark:bg-teal-950/40 text-teal-600 dark:text-teal-400 flex items-center justify-center">
                <Brain className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white font-display">
                01. Adaptive Generation
              </h3>
              <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 leading-relaxed">
                Quizzes adjust dynamically. Generate targeted lessons on any topic—from ordering tapas in Madrid to negotiating train tickets in Tokyo.
              </p>
            </div>

            <div className="bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col gap-3">
              <div className="w-12 h-12 rounded-2xl bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400 flex items-center justify-center">
                <Zap className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white font-display">
                02. Instant Correction
              </h3>
              <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 leading-relaxed">
                Never wonder why an answer was wrong. Detailed grammar explanations and audio cues guide you right away without punishment.
              </p>
            </div>

            <div className="bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col gap-3">
              <div className="w-12 h-12 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
                <Repeat className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white font-display">
                03. Mistake Mastery
              </h3>
              <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 leading-relaxed">
                Every incorrect response is saved into your personal Weak Area deck for review until the concept becomes second nature.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 4. Learning Features Breakdown */}
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
            <div className="p-5 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
              <span className="text-xs font-bold text-teal-600 dark:text-teal-400">Exercise 01</span>
              <h3 className="text-base font-bold text-slate-900 dark:text-white mt-1 mb-2">
                Multiple Choice
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                Large accessible tap cards with audio playback and keyboard number triggers.
              </p>
            </div>

            <div className="p-5 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
              <span className="text-xs font-bold text-teal-600 dark:text-teal-400">Exercise 02</span>
              <h3 className="text-base font-bold text-slate-900 dark:text-white mt-1 mb-2">
                Fill-in-the-Blank
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                Inline input boxes with contextual hint callouts and seamless Enter submission.
              </p>
            </div>

            <div className="p-5 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
              <span className="text-xs font-bold text-teal-600 dark:text-teal-400">Exercise 03</span>
              <h3 className="text-base font-bold text-slate-900 dark:text-white mt-1 mb-2">
                Word Ordering
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                Clickable word tiles to construct natural grammatical sentence structures.
              </p>
            </div>

            <div className="p-5 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
              <span className="text-xs font-bold text-teal-600 dark:text-teal-400">Exercise 04</span>
              <h3 className="text-base font-bold text-slate-900 dark:text-white mt-1 mb-2">
                Vocabulary Matching
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                Connect source terms to target definitions with responsive column pairing.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 5. Bottom CTA */}
      <section className="py-20 text-center">
        <div className="max-w-xl mx-auto px-4">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white font-display mb-4">
            Ready to speak with confidence?
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mb-8">
            Join thousands of learners practicing daily Spanish, French, and Japanese.
          </p>
          <Link to="/register">
            <Button size="xl" variant="primary" rightIcon={<ArrowRight className="w-5 h-5" />}>
              CREATE FREE ACCOUNT
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto py-8 border-t border-slate-200 dark:border-slate-800 text-center text-xs text-slate-500 dark:text-slate-400">
        <div className="max-w-5xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <span>© 2026 Verba Language Platform. All rights reserved.</span>
          <div className="flex items-center gap-6">
            <Link to="/learn" className="hover:text-slate-800 dark:hover:text-slate-200">
              Dashboard
            </Link>
            <Link to="/login" className="hover:text-slate-800 dark:hover:text-slate-200">
              Sign In
            </Link>
            <Link to="/register" className="hover:text-slate-800 dark:hover:text-slate-200">
              Register
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
};
