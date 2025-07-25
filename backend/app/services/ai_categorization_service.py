import io
import json
import logging
from typing import Dict, List, Tuple

import fitz  # PyMuPDF for better PDF text extraction

# AI/ML imports
import openai

# PDF processing
import PyPDF2
from app.core.config import settings
from app.models.meeting import MeetingCategory
from pydantic import BaseModel

# Database imports
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class CategoryDefinition(BaseModel):
    name: str
    description: str
    keywords: List[str]
    color: str
    icon: str


class ProcessedMeetingContent(BaseModel):
    summary: str
    categories: List[str]
    keywords: List[str]
    agenda_items: List[Dict]
    impact_assessment: str
    key_decisions: List[str]
    public_comments: List[str]


class AICategorization:
    """AI-powered categorization service for meeting minutes and civic content"""

    # Comprehensive social issue categories for civic engagement
    SOCIAL_ISSUE_CATEGORIES = {
        # Core Municipal Services
        "municipal_services": CategoryDefinition(
            name="Municipal Services",
            description=(
                "City services, utilities, waste management, "
                "and basic infrastructure"
            ),
            keywords=[
                "utilities",
                "water",
                "sewer",
                "waste",
                "garbage",
                "recycling",
                "city services",
            ],
            color="#4A90E2",
            icon="🏛️",
        ),
        "public_safety": CategoryDefinition(
            name="Public Safety",
            description=(
                "Police, fire, emergency services, " "and community safety initiatives"
            ),
            keywords=[
                "police",
                "fire",
                "emergency",
                "911",
                "safety",
                "crime",
                "security",
                "law enforcement",
            ],
            color="#E74C3C",
            icon="🚔",
        ),
        "transportation": CategoryDefinition(
            name="Transportation",
            description=(
                "Roads, public transit, traffic, parking, "
                "and transportation infrastructure"
            ),
            keywords=[
                "roads",
                "transit",
                "bus",
                "traffic",
                "parking",
                "highways",
                "streets",
                "transportation",
            ],
            color="#9B59B6",
            icon="🚌",
        ),
        # Social Justice & Equity
        "social_justice": CategoryDefinition(
            name="Social Justice",
            description=(
                "Civil rights, discrimination, equality, "
                "and social justice initiatives"
            ),
            keywords=[
                "civil rights",
                "discrimination",
                "equality",
                "justice",
                "bias",
                "diversity",
                "inclusion",
            ],
            color="#E67E22",
            icon="⚖️",
        ),
        "immigration": CategoryDefinition(
            name="Immigration",
            description=(
                "Immigration policy, refugee services, "
                "and immigrant community support"
            ),
            keywords=[
                "immigration",
                "refugee",
                "asylum",
                "deportation",
                "sanctuary",
                "immigrant",
                "citizenship",
            ],
            color="#1ABC9C",
            icon="🌍",
        ),
        "racial_equity": CategoryDefinition(
            name="Racial Equity",
            description=(
                "Racial justice, equity initiatives, " "and addressing systemic racism"
            ),
            keywords=[
                "racial",
                "racism",
                "equity",
                "bias",
                "minority",
                "african american",
                "hispanic",
                "native american",
            ],
            color="#F39C12",
            icon="✊",
        ),
        # Healthcare & Social Services
        "healthcare": CategoryDefinition(
            name="Healthcare",
            description=(
                "Public health, medical services, mental health, "
                "and healthcare access"
            ),
            keywords=[
                "health",
                "medical",
                "hospital",
                "mental health",
                "healthcare",
                "clinic",
                "public health",
            ],
            color="#27AE60",
            icon="🏥",
        ),
        "social_services": CategoryDefinition(
            name="Social Services",
            description=(
                "Human services, welfare, homelessness, " "and social support programs"
            ),
            keywords=[
                "welfare",
                "homeless",
                "social services",
                "food assistance",
                "housing assistance",
                "poverty",
            ],
            color="#8E44AD",
            icon="🤝",
        ),
        "senior_services": CategoryDefinition(
            name="Senior Services",
            description=("Elder care, senior programs, and age-related services"),
            keywords=[
                "senior",
                "elder",
                "aging",
                "retirement",
                "medicare",
                "social security",
            ],
            color="#34495E",
            icon="👴",
        ),
        # Housing & Development
        "housing": CategoryDefinition(
            name="Housing",
            description=(
                "Housing policy, affordable housing, " "and residential development"
            ),
            keywords=[
                "housing",
                "affordable housing",
                "rent",
                "mortgage",
                "development",
                "residential",
                "apartments",
            ],
            color="#D35400",
            icon="🏠",
        ),
        "land_use": CategoryDefinition(
            name="Land Use & Zoning",
            description=("Zoning laws, land development, and urban planning"),
            keywords=[
                "zoning",
                "land use",
                "development",
                "planning",
                "rezoning",
                "permits",
                "subdivision",
            ],
            color="#7F8C8D",
            icon="🗺️",
        ),
        "historic_preservation": CategoryDefinition(
            name="Historic Preservation",
            description=(
                "Historic districts, landmark preservation, " "and cultural heritage"
            ),
            keywords=[
                "historic",
                "preservation",
                "landmark",
                "heritage",
                "cultural",
                "architecture",
            ],
            color="#A0522D",
            icon="🏛️",
        ),
        # Environment & Sustainability
        "environment": CategoryDefinition(
            name="Environment",
            description=(
                "Environmental protection, sustainability, " "and climate action"
            ),
            keywords=[
                "environment",
                "climate",
                "sustainability",
                "pollution",
                "green",
                "renewable",
                "carbon",
            ],
            color="#2ECC71",
            icon="🌱",
        ),
        "parks_recreation": CategoryDefinition(
            name="Parks & Recreation",
            description=(
                "Public parks, recreational facilities, " "and outdoor spaces"
            ),
            keywords=[
                "parks",
                "recreation",
                "trails",
                "playground",
                "sports",
                "outdoor",
                "green space",
            ],
            color="#16A085",
            icon="🌳",
        ),
        "water_quality": CategoryDefinition(
            name="Water Quality",
            description=("Water safety, quality, and environmental water issues"),
            keywords=[
                "water quality",
                "drinking water",
                "pollution",
                "river",
                "lake",
                "watershed",
            ],
            color="#3498DB",
            icon="💧",
        ),
        # Economic Development
        "economic_development": CategoryDefinition(
            name="Economic Development",
            description=("Business development, job creation, and economic policy"),
            keywords=[
                "economic",
                "business",
                "jobs",
                "development",
                "commerce",
                "industry",
                "workforce",
            ],
            color="#E74C3C",
            icon="📈",
        ),
        "small_business": CategoryDefinition(
            name="Small Business",
            description=(
                "Small business support, entrepreneurship, " "and local commerce"
            ),
            keywords=[
                "small business",
                "entrepreneur",
                "local business",
                "startup",
                "commerce",
            ],
            color="#F39C12",
            icon="🏪",
        ),
        "taxation": CategoryDefinition(
            name="Taxation & Budget",
            description=("Tax policy, municipal budget, and fiscal matters"),
            keywords=[
                "tax",
                "budget",
                "fiscal",
                "revenue",
                "spending",
                "bonds",
                "debt",
            ],
            color="#95A5A6",
            icon="💰",
        ),
        # Education & Youth
        "education": CategoryDefinition(
            name="Education",
            description=("Schools, education policy, and student services"),
            keywords=[
                "education",
                "school",
                "student",
                "teacher",
                "learning",
                "curriculum",
            ],
            color="#3498DB",
            icon="🎓",
        ),
        "youth_services": CategoryDefinition(
            name="Youth Services",
            description=("Youth programs, child care, and services for young people"),
            keywords=[
                "youth",
                "children",
                "childcare",
                "programs",
                "kids",
                "teenagers",
            ],
            color="#9B59B6",
            icon="👶",
        ),
        # Technology & Innovation
        "technology": CategoryDefinition(
            name="Technology",
            description=("Smart city initiatives, broadband, and digital services"),
            keywords=[
                "technology",
                "digital",
                "broadband",
                "internet",
                "smart city",
                "innovation",
            ],
            color="#2C3E50",
            icon="💻",
        ),
        "transparency": CategoryDefinition(
            name="Government Transparency",
            description=("Open government, public records, and civic engagement"),
            keywords=[
                "transparency",
                "open government",
                "records",
                "accountability",
                "civic engagement",
            ],
            color="#E67E22",
            icon="👁️",
        ),
        # Arts & Culture
        "arts_culture": CategoryDefinition(
            name="Arts & Culture",
            description=("Cultural programs, arts funding, and community events"),
            keywords=[
                "arts",
                "culture",
                "museum",
                "library",
                "events",
                "festivals",
                "cultural",
            ],
            color="#8E44AD",
            icon="🎨",
        ),
        # Veterans & Military
        "veterans": CategoryDefinition(
            name="Veterans Affairs",
            description=("Veteran services, military support, and veteran benefits"),
            keywords=[
                "veterans",
                "military",
                "veteran benefits",
                "armed forces",
                "service members",
            ],
            color="#27AE60",
            icon="🎖️",
        ),
        # Infrastructure
        "infrastructure": CategoryDefinition(
            name="Infrastructure",
            description=(
                "Public infrastructure, maintenance, " "and capital improvements"
            ),
            keywords=[
                "infrastructure",
                "roads",
                "bridges",
                "maintenance",
                "capital",
                "construction",
            ],
            color="#34495E",
            icon="🏗️",
        ),
        # Public Health & Safety
        "animal_control": CategoryDefinition(
            name="Animal Control",
            description=("Animal services, pet regulations, and animal welfare"),
            keywords=["animal", "pet", "dog", "cat", "animal control", "shelter"],
            color="#F39C12",
            icon="🐕",
        ),
        "food_safety": CategoryDefinition(
            name="Food Safety",
            description=("Restaurant inspections, food safety, and public health"),
            keywords=["food safety", "restaurant", "inspection", "health department"],
            color="#E74C3C",
            icon="🍽️",
        ),
        # Emergency Management
        "emergency_management": CategoryDefinition(
            name="Emergency Management",
            description=(
                "Disaster preparedness, emergency response, " "and crisis management"
            ),
            keywords=[
                "emergency",
                "disaster",
                "preparedness",
                "response",
                "crisis",
                "evacuation",
            ],
            color="#C0392B",
            icon="🚨",
        ),
        # General Government
        "elections": CategoryDefinition(
            name="Elections",
            description=("Election administration, voting, and electoral processes"),
            keywords=["election", "voting", "ballot", "campaign", "electoral"],
            color="#2980B9",
            icon="🗳️",
        ),
        "legal_proceedings": CategoryDefinition(
            name="Legal Proceedings",
            description=("Legal matters, lawsuits, and legal compliance"),
            keywords=[
                "legal",
                "lawsuit",
                "court",
                "litigation",
                "compliance",
                "attorney",
            ],
            color="#7F8C8D",
            icon="⚖️",
        ),
    }

    def __init__(self):
        """Initialize the AI categorization service"""
        openai.api_key = settings.openai_api_key
        if not openai.api_key:
            logger.warning(
                "OpenAI API key not configured. AI features will be limited."
            )

    @classmethod
    def get_category_definitions(cls) -> Dict[str, CategoryDefinition]:
        """Get all category definitions"""
        return cls.SOCIAL_ISSUE_CATEGORIES

    @classmethod
    def initialize_categories_in_db(cls, db: Session) -> None:
        """Initialize category definitions in the database"""
        try:
            for category_id, category_def in cls.SOCIAL_ISSUE_CATEGORIES.items():
                # Check if category already exists
                existing_category = (
                    db.query(MeetingCategory)
                    .filter(MeetingCategory.name == category_def.name)
                    .first()
                )

                if not existing_category:
                    db_category = MeetingCategory(
                        name=category_def.name,
                        description=category_def.description,
                        keywords=category_def.keywords,
                        color=category_def.color,
                        icon=category_def.icon,
                    )
                    db.add(db_category)
                else:
                    # Update existing category
                    existing_category.description = category_def.description
                    existing_category.keywords = category_def.keywords
                    existing_category.color = category_def.color
                    existing_category.icon = category_def.icon

            db.commit()
            logger.info(
                f"Initialized {len(cls.SOCIAL_ISSUE_CATEGORIES)} categories in database"
            )
        except Exception as e:
            logger.error(f"Error initializing categories: {str(e)}")
            db.rollback()

    def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extract text from PDF content using PyMuPDF for better accuracy"""
        try:
            # Try PyMuPDF first (better text extraction)
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            text = ""
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                text += page.get_text() + "\n"
            pdf_document.close()
            return text
        except Exception as e:
            logger.warning(f"PyMuPDF failed, falling back to PyPDF2: {str(e)}")
            # Fallback to PyPDF2
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
            except Exception as e2:
                logger.error(f"PDF text extraction failed: {str(e2)}")
                return ""

    def categorize_content_with_ai(
        self, content: str
    ) -> Tuple[List[str], List[str], str]:
        """Use OpenAI to categorize content and extract keywords"""
        if not openai.api_key:
            logger.warning(
                "OpenAI API key not configured. Using fallback categorization."
            )
            return self._fallback_categorization(content)

        try:
            categories_list = "\n".join(
                [
                    f"- {cat.name}: {cat.description}"
                    for cat in self.SOCIAL_ISSUE_CATEGORIES.values()
                ]
            )

            prompt = f"""
            Analyze the following meeting minutes/agenda content and:
            1. Identify which categories apply (return category names exactly as listed)
            2. Extract 5-10 relevant keywords
            3. Provide a 2-3 sentence summary

            Available categories:
            {categories_list}

            Content to analyze:
            {content[:4000]}  # Limit content to avoid token limits

            Please respond in JSON format:
            {{
                "categories": ["category1", "category2"],
                "keywords": ["keyword1", "keyword2", "keyword3"],
                "summary": "Brief summary of the content"
            }}
            """

            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert at analyzing civic meeting "
                            "content and categorizing it for public engagement."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=800,
                temperature=0.1,
            )

            result = json.loads(response.choices[0].message.content)
            return (
                result.get("categories", []),
                result.get("keywords", []),
                result.get("summary", ""),
            )

        except Exception as e:
            logger.error(f"OpenAI categorization failed: {str(e)}")
            return self._fallback_categorization(content)

    def _fallback_categorization(
        self, content: str
    ) -> Tuple[List[str], List[str], str]:
        """Fallback categorization using keyword matching"""
        content_lower = content.lower()
        matched_categories = []
        all_keywords = []

        for category_id, category_def in self.SOCIAL_ISSUE_CATEGORIES.items():
            category_matches = 0
            for keyword in category_def.keywords:
                if keyword.lower() in content_lower:
                    category_matches += 1
                    all_keywords.append(keyword)

            if category_matches >= 2:  # Require at least 2 keyword matches
                matched_categories.append(category_def.name)

        # Generate simple summary (first 200 characters)
        summary = content[:200].strip()
        if len(content) > 200:
            summary += "..."

        return matched_categories, list(set(all_keywords)), summary

    def process_meeting_minutes(
        self, pdf_content: bytes, meeting_id: int, db: Session
    ) -> ProcessedMeetingContent:
        """Process meeting minutes PDF and extract categorized information"""
        try:
            # Extract text from PDF
            text_content = self.extract_text_from_pdf(pdf_content)

            if not text_content.strip():
                logger.warning(f"No text extracted from PDF for meeting {meeting_id}")
                return ProcessedMeetingContent(
                    summary="No content could be extracted from the PDF",
                    categories=[],
                    keywords=[],
                    agenda_items=[],
                    impact_assessment="Unable to assess impact - no content extracted",
                    key_decisions=[],
                    public_comments=[],
                )

            # Categorize content
            categories, keywords, summary = self.categorize_content_with_ai(
                text_content
            )

            # Extract agenda items (this could be enhanced
            # with more sophisticated parsing)
            agenda_items = self._extract_agenda_items(text_content)

            # Generate impact assessment
            impact_assessment = self._generate_impact_assessment(
                text_content, categories
            )

            # Extract key decisions
            key_decisions = self._extract_key_decisions(text_content)

            # Extract public comments
            public_comments = self._extract_public_comments(text_content)

            return ProcessedMeetingContent(
                summary=summary,
                categories=categories,
                keywords=keywords,
                agenda_items=agenda_items,
                impact_assessment=impact_assessment,
                key_decisions=key_decisions,
                public_comments=public_comments,
            )

        except Exception as e:
            logger.error(f"Error processing meeting minutes: {str(e)}")
            raise

    def _extract_agenda_items(self, content: str) -> List[Dict]:
        """Extract agenda items from meeting content"""
        # This is a simplified implementation
        # In production, you might want more sophisticated parsing
        agenda_items = []
        lines = content.split("\n")

        for i, line in enumerate(lines):
            line = line.strip()
            # Look for patterns like "1.", "A.", "Item 1", etc.
            if any(
                pattern in line.lower()
                for pattern in ["item", "agenda", "motion", "resolution"]
            ):
                if len(line) > 10:  # Avoid very short lines
                    agenda_items.append(
                        {
                            "title": line[:100],  # Limit title length
                            "description": line,
                            "line_number": i,
                        }
                    )

        return agenda_items[:20]  # Limit to 20 items

    def _generate_impact_assessment(self, content: str, categories: List[str]) -> str:
        """Generate impact assessment based on content and categories"""
        if not categories:
            return "No specific community impact identified."

        impact_areas = {
            "Public Safety": "community safety and security",
            "Transportation": "mobility and accessibility",
            "Housing": "housing affordability and availability",
            "Healthcare": "public health and medical services",
            "Environment": "environmental quality and sustainability",
            "Economic Development": "local economy and job creation",
        }

        impacts = []
        for category in categories:
            if category in impact_areas:
                impacts.append(f"This decision may impact {impact_areas[category]}.")

        return (
            " ".join(impacts)
            if impacts
            else "Community impact assessment pending further analysis."
        )

    def _extract_key_decisions(self, content: str) -> List[str]:
        """Extract key decisions from meeting content"""
        decisions = []

        # Look for decision keywords
        decision_keywords = [
            "approved",
            "denied",
            "passed",
            "failed",
            "motion",
            "voted",
            "resolution",
        ]

        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in decision_keywords):
                if len(line) > 15:  # Avoid very short lines
                    decisions.append(line[:200])  # Limit length

        return decisions[:10]  # Limit to 10 decisions

    def _extract_public_comments(self, content: str) -> List[str]:
        """Extract public comments from meeting content"""
        comments = []

        # Look for public comment sections
        comment_keywords = [
            "public comment",
            "citizen comment",
            "public input",
            "comments from",
        ]

        lines = content.split("\n")
        in_comment_section = False

        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in comment_keywords):
                in_comment_section = True
                continue

            if in_comment_section:
                if line and len(line) > 10:
                    comments.append(line[:300])  # Limit length
                    if len(comments) >= 10:  # Limit to 10 comments
                        break

        return comments
