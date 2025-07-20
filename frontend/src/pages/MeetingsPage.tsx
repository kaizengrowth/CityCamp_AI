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
  const [filter, setFilter] = useState<'all' | 'upcoming' | 'completed'>('all');
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

      // Increase timeout for production
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

      const response = await apiRequest<{meetings: Meeting[], total: number, skip: number, limit: number}>(
        API_ENDPOINTS.meetings,
        { signal: controller.signal }
      );

      clearTimeout(timeoutId);
      console.log('API response received:', response.meetings.length, 'meetings');

      // Only update if we got valid data
      if (response.meetings && Array.isArray(response.meetings)) {
        setMeetings(response.meetings);
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

  // Memoized filtered meetings to prevent recalculation on every render
  const filteredMeetings = useMemo(() => {
    return meetings.filter(meeting => {
      const matchesSearch = meeting.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           (meeting.summary && meeting.summary.toLowerCase().includes(searchTerm.toLowerCase()));

      const now = new Date();
      const meetingDate = new Date(meeting.meeting_date);

      switch (filter) {
        case 'upcoming':
          return matchesSearch && meetingDate >= now;
        case 'completed':
          return matchesSearch && meetingDate < now;
        default:
          return matchesSearch;
      }
    });
  }, [meetings, searchTerm, filter]);

  // Memoized topic and keyword calculations
  const { topTopics, topKeywords } = useMemo(() => {
    const topicCounts: { [key: string]: number } = {};
    const keywordCounts: { [key: string]: number } = {};

    meetings.slice(0, 10).forEach(meeting => {
      if (meeting.topics) {
        meeting.topics.forEach(topic => {
          topicCounts[topic] = (topicCounts[topic] || 0) + 1;
        });
      }
      if (meeting.keywords) {
        meeting.keywords.forEach(keyword => {
          keywordCounts[keyword] = (keywordCounts[keyword] || 0) + 1;
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
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">City Council Meetings</h1>
        <div className="flex gap-2">
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
          <h2 className="text-lg font-semibold text-blue-900 mb-3">Recent Meetings Analysis</h2>
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

      {/* Search and Filter Controls */}
      <div className="bg-white p-4 rounded-lg shadow space-y-4">
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
                  className={`bg-white p-6 rounded-lg shadow cursor-pointer transition-all hover:shadow-md ${
                    selectedMeeting?.id === meeting.id ? 'ring-2 ring-primary-500' : ''
                  }`}
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
