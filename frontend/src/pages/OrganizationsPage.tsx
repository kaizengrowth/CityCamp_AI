import React, { useState, useEffect, useMemo } from 'react';
import { apiRequest, API_ENDPOINTS } from '../config/api';
import toast from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';
import { getEnvironmentConfig } from '../utils/environment';

interface Organization {
  id: number;
  name: string;
  slug: string;
  short_description?: string;
  description: string;
  website_url?: string;
  contact_email?: string;
  phone?: string;
  address?: string;
  organization_type?: string;
  focus_areas?: string[];
  service_areas?: string[];
  facebook_url?: string;
  twitter_handle?: string;
  instagram_handle?: string;
  linkedin_url?: string;
  founded_year?: number;
  member_count?: number;
  is_verified: boolean;
  is_active: boolean;
  created_at: string;
}

interface OrganizationListResponse {
  organizations: Organization[];
  total: number;
  skip: number;
  limit: number;
}

// Backup data for when API is not available (local development)
const BACKUP_ORGANIZATIONS: Organization[] = [
  {
    id: 1,
    name: "Tulsa Community Foundation",
    slug: "tulsa-community-foundation",
    description: "The Tulsa Community Foundation connects generous people with nonprofits and causes they care about to strengthen our community. Since 1952, we have awarded more than $700 million in grants and scholarships to build a stronger, more equitable Tulsa region.",
    short_description: "Connecting generous people with causes to strengthen Tulsa since 1952.",
    website_url: "https://www.tulsacf.org",
    organization_type: "nonprofit",
    focus_areas: ["community_building", "economic_development", "education", "arts_culture"],
    service_areas: ["Greater Tulsa Area", "Northeastern Oklahoma"],
    founded_year: 1952,
    is_verified: true,
    is_active: true,
    contact_email: "info@tulsacf.org",
    address: "7030 S Yale Ave #600, Tulsa, OK 74136",
    created_at: "2024-01-01T00:00:00Z"
  },
  {
    id: 2,
    name: "Terrence Crutcher Foundation",
    slug: "terrence-crutcher-foundation",
    description: "The Terrence Crutcher Foundation works to improve police and community relations through education, advocacy, and community engagement. Founded in memory of Terence Crutcher, we focus on police violence prevention, mental health outreach, and supporting families affected by police violence in Tulsa's Black communities.",
    short_description: "Neighborhood organizing in Tulsa's Black communities, focusing on police violence and mental health outreach.",
    website_url: "https://www.tcrucherfoundation.org",
    organization_type: "nonprofit",
    focus_areas: ["social_justice", "public_safety", "community_building", "healthcare"],
    service_areas: ["North Tulsa", "Tulsa Metro"],
    founded_year: 2016,
    is_verified: true,
    is_active: true,
    created_at: "2024-01-01T00:00:00Z"
  },
  {
    id: 3,
    name: "Growing Together Tulsa",
    slug: "growing-together-tulsa",
    description: "Growing Together Tulsa is a resident-led organization focused on education and housing advocacy in the Kendall-Whittier neighborhood. We work to strengthen our community through neighborhood organizing, educational programs, and affordable housing initiatives that preserve our historic character.",
    short_description: "Resident-led education and housing advocacy centered on Tulsa's Kendall-Whittier neighborhood.",
    website_url: "https://www.growingtogethertulsa.org",
    organization_type: "community_group",
    focus_areas: ["education", "housing", "community_building", "historic_preservation"],
    service_areas: ["Kendall-Whittier"],
    is_verified: true,
    is_active: true,
    created_at: "2024-01-01T00:00:00Z"
  },
  {
    id: 4,
    name: "South Tulsa Community House",
    slug: "south-tulsa-community-house",
    description: "South Tulsa Community House provides vital services like food assistance, computer access, and legal aid to residents of Riverwood and surrounding neighborhoods. We serve as a community hub offering emergency assistance, educational programs, and advocacy for one of Tulsa's most high-need areas.",
    short_description: "Providing vital services like food, computer access, and legal aid in Riverwood, one of Tulsa's most high-need neighborhoods.",
    website_url: "https://www.stulsa.org",
    organization_type: "nonprofit",
    focus_areas: ["social_justice", "community_building", "economic_development", "education"],
    service_areas: ["Riverwood", "South Tulsa"],
    is_verified: true,
    is_active: true,
    contact_email: "info@stulsa.org",
    created_at: "2024-01-01T00:00:00Z"
  },
  {
    id: 5,
    name: "El Centro",
    slug: "el-centro-tulsa",
    description: "El Centro offers immigrant education and resource services in East Tulsa, providing ESL classes, citizenship preparation, community advocacy, and family support services. We serve as a cultural bridge helping immigrant families integrate while preserving their heritage and addressing systemic barriers.",
    short_description: "Offers immigrant education & resource services in East Tulsa.",
    website_url: "https://www.elcentrotulsa.org",
    organization_type: "nonprofit",
    focus_areas: ["education", "social_justice", "community_building"],
    service_areas: ["East Tulsa"],
    is_verified: true,
    is_active: true,
    contact_email: "info@elcentrotulsa.org",
    created_at: "2024-01-01T00:00:00Z"
  },
  {
    id: 6,
    name: "Emergency Infant Services",
    slug: "emergency-infant-services",
    description: "Emergency Infant Services has broad reach among low-income families across Tulsa, providing mothers with essential resources for childcare, including diapers, formula, baby clothing, and parenting education. We work to ensure every baby has what they need to thrive during their critical early months.",
    short_description: "Broad reach among low-income families across Tulsa, providing mothers with resources for childcare.",
    website_url: "https://www.emergencyinfantservices.org",
    organization_type: "nonprofit",
    focus_areas: ["healthcare", "social_justice", "youth_development"],
    service_areas: ["Tulsa Metro"],
    founded_year: 1983,
    is_verified: true,
    is_active: true,
    contact_email: "info@emergencyinfantservices.org",
    created_at: "2024-01-01T00:00:00Z"
  },
  {
    id: 7,
    name: "Oklahomans for Equality",
    slug: "oklahomans-for-equality",
    description: "Oklahomans for Equality (OkEq) serves as a center for LGBTQ+ community organizing and civic engagement in Tulsa. We provide advocacy, education, support services, and community events while working to advance equality and protect civil rights for LGBTQ+ individuals and families.",
    short_description: "Center for LGBTQ+ community organizing and civic engagement.",
    website_url: "https://www.okeq.org",
    organization_type: "advocacy",
    focus_areas: ["social_justice", "community_building", "education"],
    service_areas: ["Tulsa Metro", "Oklahoma"],
    founded_year: 1980,
    is_verified: true,
    is_active: true,
    contact_email: "info@okeq.org",
    created_at: "2024-01-01T00:00:00Z"
  },
  {
    id: 8,
    name: "Tulsa Remote",
    slug: "tulsa-remote",
    description: "Tulsa Remote is a program that brings remote workers to Tulsa by providing financial incentives and community support, helping to grow Tulsa's population and economy. The program offers $10,000 grants, community events, and professional networking opportunities.",
    short_description: "Bringing remote workers to Tulsa to grow our community.",
    website_url: "https://www.tulsaremote.com",
    organization_type: "economic_development",
    focus_areas: ["economic_development", "community_building"],
    founded_year: 2018,
    is_verified: true,
    is_active: true,
    member_count: 3000,
    created_at: "2024-01-01T00:00:00Z"
  }
];

