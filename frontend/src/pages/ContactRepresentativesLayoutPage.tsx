import React from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { ContactRepresentativesPage } from './ContactRepresentativesPage';
import { DistrictFinderPage } from './DistrictFinderPage';
import { PageHeader } from '../components/PageHeader';

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
    <div className="space-y-4 max-w-7xl mx-auto">
      {/* Header */}
      <PageHeader
        title="Contact Your Representatives"
        description="Connect with your Tulsa City Council representatives. Find your district and compose professional emails about local issues that matter to you."
      />

      {/* Tab Navigation */}
      <div className="max-w-xl mx-auto">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 justify-center" aria-label="Tabs">
            {tabs.map((tab) => {
              const isActive = location.pathname === tab.href;
              return (
                <Link
                  key={tab.name}
                  to={tab.href}
                  className={`
                    group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm focus:outline-none
                    ${isActive
                      ? 'border-brand-red text-brand-red focus:text-brand-red'
                      : 'border-transparent text-gray-500 hover:text-brand-dark-blue hover:border-gray-300 focus:text-brand-dark-blue'
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
          <h2 className="text-lg font-semibold text-brand-dark-blue mb-3">
            💡 Get Better Results
          </h2>
          <div className="grid md:grid-cols-2 gap-4 text-brand-dark-blue">
            <div>
              <h5 className="font-medium mb-1 text-sm">Start with District Finder</h5>
              <p className="text-sm">
                {location.pathname.includes('find-district') ? (
                  <>Use the AI email composer to craft your message after finding your district.</>
                ) : (
                  <>Know exactly who to contact by <Link to="/contact-representatives/find-district" className="underline hover:text-brand-red text-brand-dark-blue">finding your district first</Link>.</>
                )}
              </p>
            </div>
            <div>
              <h5 className="font-medium mb-1 text-sm">Then Compose Your Email</h5>
              <p className="text-sm">
                {location.pathname.includes('find-district') ? (
                  <>Ready to contact your rep? <Link to="/contact-representatives" className="underline hover:text-brand-red text-brand-dark-blue">Use our AI email composer</Link> for professional outreach.</>
                ) : (
                  <>Let AI help you write a professional, effective email to your representatives.</>
                )}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
