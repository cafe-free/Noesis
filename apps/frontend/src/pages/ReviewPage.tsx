import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, BookOpen, CheckCircle, RotateCcw, Sparkles } from 'lucide-react';
import { getAttemptReview } from '../lib/api/attempts';
import { QuizAttemptResult } from '../types';
import { Button } from '../components/ui/Button';

export const ReviewPage: React.FC = () => {
  const { attemptId } = useParams<{ attemptId: string }>();
  const navigate = useNavigate();

  const [attempt, setAttempt] = useState<QuizAttemptResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadAttempt() {
      if (!attemptId) return;
      setIsLoading(true);
      try {
        const data = await getAttemptReview(attemptId);
        setAttempt(data);
      } catch {
        // Fallback
      } finally {
        setIsLoading(false);
      }
    }
    loadAttempt();
  }, [attemptId]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center p-4">
        <p className="text-sm font-semibold text-slate-500">Loading mistake review...</p>
      </div>
    );
  }

  const mistakes = attempt?.mistakes || [];

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 pb-20">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 pt-6 sm:pt-10 flex flex-col gap-6">
        {/* Top Back Nav */}
        <div className="flex items-center justify-between">
          <Link
            to="/learn"
            className="inline-flex items-center gap-2 text-xs font-bold text-slate-600 dark:text-slate-300 hover:text-teal-600 dark:hover:text-teal-400 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Dashboard</span>
          </Link>

          {attempt && (
            <span className="text-xs font-semibold text-slate-400">
              Score: {attempt.score} / {attempt.totalQuestions} ({attempt.accuracyPercentage}%)
            </span>
          )}
        </div>

        {/* Title & Introduction */}
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white font-display mb-1">
            Review Weak Areas
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
            Mistakes are how our brains cement patterns. Study the grammatical rules below to retain them next time.
          </p>
        </div>

        {/* Mistakes List or Zero Mistakes State */}
        {mistakes.length === 0 ? (
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-8 text-center flex flex-col items-center gap-4 shadow-sm">
            <div className="w-14 h-14 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-500 flex items-center justify-center">
              <CheckCircle className="w-8 h-8" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white font-display">
                No mistakes in this attempt!
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-sm">
                You aced every exercise with 100% precision. Keep practicing new lessons to expand your vocabulary.
              </p>
            </div>
            <Link to="/learn" className="mt-2">
              <Button size="md" variant="primary">
                Return to Dashboard
              </Button>
            </Link>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {mistakes.map((item, idx) => (
              <div
                key={`${item.exerciseId}-${idx}`}
                className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm flex flex-col gap-4"
              >
                {/* Concept Header */}
                <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
                  <span className="text-xs font-bold text-rose-600 dark:text-rose-400">
                    {idx + 1}. {item.concept}
                  </span>
                  <span className="text-xs text-slate-400">Practice Card</span>
                </div>

                {/* Prompt */}
                <div>
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                    Question Prompt
                  </span>
                  <p className="text-base font-bold text-slate-800 dark:text-slate-100 mt-0.5">
                    {item.prompt}
                  </p>
                </div>

                {/* Comparison Box */}
                <div className="grid sm:grid-cols-2 gap-3 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-200/60 dark:border-slate-700/60">
                  <div>
                    <span className="text-xs font-bold text-rose-600 dark:text-rose-400 block mb-1">
                      You answered:
                    </span>
                    <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 font-mono">
                      {item.userAnswer || '(blank)'}
                    </p>
                  </div>
                  <div>
                    <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 block mb-1">
                      Correct answer:
                    </span>
                    <p className="text-sm font-bold text-slate-900 dark:text-white font-mono">
                      {item.correctAnswer}
                    </p>
                  </div>
                </div>

                {/* Explanation */}
                {item.explanation && (
                  <div className="p-3.5 bg-teal-50/70 dark:bg-teal-950/20 border border-teal-200/60 dark:border-teal-900/50 rounded-2xl">
                    <span className="text-xs font-bold text-teal-800 dark:text-teal-300 block mb-1">
                      Grammar & Vocabulary Note:
                    </span>
                    <p className="text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                      {item.explanation}
                    </p>
                  </div>
                )}
              </div>
            ))}

            {/* Bottom Actions */}
            <div className="pt-4 flex flex-col sm:flex-row items-center justify-between gap-4">
              <Button
                size="lg"
                variant="primary"
                onClick={() => {
                  if (attempt?.quizId) {
                    navigate(`/quiz/${attempt.quizId}`);
                  } else {
                    navigate('/learn');
                  }
                }}
                leftIcon={<RotateCcw className="w-4 h-4" />}
                className="w-full sm:w-auto"
              >
                PRACTICE THIS LESSON AGAIN
              </Button>

              <Link to="/learn" className="w-full sm:w-auto">
                <Button size="lg" variant="outline" className="w-full sm:w-auto">
                  CONTINUE TO DASHBOARD
                </Button>
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
