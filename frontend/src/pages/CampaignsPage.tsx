import React from 'react';

export const CampaignsPage: React.FC = () => {
  return (
    <div className="space-y-6 max-w-lg mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 text-center">Community Campaigns</h1>

      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Active Campaigns</h3>
        <div className="space-y-4">
          <div className="border border-gray-200 rounded-lg p-4 bg-[#fdf8f3]">
            <h4 className="font-medium">Better Public Transit Initiative</h4>
            <p className="text-gray-600 mt-2">Supporting improved bus routes and schedules for Tulsa residents.</p>
            <div className="mt-3 flex items-center space-x-4">
              <span className="text-sm text-gray-500">124 signatures</span>
              <span className="text-sm text-gray-500">Goal: 500</span>
            </div>
          </div>

          <div className="border border-gray-200 rounded-lg p-4 bg-[#fdf8f3]">
            <h4 className="font-medium">Parks & Recreation Funding</h4>
            <p className="text-gray-600 mt-2">Increase funding for park maintenance and youth programs.</p>
            <div className="mt-3 flex items-center space-x-4">
              <span className="text-sm text-gray-500">87 signatures</span>
              <span className="text-sm text-gray-500">Goal: 250</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
