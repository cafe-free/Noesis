import React from 'react';
import { Loader2 } from 'lucide-react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'success' | 'danger';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      variant = 'primary',
      size = 'md',
      isLoading = false,
      leftIcon,
      rightIcon,
      className = '',
      disabled,
      ...props
    },
    ref
  ) => {
    const baseStyles =
      'inline-flex items-center justify-center font-semibold rounded-2xl transition-all duration-150 active:scale-[0.98] select-none whitespace-nowrap focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none disabled:active:scale-100 cursor-pointer';

    const sizes = {
      sm: 'text-xs px-3 py-1.5 gap-1.5 shadow-sm',
      md: 'text-sm px-5 py-2.5 gap-2 shadow-sm',
      lg: 'text-base px-6 py-3.5 gap-2.5 shadow-md',
      xl: 'text-lg px-8 py-4 gap-3 shadow-md font-bold tracking-wide',
    };

    const variants = {
      primary:
        'bg-teal-600 text-white hover:bg-teal-500 active:bg-teal-700 shadow-teal-600/20 focus-visible:ring-teal-500 border-b-4 border-teal-700 active:border-b-0 active:translate-y-1',
      secondary:
        'bg-slate-100 text-slate-800 hover:bg-slate-200 active:bg-slate-300 dark:bg-slate-800 dark:text-slate-100 dark:hover:bg-slate-700 border-b-4 border-slate-300 dark:border-slate-900 active:border-b-0 active:translate-y-1',
      outline:
        'bg-transparent text-slate-700 border-2 border-slate-200 hover:bg-slate-50 dark:text-slate-200 dark:border-slate-700 dark:hover:bg-slate-800 focus-visible:ring-slate-400',
      ghost:
        'bg-transparent text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800/60 shadow-none focus-visible:ring-slate-400',
      success:
        'bg-emerald-600 text-white hover:bg-emerald-500 active:bg-emerald-700 shadow-emerald-600/20 focus-visible:ring-emerald-500 border-b-4 border-emerald-800 active:border-b-0 active:translate-y-1',
      danger:
        'bg-rose-600 text-white hover:bg-rose-500 active:bg-rose-700 shadow-rose-600/20 focus-visible:ring-rose-500 border-b-4 border-rose-800 active:border-b-0 active:translate-y-1',
    };

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={`${baseStyles} ${sizes[size]} ${variants[variant]} ${className}`}
        {...props}
      >
        {isLoading && <Loader2 className="w-4 h-4 animate-spin shrink-0" />}
        {!isLoading && leftIcon && <span className="shrink-0">{leftIcon}</span>}
        <span className="truncate">{children}</span>
        {!isLoading && rightIcon && <span className="shrink-0">{rightIcon}</span>}
      </button>
    );
  }
);

Button.displayName = 'Button';
