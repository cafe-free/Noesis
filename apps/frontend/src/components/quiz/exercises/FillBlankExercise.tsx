import React, { useRef, useEffect } from 'react';
import { FillBlankExercise as FillBlankType } from '../../../types';
import { Lightbulb } from 'lucide-react';

interface Props {
  exercise: FillBlankType;
  selectedAnswer: string;
  onSelectAnswer: (answer: string) => void;
  onEnterPress?: () => void;
  disabled?: boolean;
}

export const FillBlankExercise: React.FC<Props> = ({
  exercise,
  selectedAnswer,
  onSelectAnswer,
  onEnterPress,
  disabled = false,
}) => {
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Focus input on load
    if (!disabled && inputRef.current) {
      inputRef.current.focus();
    }
  }, [exercise.id, disabled]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && selectedAnswer.trim() && onEnterPress) {
      e.preventDefault();
      onEnterPress();
    }
  };

  return (
    <div className="w-full max-w-xl mx-auto flex flex-col gap-6">
      {/* Target Translation / Prompt */}
      <div className="bg-slate-50 dark:bg-slate-800/60 rounded-3xl p-6 border border-slate-200/80 dark:border-slate-800 text-center">
        <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 block mb-1">
          {exercise.prompt}
        </span>
        {exercise.payload.target_translation && (
          <p className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white font-display mb-1">
            "{exercise.payload.target_translation}"
          </p>
        )}
      </div>

      {/* Sentence with Fill-in-Blank */}
      <div className="bg-white dark:bg-slate-900 border-2 border-slate-200 dark:border-slate-800 rounded-3xl p-6 sm:p-8 shadow-sm flex flex-col items-center gap-6">
        <div className="flex flex-wrap items-center justify-center gap-2 text-xl sm:text-2xl font-medium text-slate-800 dark:text-slate-200 leading-relaxed">
          {exercise.payload.sentence_before && (
            <span>{exercise.payload.sentence_before}</span>
          )}

          <div className="relative inline-block min-w-[140px] max-w-[200px]">
            <input
              ref={inputRef}
              type="text"
              value={selectedAnswer || ''}
              disabled={disabled}
              placeholder={exercise.payload.placeholder || 'Type answer...'}
              onChange={(e) => onSelectAnswer(e.target.value)}
              onKeyDown={handleKeyDown}
              className="w-full px-3 py-1.5 text-center text-xl sm:text-2xl font-bold text-teal-700 dark:text-teal-300 bg-teal-50 dark:bg-teal-950/40 border-b-4 border-teal-500 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500/30 transition-all placeholder:text-slate-400 placeholder:font-normal placeholder:text-base"
              aria-label="Missing word"
            />
          </div>

          {exercise.payload.sentence_after && (
            <span>{exercise.payload.sentence_after}</span>
          )}
        </div>

        {exercise.hint && (
          <div className="flex items-center gap-2 text-xs font-medium text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/30 px-3.5 py-1.5 rounded-full border border-amber-200 dark:border-amber-900/50">
            <Lightbulb className="w-3.5 h-3.5 shrink-0" />
            <span>Hint: {exercise.hint}</span>
          </div>
        )}
      </div>
    </div>
  );
};
