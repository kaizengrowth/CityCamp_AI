import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export const HomePage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-0">
      {/* Hero Section */}
      <div className="bg-white py-16 w-full">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left side - Text content */}
            <div className="space-y-8">
              <div className="space-y-6">
                <h1 className="text-5xl md:text-6xl font-bold text-brand-dark-blue">
                  Civic Spark AI
                </h1>
                <p className="text-xl text-gray-600 max-w-lg">
                  Connecting Tulsa residents with city government and community organizations
                </p>
              </div>

              {!user && (
                <div className="flex gap-4">
                  <Link
                    to="/register"
                    className="px-8 py-3 bg-gray-900 text-white font-semibold rounded-lg hover:bg-gray-800 transition-colors"
                  >
                    Get Started
                  </Link>
                  <Link
                    to="/login"
                    className="px-8 py-3 border-2 border-brand-dark-blue text-brand-dark-blue font-semibold rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Sign In
                  </Link>
                </div>
              )}
            </div>

            {/* Right side - Decorative icons */}
            <div className="hidden lg:block relative">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-6">
                  <div className="w-20 h-20 bg-blue-100 rounded-2xl flex items-center justify-center">
                    <svg className="w-10 h-10 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                    </svg>
                  </div>
                  <div className="w-16 h-16 bg-yellow-100 rounded-xl flex items-center justify-center ml-8">
                    <svg className="w-8 h-8 text-yellow-600" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                    </svg>
                  </div>
                </div>
                <div className="space-y-6 mt-8">
                  <div className="w-16 h-16 bg-red-100 rounded-xl flex items-center justify-center">
                    <svg className="w-8 h-8 text-red-600" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
                    </svg>
                  </div>
                  <div className="w-20 h-20 bg-orange-100 rounded-2xl flex items-center justify-center">
                    <svg className="w-10 h-10 text-orange-600" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2l.09.06c.51.35 1.07.54 1.64.54.75 0 1.45-.35 1.89-.95l.03-.05.05-.08c.14-.21.26-.44.35-.68.06-.16.1-.33.12-.5.02-.14.02-.28 0-.42-.05-.38-.21-.73-.45-1.02L12 2zm-1.5 2.5c-.28 0-.5.22-.5.5s.22.5.5.5.5-.22.5-.5-.22-.5-.5-.5zm3 0c-.28 0-.5.22-.5.5s.22.5.5.5.5-.22.5-.5-.22-.5-.5-.5z"/>
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Explore Section */}
      <div className="py-16 bg-brand-dark-blue">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-center text-white mb-12">Explore Civic Spark AI</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {/* Meeting Alerts */}
            <Link
              to="/signup/notifications"
              className="bg-white rounded-lg p-8 text-center hover:shadow-lg transition-shadow group"
            >
              <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-6">
                <svg className="w-8 h-8 text-gray-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.89-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.11-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z"/>
                </svg>
              </div>
                            <h3 className="text-xl font-bold text-brand-dark-blue mb-3">Meeting Alerts</h3>
              <p className="text-gray-600 leading-relaxed">
                Get notified about Tulsa City Council meetings and agenda items that matter to you
              </p>
            </Link>

            {/* AI Assistant */}
            <div
              className="bg-white rounded-lg p-8 text-center hover:shadow-lg transition-shadow cursor-pointer group"
              onClick={() => {
                const chatbotWidget = document.querySelector('.fixed.bottom-4.right-4');
                if (chatbotWidget) {
                  const button = chatbotWidget.querySelector('button');
                  if (button) button.click();
                }
              }}
            >
              <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-6">
                <svg className="w-8 h-8 text-gray-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.94-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                </svg>
              </div>
              <h3 className="text-xl font-bold text-brand-dark-blue mb-3">AI Assistant</h3>
              <p className="text-gray-600 leading-relaxed">
                Ask questions about city government, policies, and get instant answers
              </p>
            </div>

            {/* City Council Meetings */}
            <Link
              to="/meetings"
              className="bg-white rounded-lg p-8 text-center hover:shadow-lg transition-shadow group"
            >
              <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-6">
                <svg className="w-8 h-8 text-gray-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M16 4c0-1.11.89-2 2-2s2 .89 2 2-.89 2-2 2-2-.89-2-2zM4 18v-4h3v4h2v-7.5c0-1.1.9-2 2-2s2 .9 2 2V18h2v-4h3v4h2V9.5c0-1.1-.9-2-2-2h-1.5v-2c0-1.38-1.12-2.5-2.5-2.5S9.5 4.12 9.5 5.5v2H8c-1.1 0-2 .9-2 2V18H4z"/>
                </svg>
              </div>
              <h3 className="text-xl font-bold text-brand-dark-blue mb-3">City Council Meetings</h3>
              <p className="text-gray-600 leading-relaxed">
                Browse upcoming meetings and agendas
              </p>
            </Link>

            {/* Contact Representatives */}
            <Link
              to="/contact-representatives"
              className="bg-white rounded-lg p-8 text-center hover:shadow-lg transition-shadow group"
            >
              <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-6">
                <svg className="w-8 h-8 text-gray-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
                </svg>
              </div>
              <h3 className="text-xl font-bold text-brand-dark-blue mb-3">Contact Representatives</h3>
              <p className="text-gray-600 leading-relaxed">
                Organize and participate in campaigns for issues you care about
              </p>
            </Link>
          </div>
        </div>
      </div>

      {/* Call to Action */}
      {!user && (
        <div className="text-center bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl p-12 text-white">
          <h2 className="text-3xl font-bold mb-4 text-gray-100">
            Ready to get involved?
          </h2>
          <p className="text-xl mb-8 opacity-90 text-gray-200">
            Join hundreds of Tulsa residents staying informed and engaged with their city government.
          </p>
          <Link
            to="/register"
            className="btn bg-white text-primary-600 hover:bg-gray-100 btn-lg px-8 py-3 text-lg font-semibold"
          >
            Create Your Account
          </Link>
        </div>
      )}
    </div>
  );
};
