import React, { useState } from 'react';
import { MatchingExercise as MatchingType } from '../../../types';
import { Check } from 'lucide-react';
import { sound } from '../../../lib/sound';

interface Props {
  exercise: MatchingType;
  selectedAnswer: Record<string, string>; // pairId -> selected right value
  onSelectAnswer: (matches: Record<string, string>) => void;
  disabled?: boolean;
}

export const MatchingExercise: React.FC<Props> = ({
  exercise,
  selectedAnswer = {},
  onSelectAnswer,
  disabled = false,
}) => {
  const { pairs, left_language, right_language } = exercise.payload;

  // Selected left item id waiting for a right match
  const [selectedLeftId, setSelectedLeftId] = useState<string | null>(null);

  // Shuffle right items once stably
  const [shuffledRights] = useState(() => {
    return [...pairs].sort(() => Math.random() - 0.5);
  });

  const handleLeftClick = (pairId: string) => {
    if (disabled) return;
    sound.playTap();
    if (selectedAnswer[pairId]) {
      // Unpair
      const updated = { ...selectedAnswer };
      delete updated[pairId];
      onSelectAnswer(updated);
      setSelectedLeftId(null);
    } else {
      setSelectedLeftId(pairId);
    }
  };

  const handleRightClick = (rightValue: string) => {
    if (disabled || !selectedLeftId) return;
    sound.playTap();

    // Check if this rightValue is already paired to another leftId
    const updated = { ...selectedAnswer };
    Object.keys(updated).forEach((k) => {
      if (updated[k] === rightValue) {
        delete updated[k];
      }
    });

    updated[selectedLeftId] = rightValue;
    onSelectAnswer(updated);
    setSelectedLeftId(null);
  };

  // Check if a rightValue is currently paired
  const isRightPaired = (rightValue: string) => {
    return Object.values(selectedAnswer).includes(rightValue);
  };

  return (
    <div className="w-full max-w-xl mx-auto flex flex-col gap-6">
      {/* Exercise instruction */}
      <div className="bg-slate-50 dark:bg-slate-800/60 rounded-3xl p-6 border border-slate-200/80 dark:border-slate-800 text-center">
        <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 block mb-1">
          {exercise.prompt}
        </span>
        <p className="text-lg font-bold text-slate-900 dark:text-white font-display">
          Tap an item on the left, then tap its match
        </p>
      </div>

      {/* Grid or Columns */}
      <div className="grid grid-cols-2 gap-4 sm:gap-6">
        {/* Left Column */}
        <div className="flex flex-col gap-3">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider text-center">
            {left_language || 'Source'}
          </span>
          {pairs.map((pair) => {
            const isPaired = !!selectedAnswer[pair.id];
            const isSelected = selectedLeftId === pair.id;

            return (
              <button
                key={`left-${pair.id}`}
                type="button"
                disabled={disabled}
                onClick={() => handleLeftClick(pair.id)}
                className={`w-full p-4 rounded-2xl border-2 font-semibold text-sm sm:text-base text-left transition-all duration-150 flex items-center justify-between cursor-pointer ${
                  isSelected
                    ? 'border-teal-500 bg-teal-50 dark:bg-teal-950/40 text-teal-900 dark:text-teal-100 ring-2 ring-teal-500/20'
                    : isPaired
                    ? 'border-emerald-500 bg-emerald-50/60 dark:bg-emerald-950/30 text-emerald-900 dark:text-emerald-200'
                    : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 hover:border-slate-300'
                }`}
              >
                <span>{pair.left}</span>
                {isPaired && <Check className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />}
              </button>
            );
          })}
        </div>

        {/* Right Column */}
        <div className="flex flex-col gap-3">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider text-center">
            {right_language || 'Target'}
          </span>
          {shuffledRights.map((item) => {
            const paired = isRightPaired(item.right);

            return (
              <button
                key={`right-${item.id}`}
                type="button"
                disabled={disabled || !selectedLeftId}
                onClick={() => handleRightClick(item.right)}
                className={`w-full p-4 rounded-2xl border-2 font-semibold text-sm sm:text-base text-left transition-all duration-150 flex items-center justify-between cursor-pointer ${
                  paired
                    ? 'border-emerald-500 bg-emerald-50/60 dark:bg-emerald-950/30 text-emerald-900 dark:text-emerald-200'
                    : selectedLeftId
                    ? 'border-teal-300 dark:border-teal-700 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 hover:border-teal-500 hover:bg-teal-50/30'
                    : 'border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 text-slate-400 cursor-not-allowed'
                }`}
              >
                <span>{item.right}</span>
                {paired && <Check className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};
