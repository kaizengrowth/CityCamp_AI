import React, { useState, useEffect } from 'react';
import { apiRequest } from '../config/api';
import toast from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';
import { getEnvironmentConfig } from '../utils/environment';
import { LoginModal } from '../components/auth/LoginModal';

interface Campaign {
  id: number;
  title: string;
  description: string;
  category: string;
  target_date?: string;
  status: string;
  is_member?: boolean;
  created_at: string;
}

interface CampaignListResponse {
  campaigns: Campaign[];
  total: number;
}

// Backup data for when API is not available (local development)
const BACKUP_CAMPAIGNS: Campaign[] = [
  {
    id: 1,
    title: "Affordable Housing Initiative",
    description: "Advocating for more affordable housing options in Tulsa through policy reform and community development partnerships. Join us in pushing for zoning changes that allow for diverse housing types and rent stabilization measures.",
    category: "Housing",
    target_date: "2024-06-30",
    status: "active",
    is_member: false,
    created_at: "2024-01-15T00:00:00Z"
  },
  {
    id: 2,
    title: "Transit Equity Campaign",
    description: "Working to improve public transportation access for underserved communities in Tulsa. We're advocating for better bus routes, reduced fares for low-income residents, and accessible infrastructure improvements.",
    category: "Transportation",
    target_date: "2024-08-15",
    status: "active",
    is_member: false,
    created_at: "2024-02-01T00:00:00Z"
  },
  {
    id: 3,
    title: "Community Solar Project",
    description: "Bringing clean, affordable solar energy to Tulsa neighborhoods through community-owned solar gardens. Help us advocate for policies that make renewable energy accessible to all residents, regardless of income level.",
    category: "Environment",
    target_date: "2024-09-30",
    status: "active",
    is_member: false,
    created_at: "2024-01-10T00:00:00Z"
  },
  {
    id: 4,
    title: "Criminal Justice Reform",
    description: "Advocating for police accountability, bail reform, and restorative justice programs in Tulsa. Join our efforts to create a more equitable justice system that prioritizes community safety and rehabilitation over punishment.",
    category: "Justice",
    target_date: "2024-12-31",
    status: "active",
    is_member: false,
    created_at: "2024-03-01T00:00:00Z"
  },
  {
    id: 5,
    title: "Digital Divide Initiative",
    description: "Ensuring all Tulsa residents have access to high-speed internet and digital literacy resources. We're working with city council to expand broadband infrastructure and create community tech centers in underserved areas.",
    category: "Technology",
    target_date: "2024-07-31",
    status: "active",
    is_member: false,
    created_at: "2024-02-15T00:00:00Z"
  },
  {
    id: 6,
    title: "Food Justice Coalition",
    description: "Fighting food apartheid in Tulsa by advocating for grocery stores in food deserts, supporting urban agriculture, and pushing for policies that make healthy food accessible and affordable for all residents.",
    category: "Health",
    target_date: "2024-10-15",
    status: "active",
    is_member: false,
    created_at: "2024-01-20T00:00:00Z"
  }
];

