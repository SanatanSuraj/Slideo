'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useDispatch } from 'react-redux';
import { setUser, setAuthToken } from '@/store/slices/authSlice';

export default function GoogleAuthSuccess() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const dispatch = useDispatch();

  useEffect(() => {
    const token = searchParams.get('token');
    const userData = searchParams.get('user');

    if (token && userData) {
      try {
        const user = JSON.parse(userData);
        
        // Store token and user data
        localStorage.setItem('authToken', token);
        dispatch(setAuthToken(token));
        dispatch(setUser(user));
        
        // Redirect to Create Presentation page
        router.replace('/upload');
      } catch (error) {
        console.error('Error parsing user data:', error);
        router.push('/auth/login?error=parse_error');
      }
    } else {
      router.push('/auth/login?error=missing_data');
    }
  }, [searchParams, router, dispatch]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 flex items-center justify-center p-4">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
        <h2 className="text-xl font-semibold text-gray-900">Completing sign in...</h2>
        <p className="text-gray-600">Please wait while we set up your account.</p>
      </div>
    </div>
  );
}
