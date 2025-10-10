'use client';

import { useEffect, useState } from 'react';
import { setCanChangeKeys, setLLMConfig } from '@/store/slices/userConfig';
import { hasValidLLMConfig } from '@/utils/storeHelpers';
import { usePathname, useRouter } from 'next/navigation';
import { useDispatch } from 'react-redux';
import { checkIfSelectedOllamaModelIsPulled } from '@/utils/providerUtils';
import { LLMConfig } from '@/types/llm_config';

export function ConfigurationInitializer({ children }: { children: React.ReactNode }) {
  const dispatch = useDispatch();

  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const route = usePathname();

  // Skip configuration check for presentation pages
  const isPresentationPage = route?.includes('/presentation');

  // Fetch user config state
  useEffect(() => {
    if (!isPresentationPage) {
      fetchUserConfigState();
    } else {
      setIsLoading(false);
    }
  }, [isPresentationPage]);

  const setLoadingToFalseAfterNavigatingTo = (pathname: string) => {
    const interval = setInterval(() => {
      if (window.location.pathname === pathname) {
        clearInterval(interval);
        setIsLoading(false);
      }
    }, 500);
  }

  const fetchUserConfigState = async () => {
    setIsLoading(true);
    const response = await fetch('/api/can-change-keys');
    const canChangeKeys = (await response.json()).canChange;
    dispatch(setCanChangeKeys(canChangeKeys));

    if (canChangeKeys) {
      const response = await fetch('/api/user-config');
      const llmConfig = await response.json();
      if (!llmConfig.LLM) {
        llmConfig.LLM = 'openai';
      }
      dispatch(setLLMConfig(llmConfig));
      const isValid = hasValidLLMConfig(llmConfig);
      console.log('ConfigurationInitializer: LLM config validity:', isValid, 'Route:', route);
      if (isValid) {
        // Check if the selected Ollama model is pulled
        if (llmConfig.LLM === 'ollama') {
          const isPulled = await checkIfSelectedOllamaModelIsPulled(llmConfig.OLLAMA_MODEL);
          if (!isPulled) {
            console.warn('Ollama model not pulled, but allowing access to continue');
            // Don't redirect - let user stay where they are
            // Show error message instead of redirecting
          }
        }
        if (llmConfig.LLM === 'custom') {
          const isAvailable = await checkIfSelectedCustomModelIsAvailable(llmConfig);
          if (!isAvailable) {
            console.warn('Custom model not available, but allowing access to continue');
            // Don't redirect - let user stay where they are
            // Show error message instead of redirecting
          }
        }
        // Don't redirect if user is on auth pages
        if (route === '/' && !route.startsWith('/auth/')) {
          router.push('/upload');
          setLoadingToFalseAfterNavigatingTo('/upload');
        } else {
          setIsLoading(false);
        }
      } else {
        // Don't redirect any pages - let the user stay where they are
        // Show error message instead of redirecting
        console.log('ConfigurationInitializer: Invalid LLM config, but allowing access to route:', route);
        console.warn('LLM configuration is invalid. Some features may not work properly.');
        setIsLoading(false);
      }
    } else {
      // Don't redirect if user is on auth pages
      if (route === '/' && !route.startsWith('/auth/')) {
        router.push('/upload');
        setLoadingToFalseAfterNavigatingTo('/upload');
      } else {
        setIsLoading(false);
      }
    }
  }


  const checkIfSelectedCustomModelIsAvailable = async (llmConfig: LLMConfig) => {
    try {
      const response = await fetch('/api/v1/ppt/openai/models/available', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: llmConfig.CUSTOM_LLM_URL,
          api_key: llmConfig.CUSTOM_LLM_API_KEY,
        }),
      });
      const data = await response.json();
      return data.includes(llmConfig.CUSTOM_MODEL);
    } catch (error) {
      console.error('Error fetching custom models:', error);
      return false;
    }
  }

  // For presentation pages, always return children immediately
  if (isPresentationPage) {
    return children;
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#E9E8F8] via-[#F5F4FF] to-[#E0DFF7] flex items-center justify-center p-4">
        <div className="max-w-md w-full">
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8 text-center">
            {/* Logo/Branding */}
            <div className="mb-6">
              <img
                src="/Logo.png"
                alt="PresentOn"
                className="h-12 mx-auto mb-4 opacity-90"
              />
              <div className="w-16 h-1 bg-gradient-to-r from-blue-500 to-purple-600 mx-auto rounded-full"></div>
            </div>

            {/* Loading Text */}
            <div className="space-y-2">
              <h3 className="text-lg font-semibold text-gray-800 font-inter">
                Initializing Application
              </h3>
              <p className="text-sm text-gray-600 font-inter">
                Loading configuration and checking model availability...
              </p>
            </div>

            {/* Progress Indicator */}
            <div className="mt-6">
              <div className="flex space-x-1 justify-center">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return children;
}