export const CampaignsPage: React.FC = () => {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [usingBackupData, setUsingBackupData] = useState(false);
  const [joiningCampaigns, setJoiningCampaigns] = useState<Set<number>>(new Set());
  const { user } = useAuth();
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
    const environment = getEnvironmentConfig();
    const forceBackup = environment.shouldUseBackupData;

    if (forceBackup) {
      console.log('Development mode: Loading backup campaign data immediately');
      setLoading(true);

      // Simulate loading delay
      setTimeout(() => {
        setCampaigns(BACKUP_CAMPAIGNS);
        setUsingBackupData(true);
        setError(null);
        setLoading(false);
        console.log('Backup campaign data loaded successfully');
      }, 500);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setUsingBackupData(false);

      console.log('Fetching campaigns from API...');

      // Set timeout for API request
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      try {
        const response = await apiRequest<CampaignListResponse>('/api/v1/campaigns/');

        console.log('Campaigns response received:', response?.campaigns?.length || 0, 'campaigns');

        if (response?.campaigns && Array.isArray(response.campaigns)) {
          setCampaigns(response.campaigns);
          setError(null);
          console.log('Successfully loaded campaigns from API');
        } else {
          throw new Error('No campaigns data received from API');
        }
      } catch (err) {
        console.error('API error - falling back to backup data:', {
          error: err,
          errorMessage: err instanceof Error ? err.message : 'Unknown error',
        });

        // Use backup data when API fails
        console.log('Using backup campaign data for local development');
        setCampaigns(BACKUP_CAMPAIGNS);
        setUsingBackupData(true);
        setError(null); // Clear error since we have backup data
      } finally {
        clearTimeout(timeoutId);
      }

    } catch (err) {
      console.error('API error - falling back to backup data:', {
        error: err,
        errorMessage: err instanceof Error ? err.message : 'Unknown error',
      });

      // Use backup data when API fails
      console.log('Using backup campaign data for local development');
      setCampaigns(BACKUP_CAMPAIGNS);
      setUsingBackupData(true);
      setError(null); // Clear error since we have backup data

    } finally {
      setLoading(false);
    }
  };

  const handleJoinCampaign = async (campaignId: number, campaignTitle: string) => {
    if (!user) {
      setIsLoginModalOpen(true);
      return;
    }

    if (usingBackupData) {
      // Simulate joining when using backup data
      setJoiningCampaigns(prev => new Set([...prev, campaignId]));

      setTimeout(() => {
        setCampaigns(prev => prev.map(campaign =>
          campaign.id === campaignId
            ? { ...campaign, is_member: true }
            : campaign
        ));
        setJoiningCampaigns(prev => {
          const newSet = new Set(prev);
          newSet.delete(campaignId);
          return newSet;
        });
        toast.success(`Successfully joined "${campaignTitle}"!`);
      }, 1000);
      return;
    }

    try {
      setJoiningCampaigns(prev => new Set([...prev, campaignId]));

      await apiRequest(`/api/v1/campaigns/${campaignId}/join`, {
        method: 'POST'
      });

      // Update the campaign's membership status
      setCampaigns(prev => prev.map(campaign =>
        campaign.id === campaignId
          ? { ...campaign, is_member: true }
          : campaign
      ));

      toast.success(`Successfully joined "${campaignTitle}"!`);
    } catch (error) {
      console.error('Error joining campaign:', error);
      toast.error('Failed to join campaign. Please try again.');
    } finally {
      setJoiningCampaigns(prev => {
        const newSet = new Set(prev);
        newSet.delete(campaignId);
        return newSet;
      });
    }
  };

  const getCategoryIcon = (category: string) => {
    const icons: { [key: string]: string } = {
      'Housing': '🏠',
      'Transportation': '🚌',
      'Environment': '🌱',
      'Justice': '⚖️',
      'Technology': '💻',
      'Health': '🏥',
      'Education': '📚',
      'Economic': '💼'
    };
    return icons[category] || '📋';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-dark-blue"></div>
        <div className="ml-4 text-gray-600">
          Loading campaigns...
        </div>
      </div>
    );
  }

  if (error && !usingBackupData) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <div className="ml-3 flex-1">
            <h3 className="text-sm font-medium text-red-800">Error loading campaigns</h3>
            <p className="mt-2 text-sm text-red-700">{error}</p>
            <div className="mt-3">
              <button
                onClick={fetchCampaigns}
                className="text-sm bg-red-100 text-red-800 px-3 py-1 rounded hover:bg-red-200 transition-colors"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="space-y-6 text-center">
        <h1 className="text-3xl font-bold text-brand-dark-blue">Community Campaigns</h1>
        <div className="text-sm text-gray-600">
          Join active advocacy campaigns and make your voice heard in Tulsa
          {usingBackupData && (
            <div className="mt-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
              ⚠️ Using sample data (API unavailable)
            </div>
          )}
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {campaigns.map((campaign) => (
          <div
            key={campaign.id}
            className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-2">
                <span className="text-2xl">{getCategoryIcon(campaign.category)}</span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {campaign.category}
                </span>
              </div>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 capitalize">
                {campaign.status}
              </span>
            </div>

            <h3 className="text-xl font-semibold text-brand-dark-blue mb-3">
              {campaign.title}
            </h3>

            <p className="text-gray-600 mb-4 text-sm leading-relaxed">
              {campaign.description}
            </p>

            {campaign.target_date && (
              <div className="text-xs text-gray-500 mb-4">
                Target Date: {new Date(campaign.target_date).toLocaleDateString()}
              </div>
            )}

            <div className="flex justify-between items-center">
              <div className="text-xs text-gray-400">
                Created {new Date(campaign.created_at).toLocaleDateString()}
              </div>

              <button
                onClick={() => handleJoinCampaign(campaign.id, campaign.title)}
                disabled={campaign.is_member || joiningCampaigns.has(campaign.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  campaign.is_member
                    ? 'bg-green-100 text-green-800 cursor-default'
                    : joiningCampaigns.has(campaign.id)
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-brand-dark-blue text-white hover:bg-brand-red'
                }`}
              >
                {campaign.is_member ? '✓ Joined' :
                 joiningCampaigns.has(campaign.id) ? 'Joining...' :
                 'Join Campaign'}
              </button>
            </div>
          </div>
        ))}
      </div>

      {campaigns.length === 0 && !loading && (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">📢</div>
          <h3 className="text-lg font-medium text-brand-dark-blue mb-2">No campaigns available</h3>
          <p className="text-gray-600">Check back later for new advocacy campaigns.</p>
        </div>
      )}

      <LoginModal
        isOpen={isLoginModalOpen}
        onClose={() => setIsLoginModalOpen(false)}
        onSuccess={() => {
          setIsLoginModalOpen(false);
          fetchCampaigns(); // Re-fetch campaigns after successful login
        }}
        title="Sign In to Join Campaign"
        message="Please sign in to join campaigns and help advocate for important issues in Tulsa."
      />
    </div>
  );
};
