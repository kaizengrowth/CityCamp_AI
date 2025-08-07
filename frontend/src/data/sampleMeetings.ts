export interface AgendaItem {
  id: number;
  item_number: string;
  title: string;
  description?: string;
  item_type?: string;
  vote_required: boolean;
  vote_result?: string;
}

export interface Meeting {
  id: number;
  title: string;
  description?: string;
  meeting_date: string;
  location: string;
  meeting_type: string;
  status: string;
  meeting_url?: string;
  agenda_url?: string;
  minutes_url?: string;
  external_id?: string;
  source: string;
  topics: string[];
  keywords: string[];
  summary?: string;
  created_at: string;
  updated_at?: string;
  agenda_items?: AgendaItem[];
  image_paths?: string[];
}

// Sample data for demo purposes
export const SAMPLE_MEETINGS: Meeting[] = [
  {
    id: 1,
    title: "Regular City Council Meeting",
    description: "Monthly regular meeting of the Tulsa City Council",
    meeting_date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    location: "One Technology Center, Tulsa, OK",
    meeting_type: "regular_council",
    status: "completed",
    agenda_url: "https://example.com/agenda",
    source: "tulsa_gov",
    topics: ["budget", "zoning", "public_safety"],
    keywords: ["ordinance", "budget", "council"],
    created_at: new Date().toISOString(),
    image_paths: [
      "https://raw.githubusercontent.com/kaizengrowth/CityCamp_AI/main/backend/storage/meeting-images/2025/01/15/25_74_1_25_74_1_2025_01_15_4PM_Minutes_4PM/25_74_1_25_74_1_2025_01_15_4PM_2025-01-15_page01.png",
      "https://raw.githubusercontent.com/kaizengrowth/CityCamp_AI/main/backend/storage/meeting-images/2025/01/15/25_74_1_25_74_1_2025_01_15_4PM_Minutes_4PM/25_74_1_25_74_1_2025_01_15_4PM_2025-01-15_page02.png"
    ],
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
    description: "Committee meeting on public works initiatives",
    meeting_date: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    location: "City Hall Committee Room",
    meeting_type: "public_works_committee",
    status: "completed",
    source: "tulsa_gov",
    topics: ["infrastructure", "transportation"],
    keywords: ["roads", "maintenance", "projects"],
    created_at: new Date().toISOString(),
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
    description: "Committee meeting on economic development initiatives",
    meeting_date: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString(),
    location: "One Technology Center",
    meeting_type: "urban_economic_committee",
    status: "scheduled",
    source: "tulsa_gov",
    topics: ["economic_development", "urban_planning"],
    keywords: ["development", "business", "planning"],
    created_at: new Date().toISOString(),
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
