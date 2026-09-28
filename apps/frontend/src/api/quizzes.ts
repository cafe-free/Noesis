import { apiClient } from './client';
import { Quiz, Exercise, QuizGenerationParams } from '../types';

interface BackendExercise {
  id: string;
  quiz_id?: string;
  type: string;
  position: number;
  prompt: string;
  payload: Record<string, any>;
}

interface BackendQuiz {
  id: string;
  title: string;
  topic: string;
  language: string;
  level: string;
  description?: string;
  estimatedMinutes?: number;
  totalXp?: number;
  exercises?: BackendExercise[];
}

function normalizeExercise(backendEx: BackendExercise): Exercise {
  const base = {
    id: backendEx.id,
    position: backendEx.position,
    prompt: backendEx.prompt,
    instruction: backendEx.payload?.instruction,
    hint: backendEx.payload?.hint,
  };

  switch (backendEx.type) {
    case 'multiple_choice':
    case 'mcq_translation':
      return {
        ...base,
        type: 'mcq_translation',
        payload: {
          source_text: backendEx.prompt,
          choices: backendEx.payload?.options || backendEx.payload?.choices || [],
          audio_phrase: backendEx.payload?.audio_phrase,
        },
      };

    case 'fill_in_blank':
    case 'fill_blank':
      return {
        ...base,
        type: 'fill_blank',
        payload: {
          sentence_before: backendEx.payload?.sentence_before || backendEx.prompt || '',
          sentence_after: backendEx.payload?.sentence_after || '',
          target_translation: backendEx.payload?.target_translation,
          placeholder: backendEx.payload?.placeholder,
        },
      };

    case 'word_order':
      return {
        ...base,
        type: 'word_order',
        payload: {
          source_sentence: backendEx.prompt,
          words: backendEx.payload?.tokens || backendEx.payload?.words || [],
          distractors: backendEx.payload?.distractors,
        },
      };

    case 'matching':
      const leftItems = backendEx.payload?.left_items || [];
      const rightItems = backendEx.payload?.right_items || [];
      const rawPairs = backendEx.payload?.pairs || [];
      let pairs = rawPairs.map((p: any, idx: number) => ({
        id: p.id || String(idx + 1),
        left: p.left || '',
        right: p.right || '',
      }));

      if (pairs.length === 0 && leftItems.length > 0) {
        pairs = leftItems.map((left: string, idx: number) => ({
          id: String(idx + 1),
          left,
          right: rightItems[idx] || '',
        }));
      }

      return {
        ...base,
        type: 'matching',
        payload: {
          pairs,
          left_language: backendEx.payload?.left_language || 'English',
          right_language: backendEx.payload?.right_language || 'Target',
        },
      };

    default:
      return {
        ...base,
        type: 'mcq_translation',
        payload: {
          source_text: backendEx.prompt,
          choices: backendEx.payload?.options || backendEx.payload?.choices || [],
        },
      };
  }
}

function normalizeQuiz(backendQuiz: BackendQuiz): Quiz {
  const exercises = (backendQuiz.exercises || []).map(normalizeExercise);
  return {
    id: backendQuiz.id,
    title: backendQuiz.title,
    topic: backendQuiz.topic,
    language: backendQuiz.language,
    level: (backendQuiz.level as 'A1' | 'A2' | 'B1' | 'B2') || 'A1',
    description: backendQuiz.description,
    estimatedMinutes: backendQuiz.estimatedMinutes || Math.max(3, Math.ceil(exercises.length * 1.5)),
    totalXp: backendQuiz.totalXp || exercises.length * 10,
    exercises,
  };
}

export async function listQuizzes(params?: {
  language?: string;
  level?: string;
  topic?: string;
}): Promise<Quiz[]> {
  const res = await apiClient.get<BackendQuiz[]>('/quizzes', { params });
  return (res || []).map(normalizeQuiz);
}

export async function getQuiz(id: string): Promise<Quiz> {
  const res = await apiClient.get<BackendQuiz>(`/quizzes/${id}`);
  return normalizeQuiz(res);
}

export async function startQuizGenerationJob(
  params: QuizGenerationParams
): Promise<{ jobId: string }> {
  const res = await apiClient.post<{ id: string }>('/generation-jobs', {
    language: params.language,
    level: params.level,
    topic: params.topic,
    count: params.questionCount,
  });
  return { jobId: res.id };
}

export async function getQuizGenerationJob(
  jobId: string,
  _params?: QuizGenerationParams
): Promise<{ quizId?: string; status?: string }> {
  const res = await apiClient.get<{ id: string; status: string; quiz_id?: string }>(
    `/generation-jobs/${jobId}`
  );
  return {
    quizId: res.quiz_id,
    status: res.status,
  };
}
