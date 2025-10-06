/**
 * API utility functions for authenticated requests
 */

interface FetchWithAuthOptions extends RequestInit {
  requireAuth?: boolean;
}

/**
 * Fetches data with automatic Authorization header injection
 * @param url - The URL to fetch
 * @param options - Fetch options
 * @returns Promise<Response>
 */
export async function fetchWithAuth(
  url: string, 
  options: FetchWithAuthOptions = {}
): Promise<Response> {
  const { requireAuth = true, ...fetchOptions } = options;
  
  // Get token from localStorage with fallback to sessionStorage
  let token = localStorage.getItem('authToken');
  if (!token) {
    token = sessionStorage.getItem('authToken');
  }
  
  // Enhanced logging
  console.log('🔐 fetchWithAuth: Starting request to:', url);
  console.log('🔐 fetchWithAuth: Token present:', !!token);
  console.log('🔐 fetchWithAuth: Token preview:', token ? `${token.substring(0, 10)}...` : 'None');
  
  // Validate token format if present
  if (token && !token.startsWith('ey')) {
    console.error('🚫 fetchWithAuth: Invalid token format detected:', token.substring(0, 10) + '...');
    console.error('🚫 fetchWithAuth: Clearing invalid token from storage');
    localStorage.removeItem('authToken');
    sessionStorage.removeItem('authToken');
    token = null;
  }
  
  // Log token status for debugging
  if (requireAuth && !token) {
    console.warn('⚠️ fetchWithAuth: No auth token found in localStorage/sessionStorage for URL:', url);
    console.warn('⚠️ fetchWithAuth: This may cause 401 Unauthorized errors');
  } else if (token) {
    console.log('✅ fetchWithAuth: Using auth token for URL:', url);
  }
  
  // Prepare headers with explicit Authorization
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    ...fetchOptions.headers,
  };
  
  // Only add Authorization header if token exists and is valid
  if (token && token.startsWith('ey')) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  // Log headers for debugging
  console.log('📤 fetchWithAuth: Request headers:', {
    'Content-Type': headers['Content-Type'],
    'Authorization': headers['Authorization'] ? `${headers['Authorization'].substring(0, 20)}...` : 'None'
  });
  
  // Make the request
  const response = await fetch(url, {
    ...fetchOptions,
    headers,
  });
  
  // Enhanced response logging
  console.log('📥 fetchWithAuth: Response status:', response.status);
  console.log('📥 fetchWithAuth: Response URL:', response.url);
  
  // Log response status for debugging
  if (response.status === 401) {
    console.error('❌ fetchWithAuth: 401 Unauthorized for URL:', url);
    console.error('❌ fetchWithAuth: Token may be invalid or expired');
    console.error('❌ fetchWithAuth: Token used:', token ? `${token.substring(0, 10)}...` : 'None');
    
    // If we get 401, try to clear potentially invalid tokens
    if (token) {
      console.error('🧹 fetchWithAuth: Clearing potentially invalid token from storage');
      localStorage.removeItem('authToken');
      sessionStorage.removeItem('authToken');
    }
  } else if (response.status >= 500) {
    console.error('❌ fetchWithAuth: Server error for URL:', url, 'Status:', response.status);
  } else if (response.status >= 400) {
    console.warn('⚠️ fetchWithAuth: Client error for URL:', url, 'Status:', response.status);
  } else {
    console.log('✅ fetchWithAuth: Request successful for URL:', url, 'Status:', response.status);
  }
  
  return response;
}

/**
 * Fetches data with FormData (for file uploads) and automatic Authorization header injection
 * @param url - The URL to fetch
 * @param options - Fetch options
 * @returns Promise<Response>
 */
export async function fetchWithAuthFormData(
  url: string, 
  options: FetchWithAuthOptions = {}
): Promise<Response> {
  const { requireAuth = true, ...fetchOptions } = options;
  
  // Get token from localStorage with fallback to sessionStorage
  let token = localStorage.getItem('authToken');
  if (!token) {
    token = sessionStorage.getItem('authToken');
  }
  
  // Validate token format if present
  if (token && !token.startsWith('ey')) {
    console.error('🚫 fetchWithAuthFormData: Invalid token format detected:', token.substring(0, 10) + '...');
    console.error('🚫 fetchWithAuthFormData: Clearing invalid token from storage');
    localStorage.removeItem('authToken');
    sessionStorage.removeItem('authToken');
    token = null;
  }
  
  // Log token status for debugging
  if (requireAuth && !token) {
    console.warn('fetchWithAuthFormData: No auth token found in localStorage/sessionStorage for URL:', url);
    console.warn('fetchWithAuthFormData: This may cause 401 Unauthorized errors');
  } else if (token) {
    console.log('fetchWithAuthFormData: Using auth token for URL:', url);
  }
  
  // Prepare headers (don't set Content-Type for FormData)
  const headers: HeadersInit = {
    'Accept': 'application/json',
    ...fetchOptions.headers,
  };
  
  // Add Authorization header if token exists and is valid
  if (token && token.startsWith('ey')) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  // Make the request
  const response = await fetch(url, {
    ...fetchOptions,
    headers,
  });
  
  // Log response status for debugging
  if (response.status === 401) {
    console.error('fetchWithAuthFormData: 401 Unauthorized for URL:', url);
    console.error('fetchWithAuthFormData: Token may be invalid or expired');
    
    // If we get 401, try to clear potentially invalid tokens
    if (token) {
      console.error('🧹 fetchWithAuthFormData: Clearing potentially invalid token from storage');
      localStorage.removeItem('authToken');
      sessionStorage.removeItem('authToken');
    }
  }
  
  return response;
}

