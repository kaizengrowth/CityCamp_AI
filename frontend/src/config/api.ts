/**
 * API Configuration
 * Handles different environments and API endpoints
 */

// Get the base URL for API calls
const getApiBaseUrl = (): string => {
  // In production, use relative URLs (same domain as frontend)
  if (process.env.NODE_ENV === 'production') {
    return '';
  }

  // In development, use direct backend URL
  return 'http://localhost:8002';
};

export const API_BASE_URL = getApiBaseUrl();

export const API_ENDPOINTS = {
  // Meetings
  meetings: '/api/v1/meetings/',
  meetingById: (id: number) => `/api/v1/meetings/${id}`,
  meetingAgendaItems: (id: number) => `/api/v1/meetings/${id}/agenda-items`,

  // Auth
  login: '/api/v1/auth/login',
  register: '/api/v1/auth/register',
  profile: '/api/v1/auth/me',

  // Chatbot
  chatbot: '/api/v1/chatbot/chat',

  // Health
  health: '/health',
} as const;

/**
 * Make an API request with proper error handling
 */
export const apiRequest = async <T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> => {
  const url = `${API_BASE_URL}${endpoint}`;
  console.log('Making API request to:', url);

  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    console.log('Sending request with options:', defaultOptions);
    const response = await fetch(url, defaultOptions);
    console.log('Response status:', response.status);
    console.log('Response ok:', response.ok);
    console.log('Response headers:', Object.fromEntries(response.headers.entries()));

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Response error text:', errorText);
      throw new Error(`HTTP error! status: ${response.status}, text: ${errorText}`);
    }

    const data = await response.json();
    console.log('Response data received:', data);
    return data;
  } catch (error) {
    console.error('API request failed:', error);
    console.error('Error type:', typeof error);
    if (error instanceof Error) {
      console.error('Error message:', error.message);
      console.error('Error stack:', error.stack);
    }
    throw error;
  }
};

export default {
  API_BASE_URL,
  API_ENDPOINTS,
  apiRequest,
};
