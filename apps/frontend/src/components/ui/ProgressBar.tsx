import React from 'react';

interface ProgressBarProps {
  value: number; // 0 to 100
  max?: number;
  height?: 'sm' | 'md' | 'lg';
  color?: 'teal' | 'emerald' | 'amber' | 'rose' | 'indigo';
  showLabel?: boolean;
  className?: string;
  ariaLabel?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  height = 'md',
  color = 'teal',
  showLabel = false,
  className = '',
  ariaLabel = 'Progress',
}) => {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));

  const heights = {
    sm: 'h-2',
    md: 'h-3.5',
    lg: 'h-5',
  };

  const colors = {
    teal: 'bg-teal-500 shadow-teal-500/20',
    emerald: 'bg-emerald-500 shadow-emerald-500/20',
    amber: 'bg-amber-500 shadow-amber-500/20',
    rose: 'bg-rose-500 shadow-rose-500/20',
    indigo: 'bg-indigo-500 shadow-indigo-500/20',
  };

  return (
    <div className={`w-full flex items-center gap-3 ${className}`}>
      <div
        role="progressbar"
        aria-valuenow={Math.round(percentage)}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={ariaLabel}
        className={`relative w-full ${heights[height]} bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden shadow-inner`}
      >
        <div
          className={`h-full ${colors[color]} rounded-full transition-all duration-300 ease-out`}
          style={{ width: `${percentage}%` }}
        >
          {/* Subtle glossy sheen for warmth */}
          <div className="w-full h-1/2 bg-white/20 rounded-full" />
        </div>
      </div>
      {showLabel && (
        <span className="text-xs font-semibold tabular-nums text-slate-600 dark:text-slate-400 shrink-0">
          {Math.round(percentage)}%
        </span>
      )}
    </div>
  );
};
