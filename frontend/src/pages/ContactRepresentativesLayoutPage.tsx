import React from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { ContactRepresentativesPage } from './ContactRepresentativesPage';
import { DistrictFinderPage } from './DistrictFinderPage';

export const ContactRepresentativesLayoutPage: React.FC = () => {
  const location = useLocation();

  const tabs = [
    {
      name: 'Contact Representatives',
      href: '/contact-representatives',
      description: ''
    },
    {
      name: 'Find Your District',
      href: '/contact-representatives/find-district',
      description: ''
    }
  ];

  return (
    <div className="space-y-6 max-w-lg mx-auto">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900">
          Contact Your Representatives
        </h1>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          Connect with your Tulsa City Council representatives. Find your district
          and compose professional emails about local issues that matter to you.
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8 justify-center" aria-label="Tabs">
          {tabs.map((tab) => {
            const isActive = location.pathname === tab.href;
            return (
              <Link
                key={tab.name}
                to={tab.href}
                className={`
                  group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm
                  ${isActive
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <span>{tab.name}</span>
                <span className="ml-2 text-xs text-gray-400 hidden sm:block">
                  {tab.description}
                </span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mt-6">
        <Routes>
          <Route path="/" element={<ContactRepresentativesPage />} />
          <Route path="/find-district" element={<DistrictFinderPage />} />
        </Routes>
      </div>

      {/* Cross-linking Section */}
      <div className="bg-[#fdf8f3] rounded-xl p-6 mt-8">
        <h2 className="text-lg font-semibold text-blue-900 mb-3">
          💡 Get Better Results
        </h2>
        <div className="grid md:grid-cols-2 gap-4 text-blue-800">
          <div>
            <h5 className="font-medium mb-1 text-sm">Start with District Finder</h5>
            <p className="text-sm">
              {location.pathname.includes('find-district') ? (
                <>Use the AI email composer to craft your message after finding your district.</>
              ) : (
                <>Know exactly who to contact by <Link to="/contact-representatives/find-district" className="underline hover:text-blue-900">finding your district first</Link>.</>
              )}
            </p>
          </div>
          <div>
            <h5 className="font-medium mb-1 text-sm">Then Compose Your Email</h5>
            <p className="text-sm">
              {location.pathname.includes('find-district') ? (
                <>Ready to contact your rep? <Link to="/contact-representatives" className="underline hover:text-blue-900">Use our AI email composer</Link> for professional outreach.</>
              ) : (
                <>Let AI help you write a professional, effective email to your representatives.</>
              )}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
