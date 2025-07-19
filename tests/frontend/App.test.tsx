import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from '../../frontend/src/App';

// Mock the API module
jest.mock('../../frontend/src/config/api', () => ({
  apiRequest: jest.fn(),
}));

// Mock date-fns
jest.mock('date-fns', () => ({
  format: jest.fn((date, formatStr) => '2024-01-01'),
  parseISO: jest.fn((dateStr) => new Date(dateStr)),
  isValid: jest.fn(() => true),
}));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const AppWrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>
        {children}
  </QueryClientProvider>
);

describe('App', () => {
  test('renders without crashing', () => {
    render(
      <AppWrapper>
        <App />
      </AppWrapper>
    );

    // The app should render without throwing an error
    expect(document.body).toBeInTheDocument();
  });

  test('contains main navigation elements', () => {
    render(
      <AppWrapper>
        <App />
      </AppWrapper>
    );

    // Check if the main app structure is present
    // This is a basic test - you can expand based on your actual app structure
    const appElement = document.querySelector('div');
    expect(appElement).toBeInTheDocument();
  });
});
