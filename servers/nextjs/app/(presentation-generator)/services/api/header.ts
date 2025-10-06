/**
 * Safely retrieves authentication token from multiple sources
 * @returns string | null - The auth token or null if not found
 */
const getAuthToken = (): string | null => {
  try {
    // Try localStorage first (primary storage)
    let token = localStorage.getItem('authToken');
    
    // Fallback to sessionStorage if not in localStorage
    if (!token) {
      token = sessionStorage.getItem('authToken');
    }
    
    // Fallback to access_token key (alternative naming)
    if (!token) {
      token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
    }
    
    return token;
  } catch (error) {
    console.error('Error reading auth token from storage:', error);
    return null;
  }
};

/**
 * Validates if a token has a reasonable format
 * @param token - The token to validate
 * @returns boolean - True if token appears valid
 */
const isValidTokenFormat = (token: string): boolean => {
  // Basic JWT format check (starts with 'ey' for JWT)
  if (!token.startsWith('ey')) {
    return false;
  }
  
  // Check minimum length (JWT should be at least 20 characters)
  if (token.length < 20) {
    return false;
  }
  
  return true;
};

/**
 * Gets authentication headers with robust token handling
 * @returns Record<string, string> - Headers object with auth if available
 */
export const getAuthHeader = (): Record<string, string> => {
  try {
    const token = getAuthToken();
    
    if (!token) {
      console.warn("⚠️ No auth token found - requests may fail with 401");
      return {};
    }
    
    // Basic token sanity check
    if (!isValidTokenFormat(token)) {
      console.error("🚫 Invalid token format:", token.slice(0, 10) + "...");
      // Clean up invalid token
      try {
        localStorage.removeItem('authToken');
        localStorage.removeItem('access_token');
        sessionStorage.removeItem('authToken');
        sessionStorage.removeItem('access_token');
      } catch (error) {
        console.error('Error clearing invalid token:', error);
      }
      return {};
    }
    
    console.log('✅ Valid auth token found');
    return { Authorization: `Bearer ${token}` };
  } catch (error) {
    console.error("Error reading auth token:", error);
    return {};
  }
};

/**
 * Gets complete headers including auth token
 * @returns Record<string, string> - Complete headers object
 */
export const getHeader = () => {
  const authHeader = getAuthHeader();
  
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "application/json",  
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    ...authHeader, // Spread auth header (empty object if no token)
  };
  
  // Log header status for debugging
  if (authHeader.Authorization) {
    console.log('getHeader: Added Authorization header');
  } else {
    console.warn('getHeader: No auth token found - requests may fail with 401');
  }
  
  return headers;
};

/**
 * Gets headers for FormData requests with robust token handling
 * @returns Record<string, string> - Headers object for FormData requests
 */
export const getHeaderForFormData = () => {
  const authHeader = getAuthHeader();
  
  const headers: Record<string, string> = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    ...authHeader, // Spread auth header (empty object if no token)
  };
  
  // Log header status for debugging
  if (authHeader.Authorization) {
    console.log('getHeaderForFormData: Added Authorization header');
  } else {
    console.warn('getHeaderForFormData: No auth token found - requests may fail with 401');
  }
  
  return headers;
};
