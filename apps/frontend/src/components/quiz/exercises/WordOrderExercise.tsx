import React from 'react';
import { WordOrderExercise as WordOrderType } from '../../../types';
import { RotateCcw } from 'lucide-react';
import { sound } from '../../../lib/sound';

interface Props {
  exercise: WordOrderType;
  selectedAnswer: string[];
  onSelectAnswer: (words: string[]) => void;
  disabled?: boolean;
}

export const WordOrderExercise: React.FC<Props> = ({
  exercise,
  selectedAnswer = [],
  onSelectAnswer,
  disabled = false,
}) => {
  const allWords = exercise.payload.words || [];

  // Determine available words in the bank by counting occurrences and subtracting used
  const getAvailableWordIndices = (): number[] => {
    const used = [...selectedAnswer];
    const available: number[] = [];

    allWords.forEach((word, idx) => {
      const foundIdx = used.indexOf(word);
      if (foundIdx !== -1) {
        used.splice(foundIdx, 1);
      } else {
        available.push(idx);
      }
    });

    return available;
  };

  const availableIndices = getAvailableWordIndices();

  const handleAddWord = (word: string) => {
    if (disabled) return;
    sound.playTap();
    onSelectAnswer([...selectedAnswer, word]);
  };

  const handleRemoveWord = (indexToRemove: number) => {
    if (disabled) return;
    sound.playTap();
    const next = [...selectedAnswer];
    next.splice(indexToRemove, 1);
    onSelectAnswer(next);
  };

  const handleReset = () => {
    if (disabled) return;
    sound.playTap();
    onSelectAnswer([]);
  };

  return (
    <div className="w-full max-w-xl mx-auto flex flex-col gap-6">
      {/* Target prompt */}
      <div className="bg-slate-50 dark:bg-slate-800/60 rounded-3xl p-6 border border-slate-200/80 dark:border-slate-800 text-center">
        <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 block mb-1">
          {exercise.prompt}
        </span>
        <p className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white font-display">
          "{exercise.payload.source_sentence}"
        </p>
      </div>

      {/* Answer Tray (Drop Area / Constructed Sentence) */}
      <div className="min-h-[90px] p-4 bg-white dark:bg-slate-900 border-2 border-dashed border-teal-300 dark:border-teal-800/80 rounded-2xl flex flex-wrap items-center gap-2 relative">
        {selectedAnswer.length === 0 ? (
          <span className="text-sm font-medium text-slate-400 dark:text-slate-500 italic mx-auto">
            Tap the word tiles below in order
          </span>
        ) : (
          selectedAnswer.map((word, idx) => (
            <button
              key={`selected-${idx}-${word}`}
              type="button"
              disabled={disabled}
              onClick={() => handleRemoveWord(idx)}
              className="px-4 py-2.5 bg-teal-50 dark:bg-teal-950/40 text-teal-800 dark:text-teal-200 border-2 border-teal-500 dark:border-teal-400 rounded-xl font-bold text-base shadow-sm hover:bg-rose-50 hover:text-rose-700 hover:border-rose-400 transition-all active:scale-95 cursor-pointer"
            >
              {word}
            </button>
          ))
        )}

        {selectedAnswer.length > 0 && !disabled && (
          <button
            type="button"
            onClick={handleReset}
            title="Reset words"
            className="absolute top-2 right-2 p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors cursor-pointer"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Word Bank */}
      <div className="flex flex-wrap items-center justify-center gap-2.5 p-4 bg-slate-50/70 dark:bg-slate-900/40 rounded-2xl border border-slate-200/60 dark:border-slate-800/60 min-h-[80px]">
        {allWords.map((word, idx) => {
          const isAvailable = availableIndices.includes(idx);
          return (
            <button
              key={`bank-${idx}-${word}`}
              type="button"
              disabled={!isAvailable || disabled}
              onClick={() => handleAddWord(word)}
              className={`px-4 py-2.5 rounded-xl font-bold text-base transition-all duration-150 border-b-4 select-none ${
                isAvailable
                  ? 'bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 border-2 border-slate-200 dark:border-slate-700 border-b-slate-300 dark:border-b-slate-900 hover:border-slate-300 active:border-b-0 active:translate-y-1 shadow-sm cursor-pointer'
                  : 'bg-slate-100 dark:bg-slate-800/40 text-transparent border-dashed border-2 border-slate-200/50 dark:border-slate-800/30 cursor-default pointer-events-none'
              }`}
            >
              {word}
            </button>
          );
        })}
      </div>
    </div>
  );
};
