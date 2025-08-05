import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ChatbotWidget } from './ChatbotWidget';

const navigation = [
  { name: 'Home', href: '/' },
  { name: 'Meetings', href: '/meetings' },
  { name: 'Organizations', href: '/organizations' },
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
            <Link to="/" className="relative group flex items-center">
              <button className="flex items-center space-x-2 sparkle-effect hover:text-black mb-4 relative">
                <div className="w-12 h-8 bg-brand-yellow rounded-lg flex items-center justify-center hover:text-black">
                  <span className="text-white font-bold text-xs group-hover:text-black">TULSA</span>
                </div>
                <span className="text-xl font-bold text-brand-dark-blue">CivicSpark AI</span>
              </button>
              <div className="absolute mt-24 w-48 bg-white rounded-md shadow-lg z-10 hidden group-hover:block group-focus-within:block">
                <Link to="https://www.tulsacouncil.org" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Tulsa</Link>
                <Link to="https://council.nyc.gov" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">New York City</Link>
              </div>
            </Link>

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
                    className="px-2 sm:px-3 lg:px-4 py-2 text-xs sm:text-sm font-medium text-white bg-brand-medium-blue rounded-md transition-colors hover:bg-brand-red hover:text-white whitespace-nowrap"
                  >
                    <span className="hidden sm:inline">Get Notified</span>
                    <span className="sm:hidden">Notify</span>
                  </Link>
                  <Link
                    to="/login"
                    className="px-2 sm:px-3 lg:px-4 py-2 text-xs sm:text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors whitespace-nowrap"
                  >
                    Login / Register
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
                    className="block px-3 py-2 text-base font-medium text-white bg-brand-medium-blue rounded-md transition-colors text-center"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Get Notified
                  </Link>
                  <Link
                    to="/login"
                    className="block px-3 py-2 text-base font-medium text-gray-700 hover:text-gray-900 transition-colors"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Login / Register
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className={`flex-1 ${location.pathname === '/' ? '' : 'px-4 sm:px-6 lg:px-8 pt-4'}`}>
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 flex-shrink-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center">
            <span className="text-sm text-gray-600">
              © 2025 <span className="text-brand-red font-semibold">CivicSpark AI</span>. Connecting Tulsa and NYC residents to city government and neighborhood organizations.
            </span>
          </div>
        </div>
      </footer>

      {/* Chatbot Widget */}
      <ChatbotWidget />
    </div>
  );
};
