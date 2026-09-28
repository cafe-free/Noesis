import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { RotateCcw } from 'lucide-react';
import { getAttemptReview } from '../api/attempts';
import { QuizAttemptResult } from '../types';
import { Button } from '../components/ui/Button';
import {
  MistakeCard,
  MistakeEmptyState,
  ReviewHeader,
  QuestionReviewCard,
} from '../components/review';

export const ReviewPage: React.FC = () => {
  const { attemptId } = useParams<{ attemptId: string }>();
  const navigate = useNavigate();

  const [attempt, setAttempt] = useState<QuizAttemptResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'mistakes' | 'all'>('mistakes');

  useEffect(() => {
    async function loadAttempt() {
      if (!attemptId) return;
      setIsLoading(true);
      try {
        const data = await getAttemptReview(attemptId);
        setAttempt(data);
        if (data.mistakes.length === 0 && data.allAnswers && data.allAnswers.length > 0) {
          setActiveTab('all');
        }
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
        <p className="text-sm font-semibold text-slate-500">Loading quiz review...</p>
      </div>
    );
  }

  const mistakes = attempt?.mistakes || [];
  const allAnswers = attempt?.allAnswers || [];
  const hasAllAnswers = allAnswers.length > 0;

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 pb-20">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 pt-6 sm:pt-10 flex flex-col gap-6">
        <ReviewHeader attempt={attempt} />

        {/* View Mode Toggle if all answers are recorded */}
        {hasAllAnswers && mistakes.length > 0 && (
          <div className="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-3">
            <button
              type="button"
              onClick={() => setActiveTab('mistakes')}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-colors cursor-pointer ${
                activeTab === 'mistakes'
                  ? 'bg-rose-100 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300'
                  : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
              }`}
            >
              Mistakes Only ({mistakes.length})
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('all')}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-colors cursor-pointer ${
                activeTab === 'all'
                  ? 'bg-teal-100 dark:bg-teal-950/60 text-teal-700 dark:text-teal-300'
                  : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
              }`}
            >
              All Questions ({allAnswers.length})
            </button>
          </div>
        )}

        {/* Display Content */}
        {activeTab === 'all' && hasAllAnswers ? (
          <div className="flex flex-col gap-4">
            {allAnswers.map((item, idx) => (
              <QuestionReviewCard
                key={`${item.exerciseId}-${idx}`}
                item={item}
                index={idx}
              />
            ))}
          </div>
        ) : mistakes.length === 0 ? (
          <div className="flex flex-col gap-6">
            <MistakeEmptyState />
            {hasAllAnswers && (
              <div className="flex flex-col gap-4">
                <h3 className="text-base font-bold text-slate-800 dark:text-slate-200">
                  Completed Questions & Solutions
                </h3>
                {allAnswers.map((item, idx) => (
                  <QuestionReviewCard
                    key={`${item.exerciseId}-${idx}`}
                    item={item}
                    index={idx}
                  />
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {mistakes.map((item, idx) => (
              <MistakeCard
                key={`${item.exerciseId}-${idx}`}
                item={item}
                index={idx}
              />
            ))}
          </div>
        )}

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

          <Link to="/progress" className="w-full sm:w-auto">
            <Button size="lg" variant="outline" className="w-full sm:w-auto">
              VIEW ALL QUIZ RECORDS
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};
