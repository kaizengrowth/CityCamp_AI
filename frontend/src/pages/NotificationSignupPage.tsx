import React from 'react';
import { NotificationSignup } from '../components/NotificationSignup';

export const NotificationSignupPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4">
        <NotificationSignup />
      </div>
    </div>
  );
};
