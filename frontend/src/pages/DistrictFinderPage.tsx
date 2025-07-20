import React from 'react';
import { DistrictMapper } from '../components/DistrictMapper';

export const DistrictFinderPage: React.FC = () => {
  return (
    <div className="space-y-8">
      <DistrictMapper />

      <div className="bg-blue-50 rounded-xl p-6">
        <h2 className="text-xl font-semibold text-blue-900 mb-4">
          Why Know Your District?
        </h2>
        <div className="grid md:grid-cols-2 gap-6 text-blue-800">
          <div>
            <h3 className="font-medium mb-2">🗳️ Local Representation</h3>
            <p className="text-sm">
              Your City Council member represents your specific neighborhood and
              advocates for local issues that affect your daily life.
            </p>
          </div>
          <div>
            <h3 className="font-medium mb-2">📢 Direct Communication</h3>
            <p className="text-sm">
              Contact your representative directly about local concerns like
              roads, parks, zoning, and neighborhood development.
            </p>
          </div>
          <div>
            <h3 className="font-medium mb-2">📊 Informed Voting</h3>
            <p className="text-sm">
              Stay informed about your representative's positions and voting record
              to make educated decisions during elections.
            </p>
          </div>
          <div>
            <h3 className="font-medium mb-2">🤝 Community Engagement</h3>
            <p className="text-sm">
              Participate in town halls, community meetings, and local initiatives
              organized by your district representative.
            </p>
          </div>
        </div>
      </div>

      <div className="bg-gray-50 rounded-xl p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Additional Resources
        </h2>
        <div className="space-y-3">
          <a
            href="https://www.tulsacouncil.org"
            target="_blank"
            rel="noopener noreferrer"
            className="block p-3 bg-white rounded-lg border hover:border-blue-300 transition-colors"
          >
            <h3 className="font-medium text-gray-900">Tulsa City Council Website</h3>
            <p className="text-sm text-gray-600">
              Official information, meeting agendas, and contact details for all council members.
            </p>
          </a>
          <a
            href="https://cityoftulsa.maps.arcgis.com/apps/webappviewer/index.html?id=d0d03cae97d348b9a67ed1eff92d6ca0"
            target="_blank"
            rel="noopener noreferrer"
            className="block p-3 bg-white rounded-lg border hover:border-blue-300 transition-colors"
          >
            <h3 className="font-medium text-gray-900">Official District Map</h3>
            <p className="text-sm text-gray-600">
              Interactive map showing detailed boundaries for all 9 City Council districts.
            </p>
          </a>
          <a
            href="/contact-representatives"
            className="block p-3 bg-white rounded-lg border hover:border-blue-300 transition-colors"
          >
            <h3 className="font-medium text-gray-900">AI Email Composer</h3>
            <p className="text-sm text-gray-600">
              Use AI to help compose professional emails to your representatives about local issues.
            </p>
          </a>
        </div>
      </div>
    </div>
  );
};
