import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export const HomePage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <div className="text-center space-y-6">
        <div className="space-y-4">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 gradient-text">
            CityCamp AI
          </h1>
          <p className="text-xl md:text-2xl text-gray-600 max-w-3xl mx-auto">
            Connecting Tulsa residents with city government and neighborhood organizations.
          </p>
        </div>

        {!user && (
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register"
              className="btn btn-primary btn-lg px-8 py-3 text-lg"
            >
              Get Started
            </Link>
            <Link
              to="/login"
              className="btn btn-outline btn-lg px-8 py-3 text-lg"
            >
              Sign In
            </Link>
          </div>
        )}
      </div>

      {/* Features Section */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
        <Link
          to="/signup/notifications"
          className="card p-6 text-center hover:shadow-lg transition-shadow cursor-pointer group"
        >
          <div className="w-12 h-12 bg-primary-100 group-hover:bg-primary-200 rounded-lg flex items-center justify-center mx-auto mb-4 transition-colors">
            <span className="text-2xl">📅</span>
          </div>
          <h3 className="text-xl font-semibold mb-2 group-hover:text-primary-600 transition-colors">Meeting Alerts</h3>
          <p className="text-gray-600">
            Get notified about Tulsa City Council meetings and agenda items that matter to you.
          </p>
        </Link>

        <div className="card p-6 text-center hover:shadow-lg transition-shadow cursor-pointer group" onClick={() => {
          // Scroll to chatbot or trigger chatbot
          const chatbotWidget = document.querySelector('.fixed.bottom-4.right-4');
          if (chatbotWidget) {
            const button = chatbotWidget.querySelector('button');
            if (button) button.click();
          }
        }}>
          <div className="w-12 h-12 bg-primary-100 group-hover:bg-primary-200 rounded-lg flex items-center justify-center mx-auto mb-4 transition-colors">
            <span className="text-2xl">🤖</span>
          </div>
          <h3 className="text-xl font-semibold mb-2 group-hover:text-primary-600 transition-colors">AI Assistant</h3>
          <p className="text-gray-600">
            Ask questions about city government, policies, and get instant answers.
          </p>
        </div>

        <Link
          to="/campaigns"
          className="card p-6 text-center hover:shadow-lg transition-shadow cursor-pointer group"
        >
          <div className="w-12 h-12 bg-primary-100 group-hover:bg-primary-200 rounded-lg flex items-center justify-center mx-auto mb-4 transition-colors">
            <span className="text-2xl">📢</span>
          </div>
          <h3 className="text-xl font-semibold mb-2 group-hover:text-primary-600 transition-colors">Community Campaigns</h3>
          <p className="text-gray-600">
            Organize and participate in campaigns for issues you care about.
          </p>
        </Link>

        <Link
          to="/contact-representatives"
          className="card p-6 text-center hover:shadow-lg transition-shadow cursor-pointer group"
        >
          <div className="w-12 h-12 bg-primary-100 group-hover:bg-primary-200 rounded-lg flex items-center justify-center mx-auto mb-4 transition-colors">
            <span className="text-2xl">✉️</span>
          </div>
          <h3 className="text-xl font-semibold mb-2 group-hover:text-primary-600 transition-colors">Contact Representatives</h3>
          <p className="text-gray-600">
            AI-powered email generation to help you reach out to your representatives.
          </p>
        </Link>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl p-8 shadow-sm">
        <h2 className="text-3xl font-bold text-center mb-8">Explore CityCamp AI</h2>
        <div className="grid md:grid-cols-3 gap-6">
          <Link
            to="/meetings"
            className="group p-6 rounded-lg border-2 border-gray-200 hover:border-primary-300 transition-colors"
          >
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white text-xl">📅</span>
              </div>
              <div>
                <h3 className="text-lg font-semibold group-hover:text-primary-600">
                  City Council Meetings
                </h3>
                <p className="text-gray-600">
                  Browse upcoming meetings and agendas
                </p>
              </div>
            </div>
          </Link>

          <Link
            to="/campaigns"
            className="group p-6 rounded-lg border-2 border-gray-200 hover:border-primary-300 transition-colors"
          >
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white text-xl">📢</span>
              </div>
              <div>
                <h3 className="text-lg font-semibold group-hover:text-primary-600">
                  Active Campaigns
                </h3>
                <p className="text-gray-600">
                  Join campaigns in your community
                </p>
              </div>
            </div>
          </Link>

          <Link
            to="/chatbot"
            className="group p-6 rounded-lg border-2 border-gray-200 hover:border-primary-300 transition-colors"
          >
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white text-xl">🤖</span>
              </div>
              <div>
                <h3 className="text-lg font-semibold group-hover:text-primary-600">
                  AI Assistant
                </h3>
                <p className="text-gray-600">
                  Get answers about city government
                </p>
              </div>
            </div>
          </Link>
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
