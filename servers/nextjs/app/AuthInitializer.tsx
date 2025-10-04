'use client';

import { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { setUser, setAuthToken, clearAuth } from '@/store/slices/authSlice';

export function AuthInitializer({ children }: { children: React.ReactNode }) {
  const dispatch = useDispatch();

  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('authToken');
      
      if (token) {
        try {
          // Verify token with backend
          const response = await fetch('/api/auth/me', {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });

          if (response.ok) {
            const userData = await response.json();
            dispatch(setAuthToken(token));
            dispatch(setUser(userData));
          } else {
            // Token is invalid, clear auth state
            localStorage.removeItem('authToken');
            dispatch(clearAuth());
          }
        } catch (error) {
          // Network error, clear auth state
          localStorage.removeItem('authToken');
          dispatch(clearAuth());
        }
      }
    };

    initializeAuth();
  }, [dispatch]);

  return <>{children}</>;
}
