import React, { useEffect } from 'react';
import { MultipleChoiceExercise as MCQType } from '../../../types';
import { Volume2 } from 'lucide-react';
import { sound } from '../../../lib/sound';

interface Props {
  exercise: MCQType;
  selectedAnswer: string | null;
  onSelectAnswer: (answer: string) => void;
  disabled?: boolean;
}

export const MultipleChoiceExercise: React.FC<Props> = ({
  exercise,
  selectedAnswer,
  onSelectAnswer,
  disabled = false,
}) => {
  const choices = exercise.payload.choices || [];

  // Keyboard shortcut listener (1, 2, 3, 4)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (disabled) return;
      const keyNum = parseInt(e.key, 10);
      if (keyNum >= 1 && keyNum <= choices.length) {
        onSelectAnswer(choices[keyNum - 1]);
        sound.playTap();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [choices, disabled, onSelectAnswer]);

  return (
    <div className="w-full max-w-xl mx-auto flex flex-col gap-6">
      {/* Source Prompt Box */}
      <div className="bg-slate-50 dark:bg-slate-800/60 rounded-3xl p-6 border border-slate-200/80 dark:border-slate-800 flex items-center justify-between gap-4">
        <div>
          <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 block mb-1">
            {exercise.prompt}
          </span>
          <p className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white font-display">
            "{exercise.payload.source_text}"
          </p>
        </div>
        <button
          type="button"
          onClick={() => sound.playTap()}
          aria-label="Listen to pronunciation"
          className="p-3 rounded-2xl bg-teal-50 dark:bg-teal-950/40 text-teal-600 dark:text-teal-400 hover:bg-teal-100 transition-colors shrink-0 cursor-pointer"
        >
          <Volume2 className="w-6 h-6" />
        </button>
      </div>

      {exercise.instruction && (
        <p className="text-sm font-medium text-slate-500 dark:text-slate-400 text-center">
          {exercise.instruction}
        </p>
      )}

      {/* Choice Options */}
      <div className="flex flex-col gap-3" role="radiogroup" aria-label="Answer options">
        {choices.map((choice, index) => {
          const isSelected = selectedAnswer === choice;
          return (
            <button
              key={choice}
              type="button"
              role="radio"
              aria-checked={isSelected}
              disabled={disabled}
              onClick={() => {
                onSelectAnswer(choice);
                sound.playTap();
              }}
              className={`w-full text-left p-4 sm:p-5 rounded-2xl border-2 transition-all duration-150 flex items-center justify-between group cursor-pointer ${
                isSelected
                  ? 'border-teal-500 bg-teal-50/70 dark:bg-teal-950/30 text-teal-950 dark:text-teal-100 shadow-md ring-2 ring-teal-500/20 translate-x-1'
                  : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 hover:border-slate-300 dark:hover:border-slate-700 hover:bg-slate-50/50'
              } ${disabled ? 'opacity-80 pointer-events-none' : ''}`}
            >
              <div className="flex items-center gap-3.5">
                <span
                  className={`w-7 h-7 rounded-xl flex items-center justify-center text-xs font-bold border transition-colors ${
                    isSelected
                      ? 'bg-teal-500 border-teal-500 text-white'
                      : 'border-slate-300 dark:border-slate-700 text-slate-500 group-hover:border-slate-400'
                  }`}
                >
                  {index + 1}
                </span>
                <span className="text-base sm:text-lg font-medium">{choice}</span>
              </div>
              <div
                className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors ${
                  isSelected
                    ? 'border-teal-500 bg-teal-500'
                    : 'border-slate-300 dark:border-slate-700'
                }`}
              >
                {isSelected && <div className="w-2 h-2 rounded-full bg-white" />}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
