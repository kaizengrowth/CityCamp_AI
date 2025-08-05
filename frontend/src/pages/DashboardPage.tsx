import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiRequest } from '../config/api';
import toast from 'react-hot-toast';

interface Campaign {
  id: number;
  title: string;
  description: string;
  category: string;
  status: string;
  current_signatures: number;
  target_signatures?: number;
  member_count: number;
  is_member?: boolean;
  membership_role?: string;
}

interface UserCampaignSummary {
  total_subscribed: number;
  active_campaigns: Campaign[];
  recent_updates: number;
}

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [campaignSummary, setCampaignSummary] = useState<UserCampaignSummary | null>(null);
  const [loadingCampaigns, setLoadingCampaigns] = useState(true);

  useEffect(() => {
    if (user) {
      fetchUserCampaigns();
    }
  }, [user]);

  const fetchUserCampaigns = async () => {
    try {
      setLoadingCampaigns(true);
      const response = await apiRequest<UserCampaignSummary>(
        '/api/v1/campaigns/me/subscriptions'
      );
      setCampaignSummary(response);
    } catch (err) {
      console.error('Error fetching user campaigns:', err);
      toast.error('Failed to load your campaigns');
    } finally {
      setLoadingCampaigns(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-brand-dark-blue">Dashboard</h1>
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
          {loadingCampaigns ? (
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-brand-dark-blue mr-2"></div>
              <p className="text-gray-600">Loading...</p>
            </div>
          ) : campaignSummary ? (
            <div>
              <p className="text-gray-600 mb-3">
                You're participating in {campaignSummary.total_subscribed} {campaignSummary.total_subscribed === 1 ? 'campaign' : 'campaigns'}.
              </p>
              {campaignSummary.active_campaigns.length > 0 && (
                <div className="space-y-2">
                  {campaignSummary.active_campaigns.slice(0, 3).map((campaign) => (
                    <div key={campaign.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <div>
                        <p className="text-sm font-medium text-brand-dark-blue">{campaign.title}</p>
                        <p className="text-xs text-gray-500">{campaign.category}</p>
                      </div>
                      <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                        {campaign.membership_role}
                      </span>
                    </div>
                  ))}
                  {campaignSummary.active_campaigns.length > 3 && (
                    <p className="text-xs text-gray-500 text-center pt-2">
                      +{campaignSummary.active_campaigns.length - 3} more campaigns
                    </p>
                  )}
                </div>
              )}
            </div>
          ) : (
            <p className="text-gray-600">No active campaigns found.</p>
          )}
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
