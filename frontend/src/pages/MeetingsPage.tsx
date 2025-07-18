import React from 'react';

export const MeetingsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">City Council Meetings</h1>
      
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Upcoming Meetings</h3>
        <div className="space-y-4">
          <div className="border-l-4 border-primary-600 pl-4">
            <h4 className="font-medium">Regular City Council Meeting</h4>
            <p className="text-gray-600">January 25, 2024 at 6:00 PM</p>
            <p className="text-sm text-gray-500">City Hall Council Chamber</p>
          </div>
          <div className="border-l-4 border-primary-600 pl-4">
            <h4 className="font-medium">Budget Committee Meeting</h4>
            <p className="text-gray-600">January 30, 2024 at 2:00 PM</p>
            <p className="text-sm text-gray-500">Committee Room A</p>
          </div>
        </div>
      </div>
    </div>
  );
}; 