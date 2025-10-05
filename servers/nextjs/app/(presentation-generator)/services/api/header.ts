export const getHeader = () => {
  const token = localStorage.getItem('authToken');
  
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "application/json",  
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
  };
  
  // Add Authorization header if token exists
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
    console.log('getHeader: Added Authorization header');
  } else {
    console.warn('getHeader: No auth token found - requests may fail with 401');
  }
  
  return headers;
};

export const getHeaderForFormData = () => {
  const token = localStorage.getItem('authToken');
  
  const headers: Record<string, string> = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
  };
  
  // Add Authorization header if token exists
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
    console.log('getHeaderForFormData: Added Authorization header');
  } else {
    console.warn('getHeaderForFormData: No auth token found - requests may fail with 401');
  }
  
  return headers;
};
