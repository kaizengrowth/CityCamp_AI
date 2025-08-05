import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { format } from 'date-fns';
import { apiRequest, API_ENDPOINTS } from '../config/api';
import { Meeting, AgendaItem, SAMPLE_MEETINGS } from '../data/sampleMeetings';
import toast from 'react-hot-toast';

export const MeetingsPage: React.FC = () => {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMeeting, setSelectedMeeting] = useState<Meeting | null>(null);
  const [filter, setFilter] = useState<'all' | 'upcoming' | 'completed'>('completed');
  const [documentTypeFilter, setDocumentTypeFilter] = useState<'all' | 'agenda' | 'minutes'>('all');
  const [meetingTypeFilter, setMeetingTypeFilter] = useState<string>('all');
  const [dateFilter, setDateFilter] = useState<string>('all'); // New date filter
  const [startDate, setStartDate] = useState<string>(''); // Date range start
  const [endDate, setEndDate] = useState<string>(''); // Date range end
  const [demoMode, setDemoMode] = useState(false);
  const [initialLoadComplete, setInitialLoadComplete] = useState(false);

  // Refs to prevent multiple concurrent API calls
  const fetchingRef = useRef<boolean>(false);
  const fetchingMeetingRef = useRef<number | null>(null);

  useEffect(() => {
    // Only fetch on initial mount
    if (!initialLoadComplete) {
      fetchMeetings();
    }
  }, [initialLoadComplete]);

  const fetchMeetings = async (isRetry = false) => {
    if (fetchingRef.current) return;

    try {
      setLoading(true);
      setError(null);
      fetchingRef.current = true;

      if (isRetry) {
        toast.loading('Retrying...', { id: 'fetch-meetings' });
      }

      console.log('Fetching meetings from API...');

      // Increase timeout for production and fetch more meetings
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 second timeout

      const response = await apiRequest<{meetings: Meeting[], total: number, skip: number, limit: number}>(
        `${API_ENDPOINTS.meetings}?limit=100&skip=0`, // Fetch up to 100 meetings
        { signal: controller.signal }
      );

      clearTimeout(timeoutId);
      console.log('API response received:', response.meetings.length, 'meetings');

      // Only update if we got valid data
      if (response.meetings && Array.isArray(response.meetings)) {
        // Sort meetings chronologically from most recent to farthest back
        const sortedMeetings = response.meetings.sort((a, b) => 
          new Date(b.meeting_date).getTime() - new Date(a.meeting_date).getTime()
        );
        
        setMeetings(sortedMeetings);
        setDemoMode(false);
        setError(null);

        if (isRetry) {
          toast.success('Successfully loaded meetings!', { id: 'fetch-meetings' });
        }
      } else {
        throw new Error('Invalid response format');
      }

    } catch (err) {
      console.error('API error:', {
        error: err,
        errorMessage: err instanceof Error ? err.message : 'Unknown error',
        environment: process.env.NODE_ENV,
        url: window.location.href
      });

      // Only show demo data as fallback, don't auto-retry in production
      if (!isRetry && process.env.NODE_ENV === 'production') {
        console.log('Production: showing demo data as fallback');
        setMeetings(SAMPLE_MEETINGS);
        setDemoMode(true);
        setError(`API temporarily unavailable: ${err instanceof Error ? err.message : 'Unknown error occurred'}. Showing sample data.`);

        // Show subtle notification
        toast.error('Could not load latest data. Showing sample content.', {
          duration: 3000,
          id: 'fetch-meetings'
        });
      } else {
        // Development mode or retry - show error
        setError(`Failed to load meetings: ${err instanceof Error ? err.message : 'Unknown error occurred'}`);
        setMeetings(SAMPLE_MEETINGS);
        setDemoMode(true);

        if (isRetry) {
          toast.error('Still unable to connect. Showing demo data.', { id: 'fetch-meetings' });
        }
      }
    } finally {
      setLoading(false);
      fetchingRef.current = false;
      setInitialLoadComplete(true);
    }
  };

  const fetchMeetingDetails = useCallback(async (meetingId: number) => {
    // Prevent multiple concurrent requests for the same meeting
    if (fetchingMeetingRef.current === meetingId) {
      console.log('Already fetching meeting details for:', meetingId);
      return;
    }

    console.log('fetchMeetingDetails called with meetingId:', meetingId);
    fetchingMeetingRef.current = meetingId;

    try {
      if (demoMode) {
        console.log('Using demo mode, finding meeting:', meetingId);
        const meeting = SAMPLE_MEETINGS.find(m => m.id === meetingId);
        if (meeting) {
          console.log('Found demo meeting:', meeting.title);
          setSelectedMeeting(meeting);
        } else {
          console.error('Demo meeting not found:', meetingId);
          toast.error('Demo meeting not found');
        }
        return;
      }

      console.log('Fetching meeting details from API...');
      const loadingToast = toast.loading('Loading meeting details...', { duration: 0 });

      const response = await apiRequest<{meeting: Meeting, agenda_items: AgendaItem[], categories: any[], pdf_url: string | null}>(
        API_ENDPOINTS.meetingById(meetingId)
      );
      console.log('Meeting response received:', response);

      const meeting = response.meeting;
      meeting.agenda_items = response.agenda_items || [];

      console.log('Meeting fetched successfully:', meeting.title);
      setSelectedMeeting(meeting);
      toast.success('Meeting details loaded', { id: loadingToast });

    } catch (err) {
      console.error('Error fetching meeting details:', {
        error: err,
        meetingId,
        errorMessage: err instanceof Error ? err.message : 'Unknown error',
        demoMode,
        environment: process.env.NODE_ENV
      });

      toast.error(`Failed to load meeting details. Please try again.`);

      // Clear selection to allow retry
      setSelectedMeeting(null);
    } finally {
      // Always reset the fetching ref to allow future clicks
      fetchingMeetingRef.current = null;
    }
  }, [demoMode]);

  // Manual retry function
  const handleRetry = useCallback(() => {
    setInitialLoadComplete(false); // Reset to allow refetch
    fetchMeetings(true);
  }, []);

  // Force refresh function for production
  const handleForceRefresh = useCallback(() => {
    setDemoMode(false);
    setMeetings([]);
    setInitialLoadComplete(false);
    fetchMeetings(true);
  }, []);

  // Enhanced filtered meetings with date filtering and smart sorting
  const filteredMeetings = useMemo(() => {
    const filtered = meetings.filter(meeting => {
      const matchesSearch = meeting.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           (meeting.summary && meeting.summary.toLowerCase().includes(searchTerm.toLowerCase()));

      // Document type filter
      const matchesDocumentType = documentTypeFilter === 'all' ||
                                 (meeting as any).document_type === documentTypeFilter ||
                                 (!((meeting as any).document_type) && documentTypeFilter === 'agenda'); // Default to agenda

      // Meeting type filter
      const matchesMeetingType = meetingTypeFilter === 'all' ||
                               meeting.meeting_type === meetingTypeFilter;

      const now = new Date();
      const meetingDate = new Date(meeting.meeting_date);

      // Time-based filter (upcoming/completed)
      let matchesTimeFilter = true;
      switch (filter) {
        case 'upcoming':
          matchesTimeFilter = meetingDate >= now;
          break;
        case 'completed':
          matchesTimeFilter = meetingDate < now;
          break;
        default:
          matchesTimeFilter = true;
      }

      // Date range filter
      let matchesDateFilter = true;
      if (dateFilter === 'custom' && (startDate || endDate)) {
        if (startDate && endDate) {
          const start = new Date(startDate);
          const end = new Date(endDate);
          end.setHours(23, 59, 59, 999); // Include the entire end date
          matchesDateFilter = meetingDate >= start && meetingDate <= end;
        } else if (startDate) {
          const start = new Date(startDate);
          matchesDateFilter = meetingDate >= start;
        } else if (endDate) {
          const end = new Date(endDate);
          end.setHours(23, 59, 59, 999);
          matchesDateFilter = meetingDate <= end;
        }
      } else if (dateFilter !== 'all' && dateFilter !== 'custom') {
        // Predefined date filters
        const currentYear = now.getFullYear();
        const startOfYear = new Date(currentYear, 0, 1);
        const startOfLastYear = new Date(currentYear - 1, 0, 1);
        const endOfLastYear = new Date(currentYear - 1, 11, 31, 23, 59, 59, 999);
        const thirtyDaysAgo = new Date(now.getTime() - (30 * 24 * 60 * 60 * 1000));
        const ninetyDaysAgo = new Date(now.getTime() - (90 * 24 * 60 * 60 * 1000));

        switch (dateFilter) {
          case 'thisYear':
            matchesDateFilter = meetingDate >= startOfYear;
            break;
          case 'lastYear':
            matchesDateFilter = meetingDate >= startOfLastYear && meetingDate <= endOfLastYear;
            break;
          case 'last30Days':
            matchesDateFilter = meetingDate >= thirtyDaysAgo;
            break;
          case 'last90Days':
            matchesDateFilter = meetingDate >= ninetyDaysAgo;
            break;
          case '2024':
            matchesDateFilter = meetingDate >= new Date(2024, 0, 1) && meetingDate <= new Date(2024, 11, 31, 23, 59, 59, 999);
            break;
          case '2023':
            matchesDateFilter = meetingDate >= new Date(2023, 0, 1) && meetingDate <= new Date(2023, 11, 31, 23, 59, 59, 999);
            break;
          case '2022':
            matchesDateFilter = meetingDate >= new Date(2022, 0, 1) && meetingDate <= new Date(2022, 11, 31, 23, 59, 59, 999);
            break;
          default:
            matchesDateFilter = true;
        }
      }

      return matchesSearch && matchesDocumentType && matchesMeetingType && matchesTimeFilter && matchesDateFilter;
    });

    // Apply smart sorting based on filter type
    return filtered.sort((a, b) => {
      const dateA = new Date(a.meeting_date).getTime();
      const dateB = new Date(b.meeting_date).getTime();
      
      if (filter === 'upcoming') {
        // For upcoming meetings, show soonest first (earliest to latest)
        return dateA - dateB;
      } else {
        // For completed and all meetings, show most recent first (latest to earliest) 
        return dateB - dateA;
      }
    });
  }, [meetings, searchTerm, filter, documentTypeFilter, meetingTypeFilter, dateFilter, startDate, endDate]);

  // Memoized topic and keyword calculations from recent completed meetings
  const { topTopics, topKeywords } = useMemo(() => {
    const topicCounts: { [key: string]: number } = {};
    const keywordCounts: { [key: string]: number } = {};

    // Filter to only completed meetings and take the 5 most recent
    const now = new Date();
    const recentCompletedMeetings = meetings
      .filter(meeting => new Date(meeting.meeting_date) < now)
      .slice(0, 5);

    recentCompletedMeetings.forEach(meeting => {
      // Handle topics (could be array or string depending on data format)
      if (meeting.topics) {
        const topics = Array.isArray(meeting.topics) ? meeting.topics : 
                      typeof meeting.topics === 'string' ? [meeting.topics] : [];
        topics.forEach(topic => {
          if (topic && typeof topic === 'string') {
            topicCounts[topic] = (topicCounts[topic] || 0) + 1;
          }
        });
      }
      
      // Handle keywords (could be array or string depending on data format)
      if (meeting.keywords) {
        const keywords = Array.isArray(meeting.keywords) ? meeting.keywords : 
                        typeof meeting.keywords === 'string' ? [meeting.keywords] : [];
        keywords.forEach(keyword => {
          if (keyword && typeof keyword === 'string') {
            keywordCounts[keyword] = (keywordCounts[keyword] || 0) + 1;
          }
        });
      }
    });

    const topTopics = Object.entries(topicCounts)
      .sort(([,a], [,b]) => (b as number) - (a as number))
      .slice(0, 6);

    const topKeywords = Object.entries(keywordCounts)
      .sort(([,a], [,b]) => (b as number) - (a as number))
      .slice(0, 8);

    return { topTopics, topKeywords };
  }, [meetings]);

  const getMeetingTypeLabel = useCallback((type: string) => {
    const types: Record<string, string> = {
      'regular_council': 'Regular Council',
      'public_works_committee': 'Public Works Committee',
      'urban_economic_committee': 'Urban & Economic Development',
      'budget_committee': 'Budget Committee',
      'planning_commission': 'Planning Commission',
      'board_of_adjustment': 'Board of Adjustment',
      'other': 'Other'
    };
    return types[type] || type;
  }, []);

  const getStatusBadge = useCallback((status: string) => {
    const statusConfig = {
      scheduled: {
        icon: '📅',
        style: 'bg-blue-100 text-blue-800',
        title: 'Upcoming Meeting'
      },
      completed: {
        icon: '✅',
        style: 'bg-green-100 text-green-800',
        title: 'Completed Meeting'
      },
      cancelled: {
        icon: '❌',
        style: 'bg-red-100 text-red-800',
        title: 'Cancelled Meeting'
      },
      postponed: {
        icon: '⏸️',
        style: 'bg-yellow-100 text-yellow-800',
        title: 'Postponed Meeting'
      }
    };

    const config = statusConfig[status as keyof typeof statusConfig] || {
      icon: '📄',
      style: 'bg-gray-100 text-gray-800',
      title: status.charAt(0).toUpperCase() + status.slice(1)
    };

    return (
      <span
        className={`px-2 py-1 text-sm rounded-full ${config.style} flex items-center justify-center`}
        title={config.title}
      >
        {config.icon}
      </span>
    );
  }, []);

  // Optimized click handler with debouncing
  const handleMeetingClick = useCallback((meetingId: number, event: React.MouseEvent) => {
    event.preventDefault();
    event.stopPropagation();

    // Only fetch if not already selected
    if (selectedMeeting?.id !== meetingId) {
      console.log('Meeting clicked:', meetingId);
      fetchMeetingDetails(meetingId);
    }
  }, [selectedMeeting?.id, fetchMeetingDetails]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        <div className="ml-4 text-gray-600">
          Loading meetings...
        </div>
      </div>
    );
  }

  if (error && !demoMode) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <div className="ml-3 flex-1">
            <h3 className="text-sm font-medium text-red-800">Error loading meetings</h3>
            <p className="mt-2 text-sm text-red-700">{error}</p>
            <div className="mt-3 flex gap-2">
              <button
                onClick={handleRetry}
                className="text-sm bg-red-100 text-red-800 px-3 py-1 rounded hover:bg-red-200 transition-colors"
              >
                Try Again
              </button>
              <button
                onClick={() => {
                  setMeetings(SAMPLE_MEETINGS);
                  setDemoMode(true);
                  setError(null);
                }}
                className="text-sm bg-blue-100 text-blue-800 px-3 py-1 rounded hover:bg-blue-200 transition-colors"
              >
                Show Demo Data
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
        <h1 className="text-3xl font-bold text-gray-900">City Council Meetings</h1>
        <div className="text-sm text-gray-600">
          Displaying all {meetings.length} meetings chronologically (most recent first)
        </div>
        <div className="flex justify-center gap-2 mt-2">
          {demoMode && (
            <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-medium">
              Demo Mode
            </span>
          )}
          {(error || demoMode) && (
            <button
              onClick={handleForceRefresh}
              className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium hover:bg-blue-200 transition-colors"
            >
              🔄 Load Latest Data
            </button>
          )}
        </div>
      </div>

      {demoMode && (
        <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
          <div className="flex">
            <div className="ml-3 flex-1">
              <h3 className="text-sm font-medium text-blue-800">
                {error ? 'Demo Mode - API Issue' : 'Demo Mode Active'}
              </h3>
              <p className="mt-2 text-sm text-blue-700">
                {error ?
                  'API connection issue detected. Showing sample data to demonstrate functionality. Click "Load Latest Data" to retry.' :
                  'Showing sample meeting data. This demonstrates how your generated meeting minutes will appear when the backend API is connected.'
                }
              </p>
              <button
                onClick={handleForceRefresh}
                className="mt-2 text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded hover:bg-blue-200 transition-colors"
              >
                Try to load real data
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Most Frequent Topics & Keywords */}
      {!demoMode && meetings.length > 0 && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
          <h2 className="text-lg font-semibold text-blue-900 mb-3">Recent Completed Meetings Analysis</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Most Frequent Topics */}
            <div>
              <h3 className="text-sm font-medium text-blue-800 mb-2">🏷️ Topics</h3>
              <div className="flex flex-wrap gap-1">
                {topTopics.map(([topic, count]) => (
                  <span key={topic} className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
                    {topic.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} ({count})
                  </span>
                ))}
              </div>
            </div>

            {/* Most Frequent Keywords */}
            <div>
              <h3 className="text-sm font-medium text-green-800 mb-2">🔤 Keywords</h3>
              <div className="flex flex-wrap gap-1">
                {topKeywords.map(([keyword, count]) => (
                  <span key={keyword} className="bg-green-100 text-green-800 px-2 py-1 rounded-lg text-xs">
                    {keyword} ({count})
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Enhanced Search and Filter Controls */}
      <div className="bg-white p-4 rounded-lg shadow space-y-4">
        <div className="flex flex-col gap-4">
          {/* First row: Search and basic filters */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search meetings..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value as any)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="all">All Meetings</option>
                <option value="upcoming">Upcoming</option>
                <option value="completed">Completed</option>
              </select>
            </div>
            <div>
              <select
                value={documentTypeFilter}
                onChange={(e) => setDocumentTypeFilter(e.target.value as any)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="all">All Documents</option>
                <option value="agenda">Agendas</option>
                <option value="minutes">Minutes</option>
              </select>
            </div>
          </div>

          {/* Second row: Date selector and meeting type */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div>
              <select
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="all">All Dates</option>
                <option value="last30Days">Last 30 Days</option>
                <option value="last90Days">Last 90 Days</option>
                <option value="thisYear">This Year</option>
                <option value="lastYear">Last Year</option>
                <option value="2024">2024</option>
                <option value="2023">2023</option>
                <option value="2022">2022</option>
                <option value="custom">Custom Range</option>
              </select>
            </div>

            {/* Custom date range inputs */}
            {dateFilter === 'custom' && (
              <>
                <div>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="Start Date"
                  />
                </div>
                <div>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="End Date"
                  />
                </div>
              </>
            )}

            <div className="flex-1">
              <select
                value={meetingTypeFilter}
                onChange={(e) => setMeetingTypeFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="all">All Types</option>
                <optgroup label="Main Council & Committees">
                  <option value="regular_council">Regular Council</option>
                  <option value="budget_committee">Budget Committee</option>
                  <option value="public_works_committee">Public Works</option>
                  <option value="urban_economic_committee">Urban & Economic</option>
                </optgroup>
                <optgroup label="Task Forces & Special Committees">
                  <option value="quality_of_life_task_force">61st & Peoria Quality of Life</option>
                  <option value="capital_improvement_task_force">Capital Improvement</option>
                  <option value="passenger_rail_task_force">Eastern Flyer Rail</option>
                  <option value="hud_grant_committee">HUD Grant Fund</option>
                  <option value="hunger_food_task_force">Hunger & Food</option>
                  <option value="mayor_council_retreat">Mayor-Council Retreat</option>
                  <option value="public_safety_task_force">Public Safety</option>
                  <option value="river_infrastructure_task_force">River Infrastructure</option>
                  <option value="street_lighting_task_force">Street Lighting</option>
                  <option value="food_desert_task_force">Food Desert</option>
                  <option value="tribal_nations_committee">Tribal Nations Relations</option>
                  <option value="truancy_prevention_task_force">Truancy Prevention</option>
                </optgroup>
                <optgroup label="Other">
                  <option value="other">Other</option>
                </optgroup>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Meetings List */}
      <div className="flex gap-6">
        {/* Meetings List Column */}
        <div className="flex-1 flex flex-col">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            {filter === 'all' ? 'All Meetings' :
             filter === 'upcoming' ? 'Upcoming Meetings' : 'Past Meetings'}
            <span className="ml-2 text-sm font-normal text-gray-500">
              ({filteredMeetings.length})
            </span>
          </h2>

          <div className="max-h-[600px] overflow-y-auto space-y-4 pr-2">
            {filteredMeetings.length === 0 ? (
              <div className="bg-gray-50 rounded-lg p-8 text-center">
                <p className="text-gray-500">No meetings found matching your criteria.</p>
                {demoMode && (
                  <button
                    onClick={handleForceRefresh}
                    className="mt-3 text-sm bg-blue-100 text-blue-800 px-3 py-1 rounded hover:bg-blue-200 transition-colors"
                  >
                    Try loading real data
                  </button>
                )}
              </div>
            ) : (
              filteredMeetings.map((meeting) => (
                <div
                  key={meeting.id}
                  className={`p-6 rounded-lg shadow cursor-pointer transition-all hover:shadow-md ${selectedMeeting?.id === meeting.id ? 'bg-white border border-primary-800 shadow-lg' : 'bg-[#fdf8f3]'}`}
                  onClick={(e) => handleMeetingClick(meeting.id, e)}
                >
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="text-lg font-semibold text-gray-900">{meeting.title}</h3>
                    {getStatusBadge(meeting.status)}
                  </div>

                  <div className="space-y-2 text-sm text-gray-600">
                    <p className="flex items-center">
                      <span className="font-medium">Date:</span>
                      <span className="ml-2">
                        {format(new Date(meeting.meeting_date), 'MMMM d, yyyy \'at\' h:mm a')}
                      </span>
                    </p>
                    <p className="flex items-center">
                      <span className="font-medium">Type:</span>
                      <span className="ml-2">{getMeetingTypeLabel(meeting.meeting_type)}</span>
                    </p>
                    <p className="flex items-center">
                      <span className="font-medium">Location:</span>
                      <span className="ml-2">{meeting.location}</span>
                    </p>
                      {meeting.summary && (
                        <div className="flex items-center mb-2">
                          <span className="font-medium">Status:</span>
                          <span className={`ml-2 px-2 py-1 rounded-full text-xs font-medium ${meeting.summary.includes('Minutes imported from PDF') ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
                            {meeting.summary.includes('Minutes imported from PDF') ? '📄 PDF Only' : '🤖 AI Summary'}
                          </span>
                        </div>
                      )}
                      {meeting.topics && meeting.topics.length > 0 && (
                        <div className="mb-2">
                          <span className="font-medium text-gray-700">Topics:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {meeting.topics.slice(0, 3).map((topic, index) => (
                              <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                                {topic.replace(/_/g, ' ')}
                              </span>
                            ))}
                            {meeting.topics.length > 3 && (
                              <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded text-xs">
                                +{meeting.topics.length - 3} more
                              </span>
                            )}
                          </div>
                        </div>
                      )}
                      {meeting.keywords && meeting.keywords.length > 0 && (
                        <div className="mb-2">
                          <span className="font-medium text-gray-700">Keywords:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {meeting.keywords.slice(0, 5).map((keyword, index) => (
                              <span key={index} className="bg-green-50 text-green-700 px-2 py-1 rounded text-xs border border-green-200">
                                {keyword}
                              </span>
                            ))}
                            {meeting.keywords.length > 5 && (
                              <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded text-xs">
                                +{meeting.keywords.length - 5} more
                              </span>
                            )}
                          </div>
                        </div>
                      )}
                  </div>

                  {meeting.agenda_url && (
                    <div className="mt-3">
                      <a
                        href={meeting.agenda_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary-600 hover:text-primary-800 text-sm font-medium"
                        onClick={(e) => e.stopPropagation()}
                      >
                        View Agenda →
                      </a>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Meeting Details Column */}
        <div className="flex-1 flex flex-col">
          {selectedMeeting ? (
            <div className="bg-white rounded-lg shadow">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-xl font-semibold text-gray-900">{selectedMeeting.title}</h2>
                <div className="mt-2">
                  {selectedMeeting.topics && selectedMeeting.topics.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {selectedMeeting.topics.map((topic, index) => (
                        <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
                          {topic.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div className="max-h-[600px] overflow-y-auto">
                {/* Meeting Summary */}
                {selectedMeeting.summary && (
                  <div className="p-6 border-b border-gray-200">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">
                      🤖 AI-Generated Meeting Summary
                    </h3>
                    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
                      <div className="text-sm text-gray-700 leading-relaxed">
                        {selectedMeeting.summary}
                      </div>
                    </div>
                    {selectedMeeting.summary.includes('Minutes imported from PDF') && (
                      <div className="mt-2 text-xs text-yellow-600 bg-yellow-50 px-2 py-1 rounded">
                        ⚠️ This meeting has placeholder content. AI processing may be incomplete.
                      </div>
                    )}
                  </div>
                )}

                {/* AI-Extracted Keywords */}
                {selectedMeeting.keywords && selectedMeeting.keywords.length > 0 && (
                  <div className="p-6 border-b border-gray-200">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">
                      🔤 AI-Extracted Keywords
                    </h3>
                    <div className="flex flex-wrap gap-1">
                      {selectedMeeting.keywords.map((keyword, index) => (
                        <span key={index} className="bg-green-100 text-green-800 px-2 py-1 rounded-lg text-xs">
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Meeting Statistics */}
                <div className="p-6 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Meeting Statistics</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {selectedMeeting.agenda_items?.length || 0}
                      </div>
                      <div className="text-sm text-gray-600">Agenda Items</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {selectedMeeting.topics?.length || 0}
                      </div>
                      <div className="text-sm text-gray-600">Topics Covered</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">
                        {selectedMeeting.keywords?.length || 0}
                      </div>
                      <div className="text-sm text-gray-600">Keywords</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-orange-600">
                        {selectedMeeting.agenda_items?.filter(item => item.vote_result && item.vote_result !== 'none').length || 0}
                      </div>
                      <div className="text-sm text-gray-600">Votes Taken</div>
                    </div>
                  </div>
                </div>

                {/* Agenda Items */}
                {selectedMeeting.agenda_items && selectedMeeting.agenda_items.length > 0 && (
                  <div className="p-6 border-b border-gray-200">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">📋 Agenda Items</h3>
                    <div className="space-y-2">
                      {selectedMeeting.agenda_items.map((item) => (
                        <div key={item.id} className="flex items-start gap-3">
                          <div className="flex-1">
                            <p className="text-gray-900 leading-relaxed">
                              <span className="font-medium">{item.item_number}.</span> {item.title}
                              {item.description && item.description !== item.title && (
                                <span className="text-gray-600"> — {item.description}</span>
                              )}
                            </p>
                          </div>
                          {item.vote_result && (
                            <span className={`px-2 py-1 text-xs rounded-full flex-shrink-0 ${
                              item.vote_result === 'passed' ? 'bg-green-100 text-green-800' :
                              item.vote_result === 'failed' ? 'bg-red-100 text-red-800' :
                              'bg-yellow-100 text-yellow-800'
                            }`}>
                              {item.vote_result}
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-gray-50 rounded-lg p-8 text-center flex-1 flex items-center justify-center">
              <div>
                <p className="text-gray-500">Select a meeting to view details and minutes</p>
                {demoMode && (
                  <p className="text-sm text-gray-400 mt-2">Demo data available for testing</p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
