import React, { useEffect } from 'react';
import confetti from 'canvas-confetti';
import { Trophy, ArrowRight, RotateCcw } from 'lucide-react';
import { QuizAttemptResult } from '../../types';
import { Button } from '../ui/Button';
import { sound } from '../../lib/sound';
import { QuizResultStats } from './QuizResultStats';

interface QuizResultProps {
  result: QuizAttemptResult;
  onContinueLearning: () => void;
  onReviewMistakes: () => void;
  onRetryQuiz: () => void;
}

export const QuizResult: React.FC<QuizResultProps> = ({
  result,
  onContinueLearning,
  onReviewMistakes,
  onRetryQuiz,
}) => {
  useEffect(() => {
    sound.playVictory();

    // Trigger subtle confetti burst
    try {
      confetti({
        particleCount: 50,
        spread: 60,
        origin: { y: 0.65 },
        colors: ['#0d9488', '#10b981', '#f59e0b', '#6366f1'],
        disableForReducedMotion: true,
      });
    } catch {
      // Ignore
    }
  }, []);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  const hasMistakes = result.mistakes && result.mistakes.length > 0;

  return (
    <div className="w-full max-w-lg mx-auto py-8 px-4 flex flex-col items-center text-center animate-in fade-in zoom-in-95 duration-300">
      {/* Trophy Badge */}
      <div className="w-24 h-24 rounded-3xl bg-gradient-to-tr from-amber-400 to-yellow-300 flex items-center justify-center text-white shadow-xl shadow-amber-400/20 mb-6 animate-bounce">
        <Trophy className="w-12 h-12 fill-amber-100 text-amber-600" />
      </div>

      <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white font-display mb-2">
        {result.accuracyPercentage >= 80
          ? '🎉 Great job!'
          : result.accuracyPercentage >= 50
          ? '👏 Good effort!'
          : '💪 Keep practicing!'}
      </h2>

      <p className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-8">
        Lesson completed: <span className="font-bold text-slate-700 dark:text-slate-300">{result.quizTitle}</span>
      </p>

      {/* Main Stats Grid */}
      <QuizResultStats
        accuracyPercentage={result.accuracyPercentage}
        score={result.score}
        totalQuestions={result.totalQuestions}
        xpGained={result.xpGained}
        timeSpentSeconds={result.timeSpentSeconds}
      />

      {/* Action Buttons */}
      <div className="w-full flex flex-col gap-3">
        <Button
          size="lg"
          variant="primary"
          onClick={onContinueLearning}
          rightIcon={<ArrowRight className="w-5 h-5" />}
          className="w-full shadow-lg"
        >
          CONTINUE LEARNING
        </Button>

        {hasMistakes && (
          <Button
            size="lg"
            variant="outline"
            onClick={onReviewMistakes}
            className="w-full border-2 text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/20"
          >
            REVIEW MISTAKES ({result.mistakes.length})
          </Button>
        )}

        <button
          type="button"
          onClick={onRetryQuiz}
          className="flex items-center justify-center gap-2 py-2 text-xs font-bold text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 transition-colors cursor-pointer mt-1"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Practice this lesson again</span>
        </button>
      </div>
    </div>
  );
};
