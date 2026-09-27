import React from 'react';
import { Link } from 'react-router-dom';
import { Trophy, Clock, ArrowRight, BookOpen, CheckCircle, AlertTriangle } from 'lucide-react';
import { QuizAttemptResult } from '../../types';

interface QuizHistorySectionProps {
  attempts: QuizAttemptResult[];
  isLoading?: boolean;
}

export const QuizHistorySection: React.FC<QuizHistorySectionProps> = ({
  attempts,
  isLoading = false,
}) => {
  const formatDate = (isoString: string) => {
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return 'Recently';
    }
  };

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 sm:p-8 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-bold text-slate-900 dark:text-white font-display">
            Completed Quiz Records
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Review your past scores, AI quizzes, and mistake logs
          </p>
        </div>
        <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
          {attempts.length} {attempts.length === 1 ? 'session' : 'sessions'} recorded
        </span>
      </div>

      {isLoading ? (
        <div className="py-8 text-center text-xs font-medium text-slate-400">
          Loading past quiz results...
        </div>
      ) : attempts.length === 0 ? (
        <div className="py-10 text-center flex flex-col items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-teal-50 dark:bg-teal-950/40 text-teal-600 dark:text-teal-400 flex items-center justify-center">
            <BookOpen className="w-6 h-6" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200">
              No completed quizzes yet
            </h4>
            <p className="text-xs text-slate-400 max-w-sm mt-0.5">
              Take an interactive lesson or generate an AI quiz to track your accuracy and review past attempts.
            </p>
          </div>
          <Link
            to="/learn"
            className="mt-2 px-4 py-2 bg-teal-600 hover:bg-teal-500 text-white text-xs font-bold rounded-xl transition-all shadow-sm"
          >
            Start a Quiz
          </Link>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {attempts.map((att) => {
            const isHighAccuracy = att.accuracyPercentage >= 80;
            const isMediumAccuracy = att.accuracyPercentage >= 50;

            return (
              <div
                key={att.attemptId}
                className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-colors hover:border-slate-300 dark:hover:border-slate-700"
              >
                <div className="flex items-start gap-3">
                  <div
                    className={`p-2.5 rounded-2xl shrink-0 mt-0.5 ${
                      isHighAccuracy
                        ? 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400'
                        : isMediumAccuracy
                        ? 'bg-amber-100 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400'
                        : 'bg-rose-100 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400'
                    }`}
                  >
                    {isHighAccuracy ? (
                      <CheckCircle className="w-5 h-5" />
                    ) : (
                      <Trophy className="w-5 h-5" />
                    )}
                  </div>
                  <div>
                    <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 mb-0.5">
                      <span>{att.language}</span>
                      <span aria-hidden="true">·</span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {formatDate(att.completedAt)}
                      </span>
                    </div>
                    <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                      {att.quizTitle}
                    </h3>
                    <div className="flex items-center gap-2 mt-1">
                      <span
                        className={`text-xs font-bold px-2 py-0.5 rounded-md ${
                          isHighAccuracy
                            ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300'
                            : isMediumAccuracy
                            ? 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300'
                            : 'bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300'
                        }`}
                      >
                        {att.accuracyPercentage}% Accuracy
                      </span>
                      <span className="text-xs text-slate-500 dark:text-slate-400">
                        Score: {att.score} / {att.totalQuestions}
                      </span>
                      <span className="text-xs font-semibold text-amber-600 dark:text-amber-400">
                        +{att.xpGained} XP
                      </span>
                    </div>
                  </div>
                </div>

                <Link
                  to={`/review/${att.attemptId}`}
                  className="px-4 py-2 bg-white dark:bg-slate-900 text-teal-700 dark:text-teal-300 border border-teal-200 dark:border-teal-800 font-bold text-xs rounded-xl hover:bg-teal-50 dark:hover:bg-teal-950/30 transition-colors flex items-center justify-center gap-1.5 shrink-0 shadow-sm"
                >
                  <span>Review Answers</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
