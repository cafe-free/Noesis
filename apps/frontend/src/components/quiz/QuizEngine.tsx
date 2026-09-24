import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Quiz, CheckAnswerResponse, MistakeReviewItem, QuizAttemptResult } from '../../types';
import { QuizHeader } from './QuizHeader';
import { ExerciseRenderer } from './ExerciseRenderer';
import { AnswerFeedback } from './AnswerFeedback';
import { QuizResult } from './QuizResult';
import { Button } from '../ui/Button';
import { checkExerciseAnswer, submitQuizAttempt } from '../../lib/api/attempts';
import { sound } from '../../lib/sound';
import { useAuth } from '../../context/AuthContext';

interface QuizEngineProps {
  quiz: Quiz;
  onExit?: () => void;
}

export const QuizEngine: React.FC<QuizEngineProps> = ({ quiz, onExit }) => {
  const navigate = useNavigate();
  const { currentUser, updateUser } = useAuth();

  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<unknown>(null);
  const [status, setStatus] = useState<'answering' | 'checking' | 'feedback' | 'completed'>('answering');
  const [feedback, setFeedback] = useState<CheckAnswerResponse | null>(null);
  const [score, setScore] = useState(0);
  const [hearts, setHearts] = useState(currentUser?.hearts ?? 5);
  const [mistakes, setMistakes] = useState<MistakeReviewItem[]>([]);
  const [quizResult, setQuizResult] = useState<QuizAttemptResult | null>(null);
  const [isSubmittingFinal, setIsSubmittingFinal] = useState(false);

  const startTimeRef = useRef<number>(Date.now());
  const exercises = quiz.exercises;
  const currentExercise = exercises[currentIndex];

  // Reset timer on fresh load
  useEffect(() => {
    startTimeRef.current = Date.now();
  }, [quiz.id]);

  // Check if answer is provided to enable CHECK button
  const isAnswerProvided = (): boolean => {
    if (!currentExercise || selectedAnswer === null || selectedAnswer === undefined) return false;

    switch (currentExercise.type) {
      case 'mcq_translation':
        return typeof selectedAnswer === 'string' && selectedAnswer.trim().length > 0;
      case 'fill_blank':
        return typeof selectedAnswer === 'string' && selectedAnswer.trim().length > 0;
      case 'word_order':
        return Array.isArray(selectedAnswer) && selectedAnswer.length > 0;
      case 'matching': {
        const matches = selectedAnswer as Record<string, string>;
        const totalNeeded = currentExercise.payload.pairs.length;
        return Object.keys(matches).length === totalNeeded;
      }
      default:
        return false;
    }
  };

  // Submit current answer to the backend evaluation API
  const handleCheck = async () => {
    if (!isAnswerProvided() || status !== 'answering') return;

    setStatus('checking');
    try {
      const response = await checkExerciseAnswer({
        quizId: quiz.id,
        exerciseId: currentExercise.id,
        userAnswer: selectedAnswer,
      });

      setFeedback(response);
      setStatus('feedback');

      if (response.isCorrect) {
        sound.playCorrect();
        setScore((prev) => prev + 1);
      } else {
        sound.playIncorrect();
        setHearts((prev) => Math.max(0, prev - 1));

        // Format user answer representation
        let userAnsStr = '';
        if (Array.isArray(selectedAnswer)) {
          userAnsStr = selectedAnswer.join(' ');
        } else if (typeof selectedAnswer === 'object' && selectedAnswer !== null) {
          userAnsStr = Object.entries(selectedAnswer as Record<string, string>)
            .map(([k, v]) => `${k}: ${v}`)
            .join(', ');
        } else {
          userAnsStr = String(selectedAnswer || '');
        }

        const newMistake: MistakeReviewItem = {
          exerciseId: currentExercise.id,
          concept: currentExercise.instruction || quiz.topic,
          prompt: currentExercise.prompt,
          userAnswer: userAnsStr,
          correctAnswer: response.correctAnswer,
          explanation: response.explanation,
        };
        setMistakes((prev) => [...prev, newMistake]);
      }
    } catch {
      setStatus('answering');
    }
  };

  // Move to next exercise or submit final attempt
  const handleContinue = async () => {
    if (currentIndex + 1 < exercises.length) {
      // Advance to next question
      setCurrentIndex((prev) => prev + 1);
      setSelectedAnswer(null);
      setFeedback(null);
      setStatus('answering');
    } else {
      // Quiz finished - Submit attempt to backend
      setIsSubmittingFinal(true);
      const timeSpent = Math.round((Date.now() - startTimeRef.current) / 1000);

      try {
        const finalResult = await submitQuizAttempt({
          quizId: quiz.id,
          quizTitle: quiz.title,
          language: quiz.language,
          totalQuestions: exercises.length,
          score,
          timeSpentSeconds: timeSpent,
          mistakes,
        });

        // Update user XP & streak in context
        if (currentUser) {
          updateUser({
            todayXp: currentUser.todayXp + finalResult.xpGained,
            totalXp: currentUser.totalXp + finalResult.xpGained,
            hearts,
          });
        }

        setQuizResult(finalResult);
        setStatus('completed');
      } finally {
        setIsSubmittingFinal(false);
      }
    }
  };

  const handleExitQuiz = () => {
    if (onExit) {
      onExit();
    } else {
      navigate('/learn');
    }
  };

  const handleRetryQuiz = () => {
    setCurrentIndex(0);
    setSelectedAnswer(null);
    setStatus('answering');
    setFeedback(null);
    setScore(0);
    setMistakes([]);
    setQuizResult(null);
    startTimeRef.current = Date.now();
  };

  // Keyboard shortcut listener for Check (Enter key)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Enter' && status === 'answering' && isAnswerProvided()) {
        e.preventDefault();
        handleCheck();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [status, selectedAnswer]);

  if (status === 'completed' && quizResult) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col justify-center">
        <QuizResult
          result={quizResult}
          onContinueLearning={() => navigate('/learn')}
          onReviewMistakes={() => navigate(`/review/${quizResult.attemptId}`)}
          onRetryQuiz={handleRetryQuiz}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white dark:bg-slate-950 flex flex-col justify-between selection:bg-teal-500/20">
      {/* 1. Header with Progress and Hearts */}
      <QuizHeader
        currentIndex={currentIndex}
        totalQuestions={exercises.length}
        hearts={hearts}
        score={score}
        onExit={handleExitQuiz}
      />

      {/* 2. Main Exercise Canvas */}
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-6 sm:py-8 flex flex-col justify-center">
        <div className="w-full transition-all duration-300">
          <ExerciseRenderer
            exercise={currentExercise}
            selectedAnswer={selectedAnswer}
            onSelectAnswer={(val) => {
              if (status === 'answering') {
                setSelectedAnswer(val);
              }
            }}
            onEnterPress={handleCheck}
            disabled={status !== 'answering'}
          />
        </div>
      </main>

      {/* 3. Bottom Control Deck or Feedback Panel */}
      <footer className="w-full">
        {status === 'feedback' && feedback ? (
          <AnswerFeedback
            isCorrect={feedback.isCorrect}
            correctAnswer={feedback.correctAnswer}
            explanation={feedback.explanation}
            xpEarned={feedback.xpEarned}
            onContinue={handleContinue}
            isLoadingNext={isSubmittingFinal}
          />
        ) : (
          <div className="border-t border-slate-200 dark:border-slate-800 bg-white/95 dark:bg-slate-900/95 py-4 px-4 sm:px-8">
            <div className="max-w-4xl mx-auto flex items-center justify-between gap-4">
              <span className="hidden sm:inline-block text-xs font-semibold text-slate-400">
                Press <kbd className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 border text-slate-600 dark:text-slate-300 font-mono text-[10px]">Enter</kbd> to check
              </span>

              <Button
                size="lg"
                variant="primary"
                onClick={handleCheck}
                disabled={!isAnswerProvided()}
                isLoading={status === 'checking'}
                className="w-full sm:w-auto min-w-[170px] ml-auto shadow-md"
              >
                CHECK
              </Button>
            </div>
          </div>
        )}
      </footer>
    </div>
  );
};
