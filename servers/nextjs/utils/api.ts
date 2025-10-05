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
  
  // Get token from localStorage
  const token = localStorage.getItem('authToken');
  
  // Enhanced logging
  console.log('🔐 fetchWithAuth: Starting request to:', url);
  console.log('🔐 fetchWithAuth: Token present:', !!token);
  console.log('🔐 fetchWithAuth: Token preview:', token ? `${token.substring(0, 10)}...` : 'None');
  
  // Log token status for debugging
  if (requireAuth && !token) {
    console.warn('⚠️ fetchWithAuth: No auth token found in localStorage for URL:', url);
    console.warn('⚠️ fetchWithAuth: This may cause 401 Unauthorized errors');
  } else if (token) {
    console.log('✅ fetchWithAuth: Using auth token for URL:', url);
  }
  
  // Prepare headers with explicit Authorization
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': token ? `Bearer ${token}` : '',
    ...fetchOptions.headers,
  };
  
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
  
  // Get token from localStorage
  const token = localStorage.getItem('authToken');
  
  // Log token status for debugging
  if (requireAuth && !token) {
    console.warn('fetchWithAuthFormData: No auth token found in localStorage for URL:', url);
    console.warn('fetchWithAuthFormData: This may cause 401 Unauthorized errors');
  } else if (token) {
    console.log('fetchWithAuthFormData: Using auth token for URL:', url);
  }
  
  // Prepare headers (don't set Content-Type for FormData)
  const headers: HeadersInit = {
    'Accept': 'application/json',
    ...fetchOptions.headers,
  };
  
  // Add Authorization header if token exists
  if (token) {
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
  }
  
  return response;
}

/**
 * Checks if user is authenticated by verifying token exists
 * @returns boolean
 */
export function isAuthenticated(): boolean {
  const token = localStorage.getItem('authToken');
  return !!token;
}

/**
 * Gets the current auth token
 * @returns string | null
 */
export function getAuthToken(): string | null {
  return localStorage.getItem('authToken');
}

/**
 * Clears the auth token
 */
export function clearAuthToken(): void {
  localStorage.removeItem('authToken');
  console.log('Auth token cleared');
}
