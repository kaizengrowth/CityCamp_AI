import React from 'react';

export const NotificationsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Notifications</h1>

      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Recent Notifications</h3>
        <div className="space-y-4">
          <div className="border-b border-gray-200 pb-4">
            <h4 className="font-medium">City Council Meeting Tomorrow</h4>
            <p className="text-gray-600 mt-1">Regular meeting scheduled for January 25, 2024 at 6:00 PM</p>
            <p className="text-sm text-gray-500 mt-2">2 hours ago</p>
          </div>

          <div className="border-b border-gray-200 pb-4">
            <h4 className="font-medium">New Campaign Update</h4>
            <p className="text-gray-600 mt-1">Better Public Transit Initiative reached 150 signatures</p>
            <p className="text-sm text-gray-500 mt-2">1 day ago</p>
          </div>

          <div className="border-b border-gray-200 pb-4">
            <h4 className="font-medium">Budget Committee Meeting</h4>
            <p className="text-gray-600 mt-1">Budget review meeting scheduled for January 30, 2024</p>
            <p className="text-sm text-gray-500 mt-2">3 days ago</p>
          </div>
        </div>
      </div>
    </div>
  );
};
