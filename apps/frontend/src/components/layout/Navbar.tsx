import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Flame, Heart, Sparkles, Moon, Sun, Volume2, VolumeX, LogOut, User } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { sound } from '../../lib/sound';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const { currentUser, isAuthenticated, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [isMuted, setIsMuted] = React.useState(sound.getMuted());

  // Hide main nav during active quiz
  if (location.pathname.startsWith('/quiz/')) {
    return null;
  }

  const handleToggleMute = () => {
    const next = sound.toggleMute();
    setIsMuted(next);
  };

  const navLinks = [
    { label: 'Learn', href: '/learn' },
    { label: 'Practice', href: '/learn#practice' },
    { label: 'Progress', href: '/progress' },
    { label: 'Mistakes', href: '/review/attempt-sample-1' },
  ];

  return (
    <header className="sticky top-0 z-40 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 transition-colors">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        {/* Zone 1: Brand Wordmark */}
        <Link
          to="/"
          className="flex items-center gap-2.5 text-xl font-extrabold tracking-tight text-slate-900 dark:text-white group"
        >
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-teal-600 to-emerald-400 flex items-center justify-center text-white shadow-sm shadow-teal-500/30 group-hover:scale-105 transition-transform">
            <Sparkles className="w-5 h-5" />
          </div>
          <span className="font-display tracking-tight text-2xl font-bold">Verba</span>
        </Link>

        {/* Zone 2: Navigation Links */}
        <nav className="hidden md:flex items-center gap-8 text-sm font-semibold text-slate-600 dark:text-slate-300">
          {navLinks.map((link) => {
            const isActive =
              location.pathname === link.href ||
              (link.href !== '/' && location.pathname.startsWith(link.href.split('#')[0]));
            return (
              <Link
                key={link.label}
                to={link.href}
                className={`transition-colors hover:text-teal-600 dark:hover:text-teal-400 ${
                  isActive ? 'text-teal-600 dark:text-teal-400 font-bold' : ''
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        {/* Zone 3: Actions & Status */}
        <div className="flex items-center gap-3">
          {/* Sound Mute Toggle */}
          <button
            onClick={handleToggleMute}
            aria-label={isMuted ? 'Unmute sounds' : 'Mute sounds'}
            className="p-2 rounded-xl text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
          >
            {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
          </button>

          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
            className="p-2 rounded-xl text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
          >
            {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4 text-slate-600" />}
          </button>

          {isAuthenticated && currentUser ? (
            <div className="flex items-center gap-3 pl-2 border-l border-slate-200 dark:border-slate-800">
              {/* Streak */}
              <div
                title={`${currentUser.streakDays} day streak`}
                className="flex items-center gap-1 text-xs font-bold text-amber-600 dark:text-amber-400"
              >
                <Flame className="w-4 h-4 fill-amber-500 text-amber-500 animate-pulse" />
                <span className="tabular-nums">{currentUser.streakDays}</span>
              </div>

              {/* Hearts */}
              <div
                title={`${currentUser.hearts} hearts available`}
                className="flex items-center gap-1 text-xs font-bold text-rose-500 dark:text-rose-400"
              >
                <Heart className="w-4 h-4 fill-rose-500 text-rose-500" />
                <span className="tabular-nums">{currentUser.hearts}</span>
              </div>

              {/* User Dropdown / Logout */}
              <div className="flex items-center gap-2">
                <Link
                  to="/learn"
                  className="w-8 h-8 rounded-full bg-teal-100 dark:bg-teal-900/40 text-teal-700 dark:text-teal-300 flex items-center justify-center font-bold text-xs"
                >
                  {currentUser.name.charAt(0).toUpperCase()}
                </Link>
                <button
                  onClick={() => logout()}
                  title="Sign out"
                  className="p-2 text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 transition-colors cursor-pointer"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                to="/login"
                className="px-3.5 py-1.5 text-xs font-bold text-slate-700 dark:text-slate-200 hover:text-teal-600 transition-colors"
              >
                Sign in
              </Link>
              <Link
                to="/register"
                className="px-4 py-2 text-xs font-bold text-white bg-teal-600 hover:bg-teal-500 rounded-xl transition-all shadow-sm"
              >
                Get Started
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
