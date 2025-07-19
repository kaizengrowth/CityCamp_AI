import React, { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { apiRequest, API_ENDPOINTS } from '../config/api';
import { Meeting, AgendaItem, SAMPLE_MEETINGS } from '../data/sampleMeetings';



export const MeetingsPage: React.FC = () => {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMeeting, setSelectedMeeting] = useState<Meeting | null>(null);

  // Debug state changes
  useEffect(() => {
    console.log('selectedMeeting state changed:', selectedMeeting ? selectedMeeting.title : 'null');
  }, [selectedMeeting]);
  const [filter, setFilter] = useState<'all' | 'upcoming' | 'completed'>('all');
  const [demoMode, setDemoMode] = useState(false);

  useEffect(() => {
    fetchMeetings();
  }, []);

  const fetchMeetings = async () => {
    try {
      setLoading(true);
      console.log('Fetching meetings from API...');

      // Add a small delay to ensure backend is ready
      await new Promise(resolve => setTimeout(resolve, 1000));

      const response = await apiRequest<{meetings: Meeting[], total: number, skip: number, limit: number}>(API_ENDPOINTS.meetings);
      console.log('API response received:', response.meetings.length, 'meetings');
      console.log('First meeting:', response.meetings[0]);
      setMeetings(response.meetings);
      setDemoMode(false);
      console.log('Demo mode set to false');
    } catch (err) {
      console.log('API not available, using demo data');
      console.error('API error:', err);
      setMeetings(SAMPLE_MEETINGS);
      setDemoMode(true);
      setError(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchMeetingDetails = async (meetingId: number) => {
    console.log('fetchMeetingDetails called with meetingId:', meetingId);

    if (demoMode) {
      console.log('Using demo mode, finding meeting:', meetingId);
      const meeting = SAMPLE_MEETINGS.find(m => m.id === meetingId);
      if (meeting) {
        console.log('Found demo meeting:', meeting.title);
        setSelectedMeeting(meeting);
      }
      return;
    }

    try {
      console.log('Fetching meeting details from API...');
      const response = await apiRequest<{meeting: Meeting, agenda_items: AgendaItem[], categories: any[], pdf_url: string | null}>(API_ENDPOINTS.meetingById(meetingId));
      console.log('Meeting response received:', response);

      const meeting = response.meeting;
      meeting.agenda_items = response.agenda_items || [];

      console.log('Meeting fetched successfully:', meeting.title);
      console.log('Agenda items:', meeting.agenda_items.length);
      console.log('Setting selected meeting:', meeting.title);
      setSelectedMeeting(meeting);
    } catch (err) {
      console.error('Error fetching meeting details:', err);
    }
  };

  const filteredMeetings = meetings.filter(meeting => {
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

  const getMeetingTypeLabel = (type: string) => {
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
  };

  const getStatusBadge = (status: string) => {
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
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error loading meetings</h3>
            <p className="mt-2 text-sm text-red-700">{error}</p>
            <button
              onClick={fetchMeetings}
              className="mt-3 text-sm bg-red-100 text-red-800 px-3 py-1 rounded hover:bg-red-200"
            >
              Try Again
            </button>
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
        </div>
      </div>

      {demoMode && (
        <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">Demo Mode Active</h3>
              <p className="mt-2 text-sm text-blue-700">
                Showing sample meeting data. This demonstrates how your generated meeting minutes will appear when the backend API is connected.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Most Frequent Topics & Keywords */}
      {!demoMode && meetings.length > 0 && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
          <h2 className="text-lg font-semibold text-blue-900 mb-3">Recent Meetings</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Most Frequent Topics */}
            <div>
              <h3 className="text-sm font-medium text-blue-800 mb-2">🏷️ Topics</h3>
              <div className="flex flex-wrap gap-1">
                {(() => {
                  const topicCounts: { [key: string]: number } = {};
                  meetings.slice(0, 10).forEach(meeting => {
                    if (meeting.topics) {
                      meeting.topics.forEach(topic => {
                        topicCounts[topic] = (topicCounts[topic] || 0) + 1;
                      });
                    }
                  });
                  return Object.entries(topicCounts)
                    .sort(([,a], [,b]) => (b as number) - (a as number))
                    .slice(0, 6)
                    .map(([topic, count]) => (
                      <span key={topic} className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
                        {topic.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} ({count})
                      </span>
                    ));
                })()}
              </div>
            </div>

            {/* Most Frequent Keywords */}
            <div>
              <h3 className="text-sm font-medium text-green-800 mb-2">🔤 Keywords</h3>
              <div className="flex flex-wrap gap-1">
                {(() => {
                  const keywordCounts: { [key: string]: number } = {};
                  meetings.slice(0, 10).forEach(meeting => {
                    if (meeting.keywords) {
                      meeting.keywords.forEach(keyword => {
                        keywordCounts[keyword] = (keywordCounts[keyword] || 0) + 1;
                      });
                    }
                  });
                  return Object.entries(keywordCounts)
                    .sort(([,a], [,b]) => (b as number) - (a as number))
                    .slice(0, 8)
                    .map(([keyword, count]) => (
                      <span key={keyword} className="bg-green-100 text-green-800 px-2 py-1 rounded-lg text-xs">
                        {keyword} ({count})
                      </span>
                    ));
                })()}
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
              </div>
            ) : (
              filteredMeetings.map((meeting) => (
                <div
                  key={meeting.id}
                  className={`bg-white p-6 rounded-lg shadow cursor-pointer transition-all hover:shadow-md ${
                    selectedMeeting?.id === meeting.id ? 'ring-2 ring-primary-500' : ''
                  }`}
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('Meeting clicked:', meeting.id, meeting.title);
                    fetchMeetingDetails(meeting.id);
                  }}
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
                {selectedMeeting.agenda_items && selectedMeeting.agenda_items.length > 0 && (
                  <div className="p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Meeting Statistics</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-blue-50 rounded-lg p-4">
                        <div className="text-2xl font-bold text-blue-600">{selectedMeeting.agenda_items.length}</div>
                        <div className="text-sm text-blue-800">Agenda Items</div>
                      </div>
                      <div className="bg-green-50 rounded-lg p-4">
                        <div className="text-2xl font-bold text-green-600">{selectedMeeting.topics ? selectedMeeting.topics.length : 0}</div>
                        <div className="text-sm text-green-800">Topics Covered</div>
                      </div>
                      <div className="bg-purple-50 rounded-lg p-4">
                        <div className="text-2xl font-bold text-purple-600">{selectedMeeting.keywords ? selectedMeeting.keywords.length : 0}</div>
                        <div className="text-sm text-purple-800">Keywords</div>
                      </div>
                      <div className="bg-orange-50 rounded-lg p-4">
                        <div className="text-2xl font-bold text-orange-600">
                          {selectedMeeting.agenda_items ? selectedMeeting.agenda_items.filter(item => item.vote_result).length : 0}
                        </div>
                        <div className="text-sm text-orange-800">Votes Taken</div>
                      </div>
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
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
