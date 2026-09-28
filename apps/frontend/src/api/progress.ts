import { apiClient } from './client';
import { UserProfile, WeakAreaItem } from '../types';

export async function getMyProgress(): Promise<UserProfile> {
  return apiClient.get<UserProfile>('/progress/me');
}

export async function getWeaknesses(): Promise<WeakAreaItem[]> {
  const res = await apiClient.get<WeakAreaItem[]>('/progress/me/weaknesses');
  return res || [];
}
