import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { BookOpen, Sparkles, BarChart2, UserCheck } from 'lucide-react';

export const MobileNav: React.FC = () => {
  const location = useLocation();

  // Hide during active quiz
  if (location.pathname.startsWith('/quiz/')) {
    return null;
  }

  const items = [
    { label: 'Learn', icon: BookOpen, path: '/learn' },
    { label: 'Practice', icon: Sparkles, path: '/learn#practice' },
    { label: 'Progress', icon: BarChart2, path: '/progress' },
    { label: 'Review', icon: UserCheck, path: '/review/attempt-sample-1' },
  ];

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 px-4 py-2 flex items-center justify-around shadow-lg">
      {items.map((item) => {
        const Icon = item.icon;
        const isActive =
          location.pathname === item.path ||
          (item.path !== '/' && location.pathname.startsWith(item.path.split('#')[0]));
        return (
          <Link
            key={item.label}
            to={item.path}
            className={`flex flex-col items-center gap-1 py-1 px-3 text-xs font-semibold transition-colors ${
              isActive
                ? 'text-teal-600 dark:text-teal-400'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-800'
            }`}
          >
            <Icon className="w-5 h-5" />
            <span className="text-[11px]">{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );
};
