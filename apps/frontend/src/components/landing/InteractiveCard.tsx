import React, { useState } from 'react';
import { Volume2 } from 'lucide-react';
import { Button } from '../ui/Button';
import { sound } from '../../lib/sound';

export interface DemoChoice {
  text: string;
  isCorrect: boolean;
}

const DEFAULT_CHOICES: DemoChoice[] = [
  { text: 'Yo como manzanas frescas.', isCorrect: true },
  { text: 'Yo come manzanas frescas.', isCorrect: false },
  { text: 'Yo comen manzanas frescas.', isCorrect: false },
];

export interface InteractiveCardProps {
  promptContext?: string;
  promptQuestion?: string;
  choices?: DemoChoice[];
}

export const InteractiveCard: React.FC<InteractiveCardProps> = ({
  promptContext = 'Spanish A1 · Food',
  promptQuestion = 'Translate: "I eat fresh apples."',
  choices = DEFAULT_CHOICES,
}) => {
  const [selectedChoice, setSelectedChoice] = useState<string | null>(null);
  const [checked, setChecked] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);

  const handleCheck = () => {
    if (!selectedChoice) return;
    const choice = choices.find((c) => c.text === selectedChoice);
    const correct = !!choice?.isCorrect;
    setIsCorrect(correct);
    setChecked(true);
    if (correct) {
      sound.playCorrect();
    } else {
      sound.playIncorrect();
    }
  };

  const handleReset = () => {
    setSelectedChoice(null);
    setChecked(false);
  };

  return (
    <div className="bg-slate-50 dark:bg-slate-900 border-2 border-slate-200 dark:border-slate-800 rounded-3xl p-6 sm:p-8 shadow-lg">
      {/* Header / Prompt */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <span className="text-xs font-semibold text-slate-400">{promptContext}</span>
          <p className="text-lg font-bold text-slate-900 dark:text-white mt-0.5">
            {promptQuestion}
          </p>
        </div>
        <button
          type="button"
          onClick={() => sound.playTap()}
          aria-label="Sound demo"
          className="p-2.5 rounded-xl bg-teal-50 dark:bg-teal-950/40 text-teal-600 dark:text-teal-400 hover:bg-teal-100 transition-colors cursor-pointer"
        >
          <Volume2 className="w-5 h-5" />
        </button>
      </div>

      {/* Options */}
      <div className="flex flex-col gap-3 mb-6">
        {choices.map((choice, i) => {
          const isSelected = selectedChoice === choice.text;
          return (
            <button
              key={choice.text}
              type="button"
              disabled={checked}
              onClick={() => {
                setSelectedChoice(choice.text);
                sound.playTap();
              }}
              className={`w-full text-left p-4 rounded-2xl border-2 font-medium text-sm sm:text-base flex items-center justify-between transition-all cursor-pointer ${
                isSelected
                  ? 'border-teal-500 bg-teal-50/70 dark:bg-teal-950/30 text-teal-950 dark:text-teal-100 ring-2 ring-teal-500/20'
                  : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 hover:border-slate-300'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className="w-6 h-6 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 flex items-center justify-center text-xs font-bold">
                  {i + 1}
                </span>
                <span>{choice.text}</span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Feedback / Check Action */}
      {checked ? (
        <div
          className={`p-4 rounded-2xl border ${
            isCorrect
              ? 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-300 text-emerald-800 dark:text-emerald-200'
              : 'bg-rose-50 dark:bg-rose-950/40 border-rose-300 text-rose-800 dark:text-rose-200'
          } flex flex-col sm:flex-row sm:items-center justify-between gap-3`}
        >
          <div>
            <h4 className="font-bold text-sm">
              {isCorrect ? '✓ Correct! +10 XP' : '✕ Not quite: Yo como manzanas frescas.'}
            </h4>
            <p className="text-xs opacity-90 mt-0.5">
              {isCorrect
                ? '"Como" is the first-person singular form of the verb comer.'
                : '"Come" is 3rd-person. For "yo" (I), use "-o" -> "como".'}
            </p>
          </div>
          <button
            type="button"
            onClick={handleReset}
            className="px-4 py-2 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-xl text-xs font-bold hover:opacity-90 shrink-0 cursor-pointer"
          >
            Try Again
          </button>
        </div>
      ) : (
        <Button
          size="lg"
          variant="primary"
          onClick={handleCheck}
          disabled={!selectedChoice}
          className="w-full"
        >
          CHECK ANSWER
        </Button>
      )}
    </div>
  );
};
