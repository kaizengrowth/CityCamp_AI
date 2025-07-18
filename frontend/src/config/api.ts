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

  // Default to relative URLs (will be proxied by Vite)
  return '';
};

export const API_BASE_URL = getApiBaseUrl();

export const API_ENDPOINTS = {
  // Meetings
  meetings: '/api/v1/meetings/public',
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

  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, defaultOptions);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

export default {
  API_BASE_URL,
  API_ENDPOINTS,
  apiRequest,
};
