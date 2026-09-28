import { apiClient, clearTokens, getAccessToken, getRefreshToken, setAccessToken, setRefreshToken } from './client';
import { UserProfile } from '../types';

export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface RegisterCredentials {
  email: string;
  password: string;
  confirmPassword?: string;
  name?: string;
  username?: string;
  learningLanguage?: string;
  nativeLanguage?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in?: number;
}

export interface AuthResponse {
  token: string;
  user: UserProfile;
}

export async function getCurrentUser(): Promise<UserProfile | null> {
  const token = getAccessToken();
  if (!token) return null;

  try {
    const profile = await apiClient.get<UserProfile>('/progress/me');
    return profile;
  } catch {
    // If progress fails, try auth/me
    try {
      const user = await apiClient.get<{ id: string; email: string; username?: string }>('/auth/me');
      return {
        id: user.id,
        name: user.username || user.email.split('@')[0] || 'Learner',
        email: user.email,
        learningLanguage: 'Spanish',
        nativeLanguage: 'English',
        currentLevel: 'A1',
        streakDays: 1,
        totalXp: 0,
        dailyGoalXp: 50,
        todayXp: 0,
        hearts: 5,
        maxHearts: 5,
      };
    } catch {
      clearTokens();
      return null;
    }
  }
}

export async function loginUser(creds: LoginCredentials): Promise<AuthResponse> {
  const tokenRes = await apiClient.post<TokenResponse>('/auth/login', {
    email: creds.email,
    password: creds.password,
  });

  setAccessToken(tokenRes.access_token);
  if (tokenRes.refresh_token) {
    setRefreshToken(tokenRes.refresh_token);
  }

  const user = await getCurrentUser();
  const fallbackUser: UserProfile = {
    id: 'user-1',
    name: creds.email.split('@')[0],
    email: creds.email,
    learningLanguage: 'Spanish',
    nativeLanguage: 'English',
    currentLevel: 'A1',
    streakDays: 1,
    totalXp: 0,
    dailyGoalXp: 50,
    todayXp: 0,
    hearts: 5,
    maxHearts: 5,
  };

  return {
    token: tokenRes.access_token,
    user: user || fallbackUser,
  };
}

export async function registerUser(creds: RegisterCredentials): Promise<AuthResponse> {
  const tokenRes = await apiClient.post<TokenResponse>('/auth/register', {
    email: creds.email,
    password: creds.password,
    username: creds.name || creds.username || creds.email.split('@')[0],
  });

  setAccessToken(tokenRes.access_token);
  if (tokenRes.refresh_token) {
    setRefreshToken(tokenRes.refresh_token);
  }

  const user = await getCurrentUser();
  const fallbackUser: UserProfile = {
    id: 'user-1',
    name: creds.name || creds.email.split('@')[0],
    email: creds.email,
    learningLanguage: creds.learningLanguage || 'Spanish',
    nativeLanguage: creds.nativeLanguage || 'English',
    currentLevel: 'A1',
    streakDays: 1,
    totalXp: 0,
    dailyGoalXp: 50,
    todayXp: 0,
    hearts: 5,
    maxHearts: 5,
  };

  return {
    token: tokenRes.access_token,
    user: user || fallbackUser,
  };
}

export async function logoutUser(): Promise<void> {
  const refreshToken = getRefreshToken();
  if (refreshToken) {
    try {
      await apiClient.post('/auth/logout', { refresh_token: refreshToken });
    } catch {
      // Ignore logout request failure
    }
  }
  clearTokens();
}
