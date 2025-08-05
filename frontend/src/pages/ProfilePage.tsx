import React from 'react';
import { useAuth } from '../contexts/AuthContext';

export const ProfilePage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-brand-dark-blue">Profile</h1>

      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Personal Information</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Full Name</label>
            <p className="mt-1 text-brand-dark-blue">{user?.full_name}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <p className="mt-1 text-brand-dark-blue">{user?.email}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Username</label>
            <p className="mt-1 text-brand-dark-blue">{user?.username}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Phone Number</label>
            <p className="mt-1 text-brand-dark-blue">{user?.phone_number || 'Not provided'}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">ZIP Code</label>
            <p className="mt-1 text-brand-dark-blue">{user?.zip_code || 'Not provided'}</p>
          </div>
        </div>
      </div>
    </div>
  );
};
