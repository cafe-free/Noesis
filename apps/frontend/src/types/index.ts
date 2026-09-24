export type ExerciseType =
  | 'mcq_translation'
  | 'fill_blank'
  | 'word_order'
  | 'matching';

export interface BaseExercise {
  id: string;
  type: ExerciseType;
  position: number;
  prompt: string;
  instruction?: string;
  hint?: string;
}

export interface MultipleChoiceExercise extends BaseExercise {
  type: 'mcq_translation';
  payload: {
    source_text: string;
    choices: string[];
    audio_phrase?: string;
  };
}

export interface FillBlankExercise extends BaseExercise {
  type: 'fill_blank';
  payload: {
    sentence_before: string;
    sentence_after: string;
    target_translation?: string;
    placeholder?: string;
  };
}

export interface WordOrderExercise extends BaseExercise {
  type: 'word_order';
  payload: {
    source_sentence: string;
    words: string[];
    distractors?: string[];
  };
}

export interface MatchingPair {
  id: string;
  left: string; // e.g. English "apple"
  right: string; // e.g. Spanish "la manzana"
}

export interface MatchingExercise extends BaseExercise {
  type: 'matching';
  payload: {
    pairs: MatchingPair[];
    left_language: string;
    right_language: string;
  };
}

export type Exercise =
  | MultipleChoiceExercise
  | FillBlankExercise
  | WordOrderExercise
  | MatchingExercise;

export interface Quiz {
  id: string;
  title: string;
  topic: string;
  language: string;
  level: 'A1' | 'A2' | 'B1' | 'B2';
  description?: string;
  estimatedMinutes: number;
  totalXp: number;
  exercises: Exercise[];
}

export interface CheckAnswerRequest {
  quizId: string;
  exerciseId: string;
  userAnswer: unknown;
}

export interface CheckAnswerResponse {
  isCorrect: boolean;
  correctAnswer: string;
  explanation: string;
  xpEarned: number;
}

export interface MistakeReviewItem {
  exerciseId: string;
  concept: string;
  prompt: string;
  userAnswer: string;
  correctAnswer: string;
  explanation: string;
}

export interface QuizAttemptResult {
  attemptId: string;
  quizId: string;
  quizTitle: string;
  language: string;
  score: number;
  totalQuestions: number;
  accuracyPercentage: number;
  xpGained: number;
  timeSpentSeconds: number;
  mistakes: MistakeReviewItem[];
  completedAt: string;
}

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  learningLanguage: string;
  nativeLanguage: string;
  currentLevel: 'A1' | 'A2' | 'B1' | 'B2';
  streakDays: number;
  totalXp: number;
  dailyGoalXp: number;
  todayXp: number;
  hearts: number;
  maxHearts: number;
}

export interface WeakAreaItem {
  id: string;
  topic: string;
  concept: string;
  accuracyRate: number;
  mistakeCount: number;
  lastPracticed: string;
}

export interface QuizGenerationParams {
  language: string;
  level: 'A1' | 'A2' | 'B1' | 'B2';
  topic: string;
  questionCount: number;
}
