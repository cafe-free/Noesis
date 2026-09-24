import React, { createContext, useContext, useState, useEffect } from 'react';
import { UserProfile } from '../types';
import { getCurrentUser, loginUser, logoutUser, registerUser, LoginCredentials, RegisterCredentials } from '../lib/api/auth';
import { MOCK_USER } from '../lib/mock/data';

interface AuthContextType {
  currentUser: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (creds: LoginCredentials) => Promise<void>;
  register: (creds: RegisterCredentials) => Promise<void>;
  logout: () => Promise<void>;
  demoLogin: () => Promise<void>;
  updateUser: (updates: Partial<UserProfile>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    async function initAuth() {
      try {
        const user = await getCurrentUser();
        // If not logged in yet, default to MOCK_USER for effortless instant prototyping experience if token exists,
        // or check if there is an existing session
        if (user) {
          setCurrentUser(user);
        } else {
          // Pre-populate mock user for smooth preview experience unless explicitly logged out
          const isExplicitLoggedOut = localStorage.getItem('verba_explicit_logged_out');
          if (!isExplicitLoggedOut) {
            localStorage.setItem('verba_auth_token', 'mock_jwt_token_brian');
            localStorage.setItem('verba_user_profile', JSON.stringify(MOCK_USER));
            setCurrentUser(MOCK_USER);
          }
        }
      } catch {
        setCurrentUser(null);
      } finally {
        setIsLoading(false);
      }
    }
    initAuth();
  }, []);

  const login = async (creds: LoginCredentials) => {
    setIsLoading(true);
    localStorage.removeItem('verba_explicit_logged_out');
    try {
      const res = await loginUser(creds);
      setCurrentUser(res.user);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (creds: RegisterCredentials) => {
    setIsLoading(true);
    localStorage.removeItem('verba_explicit_logged_out');
    try {
      const res = await registerUser(creds);
      setCurrentUser(res.user);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    localStorage.setItem('verba_explicit_logged_out', 'true');
    try {
      await logoutUser();
      setCurrentUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const demoLogin = async () => {
    setIsLoading(true);
    localStorage.removeItem('verba_explicit_logged_out');
    try {
      await login({ email: 'brian24564L@gmail.com' });
    } finally {
      setIsLoading(false);
    }
  };

  const updateUser = (updates: Partial<UserProfile>) => {
    setCurrentUser((prev) => {
      if (!prev) return null;
      const updated = { ...prev, ...updates };
      localStorage.setItem('verba_user_profile', JSON.stringify(updated));
      return updated;
    });
  };

  return (
    <AuthContext.Provider
      value={{
        currentUser,
        isAuthenticated: !!currentUser,
        isLoading,
        login,
        register,
        logout,
        demoLogin,
        updateUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
