import React, { useEffect } from 'react';
import { CheckCircle2, XCircle, Sparkles } from 'lucide-react';
import { Button } from '../ui/Button';

interface AnswerFeedbackProps {
  isCorrect: boolean;
  correctAnswer: string;
  explanation?: string;
  xpEarned: number;
  onContinue: () => void;
  isLoadingNext?: boolean;
}

export const AnswerFeedback: React.FC<AnswerFeedbackProps> = ({
  isCorrect,
  correctAnswer,
  explanation,
  xpEarned,
  onContinue,
  isLoadingNext = false,
}) => {
  // Listen for Enter key to continue
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        onContinue();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onContinue]);

  return (
    <div
      role="region"
      aria-label="Answer feedback"
      className={`w-full border-t-2 transition-colors duration-200 py-6 px-4 sm:px-8 ${
        isCorrect
          ? 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-300 dark:border-emerald-800'
          : 'bg-rose-50 dark:bg-rose-950/40 border-rose-300 dark:border-rose-800'
      }`}
    >
      <div className="max-w-4xl mx-auto flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        {/* Left: Feedback text & icon */}
        <div className="flex items-start gap-4">
          <div className="mt-1">
            {isCorrect ? (
              <CheckCircle2 className="w-8 h-8 text-emerald-600 dark:text-emerald-400 fill-emerald-100 dark:fill-emerald-950 animate-bounce" />
            ) : (
              <XCircle className="w-8 h-8 text-rose-600 dark:text-rose-400 fill-rose-100 dark:fill-rose-950" />
            )}
          </div>

          <div className="flex flex-col gap-1">
            <div className="flex items-center gap-2">
              <h4
                className={`text-xl font-bold font-display ${
                  isCorrect
                    ? 'text-emerald-800 dark:text-emerald-300'
                    : 'text-rose-800 dark:text-rose-300'
                }`}
              >
                {isCorrect ? '✓ Correct!' : '✕ Not quite'}
              </h4>
              {isCorrect && xpEarned > 0 && (
                <span className="flex items-center gap-1 text-xs font-extrabold text-emerald-700 dark:text-emerald-300 bg-emerald-200/60 dark:bg-emerald-900/60 px-2 py-0.5 rounded-full">
                  <Sparkles className="w-3.5 h-3.5" />
                  +{xpEarned} XP
                </span>
              )}
            </div>

            {!isCorrect && (
              <div className="text-sm font-medium text-slate-800 dark:text-slate-200">
                <span className="text-slate-500 dark:text-slate-400">Correct answer: </span>
                <span className="font-bold text-rose-900 dark:text-rose-200">
                  {correctAnswer}
                </span>
              </div>
            )}

            {explanation && (
              <p
                className={`text-xs sm:text-sm font-medium leading-relaxed max-w-xl ${
                  isCorrect
                    ? 'text-emerald-700 dark:text-emerald-400'
                    : 'text-rose-700 dark:text-rose-400'
                }`}
              >
                {explanation}
              </p>
            )}

            {!isCorrect && (
              <p className="text-xs font-semibold text-rose-500 dark:text-rose-400 italic">
                Keep practicing!
              </p>
            )}
          </div>
        </div>

        {/* Right: Continue button */}
        <div className="flex justify-end pt-2 sm:pt-0">
          <Button
            size="lg"
            variant={isCorrect ? 'success' : 'danger'}
            onClick={onContinue}
            isLoading={isLoadingNext}
            className="w-full sm:w-auto min-w-[170px]"
          >
            CONTINUE
          </Button>
        </div>
      </div>
    </div>
  );
};
