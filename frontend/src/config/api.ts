/**
 * API Configuration
 * Handles different environments and API endpoints
 */

// Get the base URL for API calls
const getApiBaseUrl = (): string => {
  // In development and production, use relative URLs
  // Vite proxy handles development, CloudFront handles production
  return '';
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

  // Subscriptions
  subscriptions: '/api/v1/subscriptions/',
  subscriptionById: (id: number) => `/api/v1/subscriptions/${id}`,
  subscriptionTopics: '/api/v1/subscriptions/topics',
  testSms: '/api/v1/subscriptions/test-sms',

  // Representatives
  composeEmail: '/api/v1/representatives/compose-email',
  findRepresentatives: '/api/v1/representatives/find',

  // Organizations
  organizations: '/api/v1/organizations/',
  organizationById: (id: number) => `/api/v1/organizations/${id}`,
  organizationBySlug: (slug: string) => `/api/v1/organizations/slug/${slug}`,
};

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

    if (!response.ok) {
      // Enhanced error handling for production debugging
      let errorMessage = `HTTP error! status: ${response.status}`;

      try {
        const errorText = await response.text();
        console.error('Response error text:', errorText);
        errorMessage += `, text: ${errorText}`;
      } catch (e) {
        console.error('Could not read error response text');
      }

      throw new Error(errorMessage);
    }

    const data = await response.json();
    console.log('Response data received successfully');
    return data;
  } catch (error) {
    console.error('API request failed:', error);
    console.error('URL attempted:', url);
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
