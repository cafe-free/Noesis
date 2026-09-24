import React from 'react';
import { Exercise } from '../../types';
import { MultipleChoiceExercise } from './exercises/MultipleChoiceExercise';
import { FillBlankExercise } from './exercises/FillBlankExercise';
import { WordOrderExercise } from './exercises/WordOrderExercise';
import { MatchingExercise } from './exercises/MatchingExercise';

interface ExerciseRendererProps {
  exercise: Exercise;
  selectedAnswer: unknown;
  onSelectAnswer: (answer: unknown) => void;
  onEnterPress?: () => void;
  disabled?: boolean;
}

export const ExerciseRenderer: React.FC<ExerciseRendererProps> = ({
  exercise,
  selectedAnswer,
  onSelectAnswer,
  onEnterPress,
  disabled = false,
}) => {
  switch (exercise.type) {
    case 'mcq_translation':
      return (
        <MultipleChoiceExercise
          exercise={exercise}
          selectedAnswer={(selectedAnswer as string) || null}
          onSelectAnswer={onSelectAnswer}
          disabled={disabled}
        />
      );

    case 'fill_blank':
      return (
        <FillBlankExercise
          exercise={exercise}
          selectedAnswer={(selectedAnswer as string) || ''}
          onSelectAnswer={onSelectAnswer}
          onEnterPress={onEnterPress}
          disabled={disabled}
        />
      );

    case 'word_order':
      return (
        <WordOrderExercise
          exercise={exercise}
          selectedAnswer={(selectedAnswer as string[]) || []}
          onSelectAnswer={onSelectAnswer}
          disabled={disabled}
        />
      );

    case 'matching':
      return (
        <MatchingExercise
          exercise={exercise}
          selectedAnswer={(selectedAnswer as Record<string, string>) || {}}
          onSelectAnswer={onSelectAnswer}
          disabled={disabled}
        />
      );

    default:
      return (
        <div className="p-8 text-center text-slate-500">
          Unsupported exercise format.
        </div>
      );
  }
};
