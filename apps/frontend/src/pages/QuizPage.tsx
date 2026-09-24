import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Loader2, AlertCircle, ArrowLeft } from 'lucide-react';
import { getQuiz } from '../lib/api/quizzes';
import { Quiz } from '../types';
import { QuizEngine } from '../components/quiz/QuizEngine';
import { Button } from '../components/ui/Button';

export const QuizPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchQuiz = async () => {
    if (!id) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await getQuiz(id);
      setQuiz(data);
    } catch {
      setError('Could not load this lesson. Please check your connection or try again.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchQuiz();
  }, [id]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-white dark:bg-slate-950 flex flex-col items-center justify-center p-4">
        <div className="w-14 h-14 rounded-2xl bg-teal-50 dark:bg-teal-950/40 text-teal-600 dark:text-teal-400 flex items-center justify-center mb-4">
          <Loader2 className="w-7 h-7 animate-spin" />
        </div>
        <p className="text-base font-bold text-slate-800 dark:text-slate-200 font-display">
          Loading lesson...
        </p>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Preparing your interactive exercises
        </p>
      </div>
    );
  }

  if (error || !quiz) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col items-center justify-center p-4 text-center">
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-8 max-w-sm w-full shadow-lg flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-rose-50 dark:bg-rose-950/40 text-rose-500 flex items-center justify-center">
            <AlertCircle className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white font-display">
              Something went wrong
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              {error || "We couldn't find this quiz."}
            </p>
          </div>

          <div className="w-full flex flex-col gap-2 pt-2">
            <Button size="md" variant="primary" onClick={fetchQuiz} className="w-full">
              Try Again
            </Button>
            <Button
              size="md"
              variant="ghost"
              onClick={() => navigate('/learn')}
              leftIcon={<ArrowLeft className="w-4 h-4" />}
              className="w-full"
            >
              Back to Dashboard
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return <QuizEngine quiz={quiz} onExit={() => navigate('/learn')} />;
};
