import { apiClient } from './client';
import {
  CheckAnswerRequest,
  CheckAnswerResponse,
  QuizAttemptResult,
  MistakeReviewItem,
  ExerciseAttemptItem,
} from '../types';

export interface SubmitAttemptPayload {
  quizId: string;
  quizTitle?: string;
  language?: string;
  totalQuestions: number;
  score: number;
  timeSpentSeconds: number;
  mistakes: MistakeReviewItem[];
  answers?: Array<{
    exerciseId: string;
    prompt?: string;
    userAnswer: string;
    correctAnswer?: string;
    isCorrect: boolean;
    explanation?: string;
  }>;
}

interface BackendCheckAnswerResponse {
  is_correct: boolean;
  correct_answer: string;
  explanation: string;
  xp_earned: number;
}

export async function checkExerciseAnswer(
  params: CheckAnswerRequest
): Promise<CheckAnswerResponse> {
  const res = await apiClient.post<BackendCheckAnswerResponse>(
    '/exercise-attempts/check',
    {
      quiz_id: params.quizId,
      exercise_id: params.exerciseId,
      user_answer: params.userAnswer,
    }
  );

  return {
    isCorrect: res.is_correct,
    correctAnswer: res.correct_answer,
    explanation: res.explanation,
    xpEarned: res.xp_earned,
  };
}

function normalizeQuizAttemptResult(raw: any, fallback?: Partial<SubmitAttemptPayload>): QuizAttemptResult {
  const total = raw.total_questions ?? fallback?.totalQuestions ?? 1;
  const score = raw.score ?? raw.correct_answers ?? fallback?.score ?? 0;
  const accuracy = total > 0 ? Math.round((score / total) * 100) : 100;

  const mistakes: MistakeReviewItem[] = (raw.mistakes || fallback?.mistakes || []).map((m: any) => ({
    exerciseId: m.exerciseId || m.exercise_id || '',
    concept: m.concept || m.prompt || 'Grammar & Vocabulary',
    prompt: m.prompt || '',
    userAnswer: String(m.userAnswer || m.user_answer || m.answer || ''),
    correctAnswer: String(m.correctAnswer || m.correct_answer || ''),
    explanation: m.explanation || '',
  }));

  const allAnswers: ExerciseAttemptItem[] | undefined = (
    raw.answers ||
    raw.exercise_attempts ||
    fallback?.answers
  )?.map((a: any) => ({
    exerciseId: a.exerciseId || a.exercise_id || '',
    prompt: a.prompt || '',
    userAnswer: String(a.userAnswer || a.user_answer || a.answer || ''),
    correctAnswer: String(a.correctAnswer || a.correct_answer || ''),
    isCorrect: Boolean(a.isCorrect ?? a.is_correct),
    explanation: a.explanation,
  }));

  return {
    attemptId: raw.id || raw.attemptId || 'attempt-local',
    quizId: raw.quiz_id || raw.quizId || fallback?.quizId || '',
    quizTitle: raw.quiz_title || raw.quizTitle || fallback?.quizTitle || 'Practice Quiz',
    language: raw.language || fallback?.language || 'Spanish',
    score,
    totalQuestions: total,
    accuracyPercentage: accuracy,
    xpGained: raw.xp_gained ?? score * 10,
    timeSpentSeconds: raw.time_spent_seconds ?? fallback?.timeSpentSeconds ?? 60,
    mistakes,
    allAnswers,
    completedAt: raw.completed_at || raw.completedAt || new Date().toISOString(),
  };
}

export async function submitQuizAttempt(
  payload: SubmitAttemptPayload
): Promise<QuizAttemptResult> {
  const backendPayload = {
    quiz_id: payload.quizId,
    score: payload.score,
    total_questions: payload.totalQuestions,
    correct_answers: payload.score,
    time_spent_seconds: payload.timeSpentSeconds,
    mistakes: payload.mistakes,
    answers: payload.answers,
    completed_at: new Date().toISOString(),
  };

  const res = await apiClient.post<any>('/quiz-attempts', backendPayload);
  return normalizeQuizAttemptResult(res, payload);
}

export async function listUserAttempts(): Promise<QuizAttemptResult[]> {
  const res = await apiClient.get<any[]>('/quiz-attempts');
  return (res || []).map((item) => normalizeQuizAttemptResult(item));
}

export async function getAttemptReview(attemptId: string): Promise<QuizAttemptResult> {
  const res = await apiClient.get<any>(`/quiz-attempts/${attemptId}`);
  return normalizeQuizAttemptResult(res);
}
