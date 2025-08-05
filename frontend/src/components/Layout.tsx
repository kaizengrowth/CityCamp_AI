import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ChatbotWidget } from './ChatbotWidget';

const navigation = [
  { name: 'Home', href: '/' },
  { name: 'Meetings', href: '/meetings' },
  { name: 'Campaigns', href: '/campaigns' },
  { name: 'Contact Reps', href: '/contact-representatives' },
];

const userNavigation = [
  { name: 'Dashboard', href: '/dashboard' },
  { name: 'Notifications', href: '/notifications' },
  { name: 'Profile', href: '/profile' },
];

export const Layout: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white shadow-sm border-b border-gray-200 flex-shrink-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <Link to="/" className="flex items-center space-x-2">
                <div className="w-12 h-8 rounded-lg flex items-center justify-center" style={{backgroundColor: '#162a49'}}>
                  <span className="text-white font-bold text-xs">Tulsa</span>
                </div>
                <span className="text-xl font-bold" style={{color: '#162a49'}}>Civic Spark AI</span>
              </Link>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex space-x-8">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive(item.href)
                      ? 'text-primary-600 bg-primary-50'
                      : 'text-gray-700 hover:text-primary-600 hover:bg-gray-50'
                  }`}
                >
                  {item.name}
                </Link>
              ))}
            </nav>

            {/* User Menu */}
            <div className="flex items-center space-x-4">
              {user ? (
                <>
                  {/* User Navigation */}
                  <nav className="hidden md:flex space-x-4">
                    {userNavigation.map((item) => (
                      <Link
                        key={item.name}
                        to={item.href}
                        className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                          isActive(item.href)
                            ? 'text-primary-600 bg-primary-50'
                            : 'text-gray-700 hover:text-primary-600 hover:bg-gray-50'
                        }`}
                      >
                        {item.name}
                      </Link>
                    ))}
                  </nav>

                  {/* User Info & Logout */}
                  <div className="flex items-center space-x-3">
                    <span className="text-sm text-gray-700">
                      Welcome, {user.full_name}
                    </span>
                    <button
                      onClick={logout}
                      className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
                    >
                      Logout
                    </button>
                  </div>
                </>
              ) : (
                <div className="flex items-center space-x-1 sm:space-x-2 lg:space-x-3">
                  <Link
                    to="/signup/notifications"
                    className="px-2 sm:px-3 lg:px-4 py-2 text-xs sm:text-sm font-medium text-white rounded-md transition-colors hover:opacity-90 whitespace-nowrap"
                    style={{backgroundColor: '#5086d3'}}
                  >
                    <span className="hidden sm:inline">Get Notified</span>
                    <span className="sm:hidden">Notify</span>
                  </Link>
                  <Link
                    to="/login"
                    className="px-2 sm:px-3 lg:px-4 py-2 text-xs sm:text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors whitespace-nowrap"
                  >
                    Login
                  </Link>
                  <Link
                    to="/register"
                    className="px-2 sm:px-3 lg:px-4 py-2 text-xs sm:text-sm font-medium text-white rounded-md transition-colors hover:opacity-90 whitespace-nowrap"
                    style={{backgroundColor: '#5086d3'}}
                  >
                    Register
                  </Link>
                </div>
              )}

              {/* Mobile menu button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2 rounded-md text-gray-700 hover:text-gray-900 hover:bg-gray-50"
              >
                {mobileMenuOpen ? '✕' : '☰'}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-gray-200">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`block px-3 py-2 rounded-md text-base font-medium transition-colors ${
                    isActive(item.href)
                      ? 'text-primary-600 bg-primary-50'
                      : 'text-gray-700 hover:text-primary-600 hover:bg-gray-50'
                  }`}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {item.name}
                </Link>
              ))}

              {user ? (
                <>
                  {userNavigation.map((item) => (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`block px-3 py-2 rounded-md text-base font-medium transition-colors ${
                        isActive(item.href)
                          ? 'text-primary-600 bg-primary-50'
                          : 'text-gray-700 hover:text-primary-600 hover:bg-gray-50'
                      }`}
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      {item.name}
                    </Link>
                  ))}
                  <button
                    onClick={() => {
                      logout();
                      setMobileMenuOpen(false);
                    }}
                    className="w-full text-left px-3 py-2 text-base font-medium text-gray-700 hover:text-gray-900 transition-colors"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <div className="space-y-2">
                  <Link
                    to="/signup/notifications"
                    className="block px-3 py-2 text-base font-medium text-white rounded-md transition-colors text-center"
                    style={{backgroundColor: '#5086d3'}}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Get Notified
                  </Link>
                  <Link
                    to="/login"
                    className="block px-3 py-2 text-base font-medium text-gray-700 hover:text-gray-900 transition-colors"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Login
                  </Link>
                  <Link
                    to="/register"
                    className="block px-3 py-2 text-base font-medium text-white rounded-md transition-colors text-center"
                    style={{backgroundColor: '#5086d3'}}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Register
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="flex-1">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 flex-shrink-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center">
            <span className="text-sm text-gray-600">
              © 2025 <span className="text-primary-600 font-semibold">Civic Spark AI</span>. Connecting Tulsa residents to city government and neighborhood organizations.
            </span>
          </div>
        </div>
      </footer>

      {/* Chatbot Widget */}
      <ChatbotWidget />
    </div>
  );
};
