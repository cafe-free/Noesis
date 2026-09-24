import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, X, Loader2, Wand2 } from 'lucide-react';
import { Button } from '../ui/Button';
import { startQuizGenerationJob, getQuizGenerationJob } from '../../lib/api/quizzes';
import { sound } from '../../lib/sound';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  defaultLanguage?: string;
}

export const AiQuizGeneratorModal: React.FC<Props> = ({
  isOpen,
  onClose,
  defaultLanguage = 'Spanish',
}) => {
  const navigate = useNavigate();
  const [language, setLanguage] = useState(defaultLanguage);
  const [level, setLevel] = useState<'A1' | 'A2' | 'B1' | 'B2'>('A1');
  const [topic, setTopic] = useState('Everyday Life');
  const [questionCount, setQuestionCount] = useState(4);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationStep, setGenerationStep] = useState('Analyzing vocabulary level...');

  if (!isOpen) return null;

  const topics = [
    'Everyday Life',
    'Food & Dining',
    'Travel & Directions',
    'At the Coffee Shop',
    'Weekend Habits & Hobbies',
    'Shopping & Prices',
    'Family & Friends',
  ];

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);
    sound.playTap();

    try {
      setGenerationStep('Synthesizing exercises with natural grammar...');
      const { jobId } = await startQuizGenerationJob({
        language,
        level,
        topic,
        questionCount,
      });

      // Subtle step progression
      await new Promise((r) => setTimeout(r, 600));
      setGenerationStep('Balancing exercise diversity...');
      await new Promise((r) => setTimeout(r, 500));
      setGenerationStep('Finalizing your practice quiz...');

      const result = await getQuizGenerationJob(jobId, {
        language,
        level,
        topic,
        questionCount,
      });

      if (result.quizId) {
        sound.playCorrect();
        onClose();
        navigate(`/quiz/${result.quizId}`);
      }
    } catch {
      setIsGenerating(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 max-w-md w-full border border-slate-200 dark:border-slate-800 shadow-2xl relative">
        {/* Close Button */}
        {!isGenerating && (
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="absolute top-5 right-5 p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        )}

        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-2xl bg-teal-50 dark:bg-teal-950/40 text-teal-600 dark:text-teal-400 flex items-center justify-center">
            <Wand2 className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white font-display">
              Create Practice Quiz
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              AI adapts question difficulty and topics to your pace
            </p>
          </div>
        </div>

        {isGenerating ? (
          <div className="py-10 flex flex-col items-center text-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-teal-500/10 text-teal-600 dark:text-teal-400 flex items-center justify-center">
              <Loader2 className="w-8 h-8 animate-spin" />
            </div>
            <div>
              <p className="text-base font-bold text-slate-800 dark:text-slate-100 font-display">
                Generating your practice...
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                {generationStep}
              </p>
            </div>
          </div>
        ) : (
          <form onSubmit={handleGenerate} className="flex flex-col gap-4">
            {/* Language */}
            <div>
              <label className="block text-xs font-bold text-slate-600 dark:text-slate-300 mb-1.5">
                Target Language
              </label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-800 dark:text-slate-100 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-teal-500"
              >
                <option value="Spanish">Spanish</option>
                <option value="French">French</option>
                <option value="Japanese">Japanese</option>
                <option value="German">German</option>
                <option value="Italian">Italian</option>
              </select>
            </div>

            {/* Level */}
            <div>
              <label className="block text-xs font-bold text-slate-600 dark:text-slate-300 mb-1.5">
                CEFR Level
              </label>
              <div className="grid grid-cols-4 gap-2">
                {(['A1', 'A2', 'B1', 'B2'] as const).map((lvl) => (
                  <button
                    key={lvl}
                    type="button"
                    onClick={() => setLevel(lvl)}
                    className={`py-2 text-xs font-bold rounded-xl border transition-all cursor-pointer ${
                      level === lvl
                        ? 'border-teal-500 bg-teal-50 dark:bg-teal-950/40 text-teal-700 dark:text-teal-300 ring-2 ring-teal-500/20'
                        : 'border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300 hover:border-slate-300'
                    }`}
                  >
                    {lvl}
                  </button>
                ))}
              </div>
            </div>

            {/* Topic */}
            <div>
              <label className="block text-xs font-bold text-slate-600 dark:text-slate-300 mb-1.5">
                Practice Topic
              </label>
              <select
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-800 dark:text-slate-100 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-teal-500"
              >
                {topics.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>

            {/* Question count */}
            <div>
              <label className="block text-xs font-bold text-slate-600 dark:text-slate-300 mb-1.5">
                Exercise Length
              </label>
              <div className="flex items-center gap-2">
                {[4, 6, 10].map((num) => (
                  <button
                    key={num}
                    type="button"
                    onClick={() => setQuestionCount(num)}
                    className={`flex-1 py-2 text-xs font-bold rounded-xl border transition-all cursor-pointer ${
                      questionCount === num
                        ? 'border-teal-500 bg-teal-50 dark:bg-teal-950/40 text-teal-700 dark:text-teal-300 ring-2 ring-teal-500/20'
                        : 'border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300 hover:border-slate-300'
                    }`}
                  >
                    {num} Exercises
                  </button>
                ))}
              </div>
            </div>

            <Button
              type="submit"
              size="lg"
              variant="primary"
              leftIcon={<Sparkles className="w-5 h-5 fill-white/20" />}
              className="w-full mt-2"
            >
              GENERATE QUIZ
            </Button>
          </form>
        )}
      </div>
    </div>
  );
};
