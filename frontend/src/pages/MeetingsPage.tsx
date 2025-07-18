import React, { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { apiRequest, API_ENDPOINTS } from '../config/api';

interface AgendaItem {
  id: number;
  item_number: string;
  title: string;
  description?: string;
  item_type?: string;
  vote_required: boolean;
  vote_result?: string;
}

interface Meeting {
  id: number;
  title: string;
  meeting_date: string;
  location: string;
  meeting_type: string;
  status: string;
  agenda_url?: string;
  summary?: string;
  agenda_items?: AgendaItem[];
}

// Sample data for demo purposes
const SAMPLE_MEETINGS: Meeting[] = [
  {
    id: 1,
    title: "Regular City Council Meeting",
    meeting_date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    location: "One Technology Center, Tulsa, OK",
    meeting_type: "regular_council",
    status: "completed",
    agenda_url: "https://example.com/agenda",
    summary: `TULSA CITY COUNCIL MEETING MINUTES
January 15, 2025

CALL TO ORDER
The Regular Meeting of the Tulsa City Council was called to order at 5:00 PM by Council Chair.

ROLL CALL
Present: Councilors District 1-9
Absent: None

AGENDA ITEMS DISCUSSED:

1. BUDGET APPROPRIATIONS
   - Motion to approve $2.3M for street repairs
   - Passed 8-1

2. ZONING CHANGES
   - Rezoning request for 71st Street corridor
   - Public hearing held
   - Approved unanimously

3. PUBLIC SAFETY INITIATIVES
   - New police substations proposal
   - Community policing expansion
   - Approved with amendments

4. INFRASTRUCTURE PROJECTS
   - Bridge maintenance funding
   - Water system upgrades
   - Road resurfacing schedule

CITIZEN COMMENTS:
- 12 citizens spoke on various issues
- Main concerns: traffic, housing, parks

ADJOURNMENT: 7:45 PM

Meeting recorded and available online.`,
    agenda_items: [
      {
        id: 1,
        item_number: "1",
        title: "Budget Appropriations",
        description: "Review and approve city budget items",
        item_type: "motion",
        vote_required: true,
        vote_result: "passed"
      },
      {
        id: 2,
        item_number: "2",
        title: "Zoning Changes",
        description: "71st Street corridor rezoning proposal",
        item_type: "ordinance",
        vote_required: true,
        vote_result: "passed"
      },
      {
        id: 3,
        item_number: "3",
        title: "Public Safety",
        description: "New police substation locations",
        item_type: "presentation",
        vote_required: false,
        vote_result: undefined
      },
      {
        id: 4,
        item_number: "4",
        title: "Citizen Comments",
        description: "Public comment period",
        item_type: "public_comment",
        vote_required: false,
        vote_result: undefined
      }
    ]
  },
  {
    id: 2,
    title: "Public Works Committee Meeting",
    meeting_date: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    location: "City Hall Committee Room",
    meeting_type: "public_works_committee",
    status: "completed",
    summary: `PUBLIC WORKS COMMITTEE MINUTES
January 19, 2025

ATTENDEES:
Committee Chair, Committee Members, Public Works Director

AGENDA:

1. STREET MAINTENANCE REPORT
   - Winter road conditions update
   - Salt/sand usage statistics
   - Equipment status report

2. UPCOMING PROJECTS
   - Spring pothole repair schedule
   - Sidewalk improvement program
   - Traffic signal upgrades at 5 intersections

3. BUDGET REVIEW
   - Q1 spending analysis
   - Equipment replacement needs
   - Emergency repair fund status

4. CITIZEN REQUESTS
   - 23 new service requests reviewed
   - Priority ranking established
   - Response timeline set

ACTIONS TAKEN:
- Approved emergency road repair contract
- Authorized traffic study for Yale Avenue
- Scheduled public hearing for bike lane proposal

NEXT MEETING: February 2, 2025`,
    agenda_items: [
      {
        id: 5,
        item_number: "1",
        title: "Street Maintenance",
        description: "Winter road maintenance report",
        item_type: "report",
        vote_required: false,
        vote_result: undefined
      },
      {
        id: 6,
        item_number: "2",
        title: "Project Updates",
        description: "Upcoming infrastructure projects",
        item_type: "presentation",
        vote_required: false,
        vote_result: undefined
      },
      {
        id: 7,
        item_number: "3",
        title: "Budget Review",
        description: "Q1 budget analysis",
        item_type: "report",
        vote_required: false,
        vote_result: undefined
      }
    ]
  },
  {
    id: 3,
    title: "Urban & Economic Development Committee",
    meeting_date: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString(),
    location: "One Technology Center",
    meeting_type: "urban_economic_committee",
    status: "scheduled",
    agenda_items: [
      {
        id: 8,
        item_number: "1",
        title: "Economic Development",
        description: "New business incentives",
        item_type: "discussion",
        vote_required: false,
        vote_result: undefined
      },
      {
        id: 9,
        item_number: "2",
        title: "Urban Planning",
        description: "Downtown revitalization",
        item_type: "presentation",
        vote_required: false,
        vote_result: undefined
      }
    ]
  }
];

export const MeetingsPage: React.FC = () => {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMeeting, setSelectedMeeting] = useState<Meeting | null>(null);
  const [filter, setFilter] = useState<'all' | 'upcoming' | 'completed'>('all');
  const [demoMode, setDemoMode] = useState(false);

  useEffect(() => {
    fetchMeetings();
  }, []);

  const fetchMeetings = async () => {
    try {
      setLoading(true);
      const data = await apiRequest<Meeting[]>(API_ENDPOINTS.meetings);
      setMeetings(data);
      setDemoMode(false);
    } catch (err) {
      console.log('API not available, using demo data');
      setMeetings(SAMPLE_MEETINGS);
      setDemoMode(true);
      setError(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchMeetingDetails = async (meetingId: number) => {
    if (demoMode) {
      const meeting = SAMPLE_MEETINGS.find(m => m.id === meetingId);
      if (meeting) {
        setSelectedMeeting(meeting);
      }
      return;
    }

    try {
      const meeting = await apiRequest<Meeting>(API_ENDPOINTS.meetingById(meetingId));

      // Fetch agenda items
      try {
        meeting.agenda_items = await apiRequest<AgendaItem[]>(API_ENDPOINTS.meetingAgendaItems(meetingId));
      } catch (agendaErr) {
        console.log('No agenda items found for this meeting');
        meeting.agenda_items = [];
      }

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
    const styles = {
      scheduled: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800',
      postponed: 'bg-yellow-100 text-yellow-800'
    };

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${styles[status as keyof typeof styles] || 'bg-gray-100 text-gray-800'}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
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
          <button
            onClick={fetchMeetings}
            className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700"
          >
            Refresh
          </button>
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
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Meetings List Column */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900">
            {filter === 'all' ? 'All Meetings' :
             filter === 'upcoming' ? 'Upcoming Meetings' : 'Past Meetings'}
            <span className="ml-2 text-sm font-normal text-gray-500">
              ({filteredMeetings.length})
            </span>
          </h2>

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
                onClick={() => fetchMeetingDetails(meeting.id)}
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
                    <p className="flex items-center">
                      <span className="font-medium">Minutes:</span>
                      <span className="ml-2 text-green-600">Available</span>
                    </p>
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

        {/* Meeting Details Column */}
        <div className="lg:sticky lg:top-6">
          {selectedMeeting ? (
            <div className="bg-white rounded-lg shadow">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-xl font-semibold text-gray-900">{selectedMeeting.title}</h2>
                <p className="text-gray-600 mt-1">
                  {format(new Date(selectedMeeting.meeting_date), 'MMMM d, yyyy \'at\' h:mm a')}
                </p>
              </div>

              {/* Agenda Items */}
              {selectedMeeting.agenda_items && selectedMeeting.agenda_items.length > 0 && (
                <div className="p-6 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Agenda Items</h3>
                  <div className="space-y-3">
                    {selectedMeeting.agenda_items.map((item) => (
                      <div key={item.id} className="border-l-4 border-primary-200 pl-4">
                        <div className="flex justify-between items-start">
                          <h4 className="font-medium text-gray-900">
                            {item.item_number}. {item.title}
                          </h4>
                          {item.vote_result && (
                            <span className={`px-2 py-1 text-xs rounded-full ${
                              item.vote_result === 'passed' ? 'bg-green-100 text-green-800' :
                              item.vote_result === 'failed' ? 'bg-red-100 text-red-800' :
                              'bg-yellow-100 text-yellow-800'
                            }`}>
                              {item.vote_result}
                            </span>
                          )}
                        </div>
                        {item.description && (
                          <p className="text-sm text-gray-600 mt-1">{item.description}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Meeting Minutes */}
              {selectedMeeting.summary && (
                <div className="p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Meeting Minutes</h3>
                  <div className="prose prose-sm max-w-none">
                    <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans leading-relaxed">
                      {selectedMeeting.summary}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-gray-50 rounded-lg p-8 text-center">
              <p className="text-gray-500">Select a meeting to view details and minutes</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
