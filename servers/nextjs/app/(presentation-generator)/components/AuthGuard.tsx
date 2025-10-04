'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '@/store/store';
import { setAuthToken, setUser } from '@/store/slices/authSlice';

interface AuthGuardProps {
  children: React.ReactNode;
}

export default function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter();
  const dispatch = useDispatch();
  const { isAuthenticated, isLoading, user } = useSelector((state: RootState) => state.auth);
  const [isChecking, setIsChecking] = useState(true);
  const [isHydrated, setIsHydrated] = useState(false);

  // Handle hydration
  useEffect(() => {
    setIsHydrated(true);
  }, []);

  useEffect(() => {
    if (!isHydrated) return;

    const checkAuth = async () => {
      // Wait a bit for Redux to be ready
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Check localStorage for existing token
      const token = localStorage.getItem('authToken');
      console.log('AuthGuard: Token present:', !!token);
      console.log('AuthGuard: isAuthenticated:', isAuthenticated);
      console.log('AuthGuard: Current path:', window.location.pathname);
      
      if (token && !isAuthenticated) {
        console.log('AuthGuard: Token exists but not authenticated, validating...');
        // Token exists but Redux state is not set, try to fetch user info
        try {
          const response = await fetch('/api/auth/me', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });
          
          if (response.ok) {
            const userData = await response.json();
            console.log('AuthGuard: Token valid, setting user data');
            dispatch(setAuthToken(token));
            dispatch(setUser(userData));
            setIsChecking(false);
            return;
          } else {
            console.log('AuthGuard: Token invalid, clearing');
            // Token is invalid, clear it
            localStorage.removeItem('authToken');
          }
        } catch (error) {
          console.error('AuthGuard: Error checking auth:', error);
          localStorage.removeItem('authToken');
        }
      }
      
      // Only redirect if we're sure there's no token after hydration
      // and we're not already on an auth page or upload page
      if (!isLoading && !token && !window.location.pathname.startsWith('/auth/') && window.location.pathname !== '/upload') {
        console.log('AuthGuard: No token, redirecting to login');
        // No token exists, redirect to login
        router.replace('/auth/login');
        return;
      }
      
      // If we have a token or user is authenticated, allow access
      if (token || isAuthenticated) {
        console.log('AuthGuard: Access granted');
        setIsChecking(false);
      }
    };

    checkAuth();
  }, [isHydrated, isAuthenticated, isLoading, user, router, dispatch]);

  // Show loading while checking authentication or during hydration
  if (!isHydrated || isLoading || isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-900">Checking authentication...</h2>
          <p className="text-gray-600">Please wait while we verify your authentication.</p>
        </div>
      </div>
    );
  }

  // If not authenticated and no token, don't render children (redirect will happen)
  if (!isAuthenticated && !localStorage.getItem('authToken')) {
    return null;
  }

  // If authenticated or has token, render children
  return <>{children}</>;
}