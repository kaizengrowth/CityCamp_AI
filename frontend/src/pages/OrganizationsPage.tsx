import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { apiRequest } from '../config/api';

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

export const OrganizationsPage: React.FC = () => {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedOrganization, setSelectedOrganization] = useState<Organization | null>(null);
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [focusAreaFilter, setFocusAreaFilter] = useState<string>('all');
  const [verifiedOnly, setVerifiedOnly] = useState(false);

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
    try {
      setLoading(true);
      setError(null);

      console.log('Fetching organizations from API...');

      const response = await apiRequest<OrganizationListResponse>(
        `/api/v1/organizations/?limit=100&skip=0&active_only=true`
      );

      console.log('Organizations response received:', response.organizations.length, 'organizations');

      if (response.organizations && Array.isArray(response.organizations)) {
        setOrganizations(response.organizations);
        setError(null);
      } else {
        throw new Error('Invalid response format');
      }

    } catch (err) {
      console.error('API error:', {
        error: err,
        errorMessage: err instanceof Error ? err.message : 'Unknown error',
      });

      setError(`Failed to load organizations: ${err instanceof Error ? err.message : 'Unknown error occurred'}`);
      setOrganizations([]);
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

  const handleOrganizationClick = useCallback((organization: Organization) => {
    setSelectedOrganization(organization);
  }, []);

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
                    {org.is_verified && (
                      <span className="flex-shrink-0 ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        ✓ Verified
                      </span>
                    )}
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
                {selectedOrganization.is_verified && (
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    ✓ Verified
                  </span>
                )}
              </div>

              <div className="space-y-4">
                <div>
                  <p className="text-gray-700 leading-relaxed">
                    {selectedOrganization.description}
                  </p>
                </div>

                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Organization Type</h3>
                  <p className="text-gray-600">{getTypeLabel(selectedOrganization.organization_type)}</p>
                </div>

                {selectedOrganization.focus_areas && selectedOrganization.focus_areas.length > 0 && (
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Focus Areas</h3>
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
                    <h3 className="font-medium text-gray-900 mb-2">Service Areas</h3>
                    <ul className="text-gray-600 text-sm space-y-1">
                      {selectedOrganization.service_areas.map((area, index) => (
                        <li key={index}>• {area}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="border-t pt-4">
                  <h3 className="font-medium text-gray-900 mb-2">Contact Information</h3>
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
                    <h3 className="font-medium text-gray-900 mb-2">Organization Details</h3>
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