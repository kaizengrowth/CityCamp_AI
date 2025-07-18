import React from 'react';
import { useAuth } from '../contexts/AuthContext';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <div className="text-sm text-gray-600">
          Welcome back, {user?.full_name}!
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-2">Upcoming Meetings</h3>
          <p className="text-gray-600">You have 3 upcoming meetings to attend.</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-2">Active Campaigns</h3>
          <p className="text-gray-600">You're participating in 2 campaigns.</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-2">Notifications</h3>
          <p className="text-gray-600">You have 5 unread notifications.</p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
        <div className="space-y-3">
          <div className="flex items-center space-x-3">
            <div className="w-2 h-2 bg-primary-600 rounded-full"></div>
            <span className="text-gray-700">Signed up for City Council meeting notification</span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-2 h-2 bg-primary-600 rounded-full"></div>
            <span className="text-gray-700">Joined the "Better Public Transit" campaign</span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-2 h-2 bg-primary-600 rounded-full"></div>
            <span className="text-gray-700">Updated notification preferences</span>
          </div>
        </div>
      </div>
    </div>
  );
};
