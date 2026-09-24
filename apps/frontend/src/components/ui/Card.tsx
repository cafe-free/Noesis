import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'interactive' | 'flat';
  selected?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  variant = 'default',
  selected = false,
  className = '',
  ...props
}) => {
  const base =
    'rounded-2xl transition-all duration-150 p-5';

  const variants = {
    default:
      'bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm',
    interactive:
      'bg-white dark:bg-slate-900 border-2 cursor-pointer active:scale-[0.99] ' +
      (selected
        ? 'border-teal-500 bg-teal-50/50 dark:bg-teal-950/20 dark:border-teal-400 shadow-md ring-2 ring-teal-500/20'
        : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 hover:shadow-md'),
    flat:
      'bg-slate-50 dark:bg-slate-850 border border-slate-100 dark:border-slate-800/60',
  };

  return (
    <div className={`${base} ${variants[variant]} ${className}`} {...props}>
      {children}
    </div>
  );
};
