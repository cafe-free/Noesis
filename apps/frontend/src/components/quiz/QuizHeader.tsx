import React, { useState } from 'react';
import { X, Heart, Sparkles, Volume2, VolumeX } from 'lucide-react';
import { ProgressBar } from '../ui/ProgressBar';
import { sound } from '../../lib/sound';

interface QuizHeaderProps {
  currentIndex: number;
  totalQuestions: number;
  hearts: number;
  score: number;
  onExit: () => void;
}

export const QuizHeader: React.FC<QuizHeaderProps> = ({
  currentIndex,
  totalQuestions,
  hearts,
  score,
  onExit,
}) => {
  const [showExitConfirm, setShowExitConfirm] = useState(false);
  const [isMuted, setIsMuted] = useState(sound.getMuted());

  const progressPercentage = (currentIndex / Math.max(1, totalQuestions)) * 100;

  const handleMuteToggle = () => {
    const next = sound.toggleMute();
    setIsMuted(next);
  };

  return (
    <>
      <header className="w-full max-w-4xl mx-auto px-4 py-3 sm:py-4 flex items-center gap-3 sm:gap-6">
        {/* Exit Button */}
        <button
          type="button"
          onClick={() => setShowExitConfirm(true)}
          aria-label="Exit Quiz"
          className="p-2 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors cursor-pointer shrink-0"
        >
          <X className="w-6 h-6" />
        </button>

        {/* Progress Bar */}
        <div className="flex-1">
          <ProgressBar
            value={progressPercentage}
            height="md"
            color="teal"
            ariaLabel={`Quiz progress: question ${currentIndex + 1} of ${totalQuestions}`}
          />
        </div>

        {/* Question Counter */}
        <span className="hidden sm:inline-block text-xs font-bold tabular-nums text-slate-500 dark:text-slate-400 shrink-0">
          {currentIndex + 1} / {totalQuestions}
        </span>

        {/* XP earned badge */}
        <div className="flex items-center gap-1 text-xs font-bold text-teal-600 dark:text-teal-400 shrink-0">
          <Sparkles className="w-4 h-4 fill-teal-500 text-teal-500" />
          <span className="tabular-nums">+{score * 10}</span>
        </div>

        {/* Hearts */}
        <div
          title={`${hearts} hearts remaining`}
          className="flex items-center gap-1.5 text-rose-500 font-bold text-sm shrink-0"
        >
          <Heart className="w-5 h-5 fill-rose-500" />
          <span className="tabular-nums">{hearts}</span>
        </div>

        {/* Mute button */}
        <button
          type="button"
          onClick={handleMuteToggle}
          aria-label={isMuted ? 'Unmute sounds' : 'Mute sounds'}
          className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer shrink-0"
        >
          {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
        </button>
      </header>

      {/* Exit Confirmation Dialog */}
      {showExitConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 max-w-sm w-full border border-slate-200 dark:border-slate-800 shadow-2xl text-center flex flex-col gap-4">
            <h3 className="text-xl font-bold text-slate-900 dark:text-white font-display">
              Leave this lesson?
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Your progress in this quiz session will not be saved if you leave now.
            </p>
            <div className="flex flex-col gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowExitConfirm(false)}
                className="w-full py-3 font-bold text-white bg-teal-600 hover:bg-teal-500 rounded-xl transition-all shadow-md cursor-pointer"
              >
                Keep Learning
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowExitConfirm(false);
                  onExit();
                }}
                className="w-full py-2.5 font-semibold text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/30 rounded-xl transition-all cursor-pointer"
              >
                Exit Lesson
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
