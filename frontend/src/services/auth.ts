import apiClient from './api';
import type { LoginCredentials, AuthTokens, User } from '../types';

export const authService = {
  login: async (credentials: LoginCredentials): Promise<{ user: User; tokens: AuthTokens }> => {
    const response = await apiClient.post('/auth/login/', credentials);
    return response.data;
  },

  logout: async (): Promise<void> => {
    // Optional: call logout endpoint if backend has one
    // await apiClient.post('/auth/logout/');
  },

  refreshToken: async (refresh: string): Promise<{ access: string }> => {
    const response = await apiClient.post('/auth/refresh/', { refresh });
    return response.data;
  },
};