export const OrganizationsPage: React.FC = () => {
  const { user } = useAuth();
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [usingBackupData, setUsingBackupData] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedOrganization, setSelectedOrganization] = useState<Organization | null>(null);
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [focusAreaFilter, setFocusAreaFilter] = useState<string>('all');
  const [verifiedOnly, setVerifiedOnly] = useState(false);
  const [connectedOrganizations, setConnectedOrganizations] = useState<Set<number>>(new Set());
  const [connectingOrganizations, setConnectingOrganizations] = useState<Set<number>>(new Set());

  // Available filter options
  const organizationTypes = [
    { value: 'nonprofit', label: 'Non-Profit Organizations' },
    { value: 'neighborhood', label: 'Neighborhood Associations' },
    { value: 'advocacy', label: 'Advocacy Groups' },
    { value: 'community_group', label: 'Community Groups' },
    { value: 'business_association', label: 'Business Associations' },
    { value: 'educational', label: 'Educational Organizations' },
    { value: 'environmental', label: 'Environmental Groups' },
    { value: 'cultural', label: 'Cultural Organizations' },
    { value: 'economic_development', label: 'Economic Development' },
  ];

  const focusAreas = [
    { value: 'housing', label: 'Housing' },
    { value: 'education', label: 'Education' },
    { value: 'environment', label: 'Environment' },
    { value: 'transportation', label: 'Transportation' },
    { value: 'economic_development', label: 'Economic Development' },
    { value: 'public_safety', label: 'Public Safety' },
    { value: 'healthcare', label: 'Healthcare' },
    { value: 'arts_culture', label: 'Arts & Culture' },
    { value: 'social_justice', label: 'Social Justice' },
    { value: 'community_building', label: 'Community Building' },
    { value: 'historic_preservation', label: 'Historic Preservation' },
    { value: 'youth_development', label: 'Youth Development' },
  ];

  useEffect(() => {
    fetchOrganizations();
  }, []);

  const fetchOrganizations = async () => {
    const environment = getEnvironmentConfig();
    const forceBackup = environment.shouldUseBackupData;
    
    if (forceBackup) {
      console.log('Development mode: Loading backup organization data immediately');
      setLoading(true);

      // Simulate loading delay
      setTimeout(() => {
        setOrganizations(BACKUP_ORGANIZATIONS);
        setUsingBackupData(true);
        setError(null);
        setLoading(false);
        console.log('Backup organization data loaded successfully');
      }, 500);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setUsingBackupData(false);

      console.log('Fetching organizations from API...');

      // Set timeout for API request
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      try {
        const apiPromise = apiRequest<OrganizationListResponse>(
          `${API_ENDPOINTS.organizations}?limit=100&skip=0&active_only=true`
        );

        const response = await apiPromise as OrganizationListResponse;

        console.log('Organizations response received:', response?.organizations?.length || 0, 'organizations');

        if (response?.organizations && Array.isArray(response.organizations) && response.organizations.length > 0) {
          setOrganizations(response.organizations);
          setError(null);
          console.log('Successfully loaded organizations from API');
        } else {
          throw new Error('No organizations data received from API');
        }
      } catch (err) {
        console.error('API error - falling back to backup data:', {
          error: err,
          errorMessage: err instanceof Error ? err.message : 'Unknown error',
        });

        // Use backup data when API fails
        console.log('Using backup organization data for local development');
        setOrganizations(BACKUP_ORGANIZATIONS);
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
      console.log('Using backup organization data for local development');
      setOrganizations(BACKUP_ORGANIZATIONS);
      setUsingBackupData(true);
      setError(null); // Clear error since we have backup data

    } finally {
      setLoading(false);
    }
  };

  // Filtered organizations
  const filteredOrganizations = useMemo(() => {
    return organizations.filter(org => {
      const matchesSearch = org.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           (org.description && org.description.toLowerCase().includes(searchTerm.toLowerCase())) ||
                           (org.short_description && org.short_description.toLowerCase().includes(searchTerm.toLowerCase()));

      const matchesType = typeFilter === 'all' || org.organization_type === typeFilter;
      
      const matchesFocusArea = focusAreaFilter === 'all' || 
                              (org.focus_areas && org.focus_areas.includes(focusAreaFilter));

      const matchesVerified = !verifiedOnly || org.is_verified;

      return matchesSearch && matchesType && matchesFocusArea && matchesVerified;
    });
  }, [organizations, searchTerm, typeFilter, focusAreaFilter, verifiedOnly]);

  const handleOrganizationClick = (organization: Organization) => {
    setSelectedOrganization(organization);
  };

  const handleConnect = (organizationId: number, organizationName: string) => {
    if (!user) {
      toast.error('Please log in to connect with organizations');
      return;
    }

    if (connectingOrganizations.has(organizationId)) return;

    setConnectingOrganizations(prev => new Set(prev).add(organizationId));

    const updateConnection = async (isConnect: boolean) => {
      try {
        const isConnected = connectedOrganizations.has(organizationId);
        
        if (isConnected === isConnect) {
          // Disconnect logic - for now just update local state
          setConnectedOrganizations(prev => {
            const newSet = new Set(prev);
            if (isConnect) newSet.delete(organizationId);
            return newSet;
          });
          toast.success(`Disconnected from ${organizationName}`);
        } else {
          // Connect logic - for now just update local state
          setConnectedOrganizations(prev => new Set(prev).add(organizationId));
          toast.success(`Connected to ${organizationName}! You'll receive updates about their activities.`);
        }
      } catch (error) {
        toast.error('Failed to update connection. Please try again.');
      } finally {
        setConnectingOrganizations(prev => {
          const newSet = new Set(prev);
          newSet.delete(organizationId);
          return newSet;
        });
      }
    };

    updateConnection(true).catch(console.error);
  };

  const getTypeLabel = (type?: string) => {
    const typeObj = organizationTypes.find(t => t.value === type);
    return typeObj ? typeObj.label : type?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Organization';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        <div className="ml-4 text-gray-600">
          Loading organizations...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <div className="ml-3 flex-1">
            <h3 className="text-sm font-medium text-red-800">Error loading organizations</h3>
            <p className="mt-2 text-sm text-red-700">{error}</p>
            <div className="mt-3">
              <button
                onClick={fetchOrganizations}
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
        <h1 className="text-3xl font-bold text-gray-900">Community Organizations</h1>
        <div className="text-sm text-gray-600">
          Discover {filteredOrganizations.length} active community organizations in Tulsa
          {usingBackupData && (
            <div className="mt-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
              ⚠️ Using backup data (API unavailable)
            </div>
          )}
        </div>
      </div>

      {/* Search and Filter Controls */}
      <div className="bg-white p-4 rounded-lg shadow space-y-4">
        <div className="flex flex-col gap-4">
          {/* First row: Search and basic filters */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search organizations..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={verifiedOnly}
                  onChange={(e) => setVerifiedOnly(e.target.checked)}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm text-gray-700">Verified only</span>
              </label>
            </div>
          </div>

          {/* Second row: Type and focus area filters */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="all">All Organization Types</option>
                {organizationTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex-1">
              <select
                value={focusAreaFilter}
                onChange={(e) => setFocusAreaFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="all">All Focus Areas</option>
                {focusAreas.map(area => (
                  <option key={area.value} value={area.value}>
                    {area.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Organizations Grid */}
      <div className="flex gap-6">
        {/* Organizations List */}
        <div className="flex-1">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Organizations
            <span className="ml-2 text-sm font-normal text-gray-500">
              ({filteredOrganizations.length})
            </span>
          </h2>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredOrganizations.length === 0 ? (
              <div className="col-span-full bg-gray-50 rounded-lg p-8 text-center">
                <p className="text-gray-500">No organizations found matching your criteria.</p>
              </div>
            ) : (
              filteredOrganizations.map((org) => (
                <div
                  key={org.id}
                  className={`p-4 rounded-lg shadow cursor-pointer transition-all hover:shadow-md ${
                    selectedOrganization?.id === org.id 
                      ? 'bg-white border border-primary-800 shadow-lg' 
                      : 'bg-[#fdf8f3] hover:bg-white'
                  }`}
                  onClick={() => handleOrganizationClick(org)}
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-lg font-semibold text-gray-900 leading-tight">
                      {org.name}
                    </h3>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleConnect(org.id, org.name);
                      }}
                      disabled={connectingOrganizations.has(org.id)}
                      className={`flex-shrink-0 ml-2 inline-flex items-center px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                        connectedOrganizations.has(org.id)
                          ? 'bg-green-100 text-green-800 hover:bg-green-200'
                          : 'bg-green-100 text-green-800 hover:bg-green-200'
                      } ${connectingOrganizations.has(org.id) ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                    >
                      {connectingOrganizations.has(org.id) ? (
                        '...'
                      ) : connectedOrganizations.has(org.id) ? (
                        '✓ Connected'
                      ) : (
                        '+ Connect'
                      )}
                    </button>
                  </div>

                  <div className="space-y-2 text-sm">
                    <p className="text-gray-600">
                      <span className="font-medium">Type:</span>
                      <span className="ml-1">{getTypeLabel(org.organization_type)}</span>
                    </p>

                    {org.short_description && (
                      <p className="text-gray-700 line-clamp-2">
                        {org.short_description}
                      </p>
                    )}

                    {org.focus_areas && org.focus_areas.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {org.focus_areas.slice(0, 3).map((area, index) => (
                          <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                            {area.replace(/_/g, ' ')}
                          </span>
                        ))}
                        {org.focus_areas.length > 3 && (
                          <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded text-xs">
                            +{org.focus_areas.length - 3} more
                          </span>
                        )}
                      </div>
                    )}

                    {org.website_url && (
                      <div className="mt-2">
                        <a
                          href={org.website_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-primary-600 hover:text-primary-800 text-sm font-medium"
                          onClick={(e) => e.stopPropagation()}
                        >
                          Visit Website →
                        </a>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Organization Details Sidebar */}
        <div className="w-80 flex-shrink-0">
          {selectedOrganization ? (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-start justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">
                  {selectedOrganization.name}
                </h2>
                <button
                  onClick={() => handleConnect(selectedOrganization.id, selectedOrganization.name)}
                  disabled={connectingOrganizations.has(selectedOrganization.id)}
                  className={`inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    connectedOrganizations.has(selectedOrganization.id)
                      ? 'bg-green-100 text-green-800 hover:bg-green-200'
                      : 'bg-green-100 text-green-800 hover:bg-green-200'
                  } ${connectingOrganizations.has(selectedOrganization.id) ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                >
                  {connectingOrganizations.has(selectedOrganization.id) ? (
                    'Loading...'
                  ) : connectedOrganizations.has(selectedOrganization.id) ? (
                    '✓ Connected'
                  ) : (
                    '+ Connect'
                  )}
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-700 leading-relaxed">
                    {selectedOrganization.description}
                  </p>
                </div>

                <div>
                  <h3 className="text-sm font-semibold text-gray-900 mb-2">Organization Type</h3>
                  <p className="text-sm text-gray-600">{getTypeLabel(selectedOrganization.organization_type)}</p>
                </div>

                {selectedOrganization.focus_areas && selectedOrganization.focus_areas.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 mb-2">Focus Areas</h3>
                    <div className="flex flex-wrap gap-1">
                      {selectedOrganization.focus_areas.map((area, index) => (
                        <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                          {area.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {selectedOrganization.service_areas && selectedOrganization.service_areas.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 mb-2">Service Areas</h3>
                    <ul className="text-gray-600 text-sm space-y-1">
                      {selectedOrganization.service_areas.map((area, index) => (
                        <li key={index}>• {area}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="border-t pt-4">
                  <h3 className="text-sm font-semibold text-gray-900 mb-2">Contact Information</h3>
                  <div className="space-y-2 text-sm">
                    {selectedOrganization.website_url && (
                      <div>
                        <span className="font-medium">Website:</span>
                        <a 
                          href={selectedOrganization.website_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="ml-1 text-primary-600 hover:text-primary-800"
                        >
                          Visit Website
                        </a>
                      </div>
                    )}
                    {selectedOrganization.contact_email && (
                      <div>
                        <span className="font-medium">Email:</span>
                        <a 
                          href={`mailto:${selectedOrganization.contact_email}`}
                          className="ml-1 text-primary-600 hover:text-primary-800"
                        >
                          {selectedOrganization.contact_email}
                        </a>
                      </div>
                    )}
                    {selectedOrganization.phone && (
                      <div>
                        <span className="font-medium">Phone:</span>
                        <span className="ml-1 text-gray-600">{selectedOrganization.phone}</span>
                      </div>
                    )}
                    {selectedOrganization.address && (
                      <div>
                        <span className="font-medium">Address:</span>
                        <span className="ml-1 text-gray-600">{selectedOrganization.address}</span>
                      </div>
                    )}
                  </div>
                </div>

                {(selectedOrganization.founded_year || selectedOrganization.member_count) && (
                  <div className="border-t pt-4">
                    <h3 className="text-sm font-semibold text-gray-900 mb-2">Organization Details</h3>
                    <div className="space-y-1 text-sm">
                      {selectedOrganization.founded_year && (
                        <div>
                          <span className="font-medium">Founded:</span>
                          <span className="ml-1 text-gray-600">{selectedOrganization.founded_year}</span>
                        </div>
                      )}
                      {selectedOrganization.member_count && (
                        <div>
                          <span className="font-medium">Members:</span>
                          <span className="ml-1 text-gray-600">{selectedOrganization.member_count.toLocaleString()}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-gray-50 rounded-lg p-8 text-center">
              <p className="text-gray-500">Select an organization to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}; 