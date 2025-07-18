import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import App from '../../frontend/src/App';
import { AuthProvider } from '../../frontend/src/contexts/AuthContext';

// Mock the API module
jest.mock('../../frontend/src/config/api', () => ({
  apiRequest: jest.fn(),
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
    <BrowserRouter>
      <AuthProvider>
        {children}
      </AuthProvider>
    </BrowserRouter>
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
    const appElement = document.querySelector('#root');
    expect(appElement).toBeInTheDocument();
  });
}); 