/**
 * Checks if user is authenticated by verifying token exists and is valid
 * @returns boolean
 */
export function isAuthenticated(): boolean {
  const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
  return !!(token && token.startsWith('ey'));
}

/**
 * Gets the current auth token from localStorage or sessionStorage
 * @returns string | null
 */
export function getAuthToken(): string | null {
  let token = localStorage.getItem('authToken');
  if (!token) {
    token = sessionStorage.getItem('authToken');
  }
  
  // Validate token format
  if (token && !token.startsWith('ey')) {
    console.warn('getAuthToken: Invalid token format detected, clearing from storage');
    localStorage.removeItem('authToken');
    sessionStorage.removeItem('authToken');
    return null;
  }
  
  return token;
}

/**
 * Clears the auth token from both localStorage and sessionStorage
 */
export function clearAuthToken(): void {
  localStorage.removeItem('authToken');
  sessionStorage.removeItem('authToken');
  console.log('Auth token cleared from all storage');
}

/**
 * Sets the auth token in localStorage
 * @param token - The token to store
 */
export function setAuthToken(token: string): void {
  if (token && token.startsWith('ey')) {
    localStorage.setItem('authToken', token);
    console.log('Auth token stored successfully');
  } else {
    console.error('setAuthToken: Invalid token format provided');
  }
}

/**
 * Retry mechanism for failed requests
 * @param fn - The function to retry
 * @param maxRetries - Maximum number of retries
 * @param delay - Delay between retries in ms
 * @returns Promise<T>
 */
async function retry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> {
  let lastError: Error;
  
  for (let i = 0; i <= maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      
      if (i === maxRetries) {
        throw lastError;
      }
      
      console.warn(`Retry ${i + 1}/${maxRetries} failed:`, error);
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
    }
  }
  
  throw lastError!;
}

/**
 * Enhanced fetchWithAuth with retry mechanism
 * @param url - The URL to fetch
 * @param options - Fetch options
 * @param retryOptions - Retry configuration
 * @returns Promise<Response>
 */
export async function fetchWithAuthRetry(
  url: string,
  options: FetchWithAuthOptions = {},
  retryOptions: { maxRetries?: number; delay?: number } = {}
): Promise<Response> {
  const { maxRetries = 2, delay = 1000 } = retryOptions;
  
  return retry(async () => {
    const response = await fetchWithAuth(url, options);
    
    // Only retry on 401 errors (authentication issues)
    if (response.status === 401) {
      throw new Error('Authentication failed');
    }
    
    return response;
  }, maxRetries, delay);
}

/**
 * Waits for user authentication to be available
 * @param maxWaitTime - Maximum time to wait in ms
 * @param checkInterval - Interval to check authentication in ms
 * @returns Promise<boolean> - True if authenticated, false if timeout
 */
export async function waitForAuthentication(
  maxWaitTime: number = 5000,
  checkInterval: number = 100
): Promise<boolean> {
  const startTime = Date.now();
  
  while (Date.now() - startTime < maxWaitTime) {
    if (isAuthenticated()) {
      return true;
    }
    
    await new Promise(resolve => setTimeout(resolve, checkInterval));
  }
  
  return false;
}

/**
 * Fetches data with authentication, waiting for auth if needed
 * @param url - The URL to fetch
 * @param options - Fetch options
 * @returns Promise<Response>
 */
export async function fetchWithAuthWait(
  url: string,
  options: FetchWithAuthOptions = {}
): Promise<Response> {
  // Wait for authentication if not already authenticated
  if (!isAuthenticated()) {
    console.log('🔐 fetchWithAuthWait: Waiting for authentication...');
    const authenticated = await waitForAuthentication();
    
    if (!authenticated) {
      console.warn('⚠️ fetchWithAuthWait: Authentication timeout, proceeding without auth');
    }
  }
  
  return fetchWithAuth(url, options);
}
