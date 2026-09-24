import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { RotateCcw } from 'lucide-react';
import { getAttemptReview } from '../lib/api/attempts';
import { QuizAttemptResult } from '../types';
import { Button } from '../components/ui/Button';
import { MistakeCard, MistakeEmptyState, ReviewHeader } from '../components/review';

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
        <ReviewHeader attempt={attempt} />

        {/* Mistakes List or Zero Mistakes State */}
        {mistakes.length === 0 ? (
          <MistakeEmptyState />
        ) : (
          <div className="flex flex-col gap-4">
            {mistakes.map((item, idx) => (
              <MistakeCard
                key={`${item.exerciseId}-${idx}`}
                item={item}
                index={idx}
              />
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
