import React from 'react';
import { Link } from 'react-router-dom';

export const Footer: React.FC = () => {
  return (
    <footer className="mt-auto py-8 border-t border-slate-200 dark:border-slate-800 text-center text-xs text-slate-500 dark:text-slate-400">
      <div className="max-w-5xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
        <span>© 2026 Noesis Language Platform. All rights reserved.</span>
        <div className="flex items-center gap-6">
          <Link to="/learn" className="hover:text-slate-800 dark:hover:text-slate-200">
            Dashboard
          </Link>
          <Link to="/login" className="hover:text-slate-800 dark:hover:text-slate-200">
            Sign In
          </Link>
          <Link to="/register" className="hover:text-slate-800 dark:hover:text-slate-200">
            Register
          </Link>
        </div>
      </div>
    </footer>
  );
};
