import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from app.core.config import Settings
from app.models.campaign import Campaign
from app.models.meeting import Meeting
from app.services.research_service import ResearchService
from app.services.vector_service import VectorService
from openai import OpenAI
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ChatbotService:
    """Enhanced chatbot service with GPT-4 and research capabilities"""

    def __init__(self, db: Session, settings: Settings):
        self.db = db
        self.settings = settings

        # Validate OpenAI API key
        if not settings.is_openai_configured:
            logger.warning(
                "OpenAI API key is missing or using placeholder value. Chatbot will use fallback responses only."
            )
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.openai_api_key)

        self.research_service = ResearchService(settings)
        self.vector_service = VectorService(settings)

    def get_system_prompt(self) -> str:
        """Get the enhanced system prompt for the chatbot"""
        return """You are CityCamp AI for Tulsa, Oklahoma civic engagement.

FOCUS: Only answer Tulsa government, civic engagement, and municipal service questions.

RESPONSE STYLE:
- Keep responses short and conversational (2-3 sentences max)
- Use simple language, avoid jargon
- Be helpful but concise
- Use **bold** for key terms
- Provide links when relevant: [text](url)

CAPABILITIES:
- Search web for current Tulsa government info
- Retrieve official documents and meeting minutes
- Help with civic participation

If asked about non-Tulsa topics: "I focus on **Tulsa, Oklahoma** civic matters. What can I help you with regarding Tulsa government?"

Be friendly, encouraging, and brief."""

    def get_function_definitions(self) -> List[Dict[str, Any]]:
        """Define available functions for OpenAI function calling"""
        return [
            {
                "name": "search_documents",
                "description": "Search Tulsa city documents, budgets, legislation, policies, and meeting minutes using semantic search",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for Tulsa government documents",
                        },
                        "document_type": {
                            "type": "string",
                            "description": "Filter by document type: budget, legislation, policy, meeting_minutes, ordinance",
                        },
                        "category": {
                            "type": "string",
                            "description": "Filter by category: transportation, housing, finance, public_safety, utilities",
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 3)",
                            "default": 3,
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "search_web",
                "description": "Search the web for current information about Tulsa government when documents don't have the answer",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query related to Tulsa government or civic matters",
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Number of search results to return (default: 3)",
                            "default": 3,
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "retrieve_document",
                "description": "Retrieve and analyze a specific document (PDF, webpage) from a URL",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL of the document to retrieve and analyze",
                        }
                    },
                    "required": ["url"],
                },
            },
        ]

    async def process_function_call(
        self, function_name: str, arguments: Dict[str, Any]
    ) -> str:
        """Process function calls from OpenAI"""
        try:
            if function_name == "search_documents":
                query = arguments.get("query", "")
                document_type = arguments.get("document_type")
                category = arguments.get("category")
                max_results = arguments.get("max_results", 3)

                # Build filters
                filters = {}
                if document_type:
                    filters["document_type"] = document_type
                if category:
                    filters["category"] = category

                # Search documents using RAG
                results = await self.vector_service.search_documents(
                    query, max_results, filters
                )

                if results:
                    formatted_results = "**Relevant Tulsa Documents:**\n\n"
                    for i, result in enumerate(results, 1):
                        metadata = result.get("metadata", {})
                        content = result.get("content", "")
                        similarity = result.get("similarity", 0)

                        formatted_results += (
                            f"**{i}. Document Excerpt** (relevance: {similarity:.2f})\n"
                        )
                        if metadata.get("document_type"):
                            formatted_results += f"Type: {metadata['document_type']}\n"
                        if metadata.get("category"):
                            formatted_results += f"Category: {metadata['category']}\n"
                        formatted_results += f"Content: {content[:300]}...\n\n"

                    return formatted_results
                else:
                    return "No relevant documents found in the database."

            elif function_name == "search_web":
                query = arguments.get("query", "")
                num_results = arguments.get("num_results", 3)

                results = await self.research_service.search_web(query, num_results)
                return self.research_service.format_search_results(results)

            elif function_name == "retrieve_document":
                url = arguments.get("url", "")

                document = await self.research_service.retrieve_document(url)
                return self.research_service.format_document_content(document)

            else:
                return f"Unknown function: {function_name}"

        except Exception as e:
            logger.error(f"Error processing function call {function_name}: {e}")
            return f"Error executing {function_name}: {str(e)}"

    def _get_context_from_recent_meetings(self) -> str:
        """Get context from recent meetings to help answer questions"""
        try:
            recent_meetings = (
                self.db.query(Meeting)
                .order_by(Meeting.meeting_date.desc())
                .limit(5)
                .all()
            )

            if not recent_meetings:
                return "No recent meeting data available."

            context = "Recent Tulsa City Council meetings:\n"
            for meeting in recent_meetings:
                context += (
                    f"- {meeting.title} on "
                    f"{meeting.meeting_date.strftime('%B %d, %Y')}"
                )
                if meeting.summary:
                    context += f": {meeting.summary[:100]}..."
                context += "\n"

            return context
        except Exception as e:
            logger.error(f"Error fetching meeting context: {e}")
            return "Unable to fetch recent meeting information."

    def _get_context_from_campaigns(self) -> str:
        """Get context from active campaigns"""
        try:
            # Note: This assumes Campaign model exists - adjust based on actual model
            active_campaigns = (
                self.db.query(Campaign)
                .filter(Campaign.status == "active")
                .limit(3)
                .all()
            )

            if not active_campaigns:
                return "No active campaigns available."

            context = "Active civic campaigns:\n"
            for campaign in active_campaigns:
                context += f"- {campaign.title}: {campaign.description[:100]}...\n"

            return context
        except Exception as e:
            logger.error(f"Error fetching campaign context: {e}")
            return "Unable to fetch campaign information."

    async def get_ai_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """Get AI response with enhanced research capabilities"""
        try:
            # Check if OpenAI client is available
            if self.client is None:
                logger.warning("OpenAI client not available. Using fallback response.")
                return self._get_fallback_response(user_message)

            system_prompt = self.get_system_prompt()

            # Get context from local database
            meeting_context = self._get_context_from_recent_meetings()
            campaign_context = self._get_context_from_campaigns()

            # Build messages for OpenAI
            messages = [
                {
                    "role": "system",
                    "content": (
                        f"{system_prompt}\n\nCurrent local context:\n"
                        f"{meeting_context}\n{campaign_context}"
                    ),
                }
            ]

            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history[-10:]:  # Keep last 10 messages
                    messages.append(
                        {
                            "role": (
                                "user" if msg["sender"] == "user" else "assistant"
                            ),
                            "content": msg["text"],
                        }
                    )

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            logger.info(f"Calling OpenAI GPT-4 API with {len(messages)} messages...")

            # Get response from OpenAI with function calling
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                max_tokens=300,  # Reduced from 1000 to encourage shorter responses
                temperature=0.7,
                functions=self.get_function_definitions(),
                function_call="auto",
            )

            message = response.choices[0].message

            # Check if the model wants to call a function
            if message.function_call:
                function_name = message.function_call.name
                function_args = json.loads(message.function_call.arguments)

                logger.info(f"AI requested function call: {function_name}")

                # Execute the function
                function_result = await self.process_function_call(
                    function_name, function_args
                )

                # Add function result to conversation and get final response
                # Add function call message
                function_call_message: Dict[str, Any] = {
                    "role": "assistant",
                    "content": None,
                    "function_call": {
                        "name": function_name,
                        "arguments": message.function_call.arguments,
                    },
                }
                messages.append(function_call_message)  # type: ignore

                messages.append(
                    {
                        "role": "function",
                        "name": function_name,
                        "content": function_result,
                    }
                )

                # Get final response with function result
                final_response = self.client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=messages,
                    max_tokens=300,  # Reduced from 1000 to encourage shorter responses
                    temperature=0.7,
                )

                ai_response = final_response.choices[0].message.content.strip()
            else:
                ai_response = message.content.strip()

            logger.info(f"Generated AI response: {ai_response[:100]}...")
            return ai_response

        except Exception as e:
            error_message = str(e)

            # Log specific OpenAI API errors for better debugging
            if (
                "Incorrect API key" in error_message
                or "Invalid API key" in error_message
            ):
                logger.error(f"OpenAI API key is invalid: {error_message}")
            elif "Rate limit" in error_message:
                logger.error(f"OpenAI API rate limit exceeded: {error_message}")
            elif "quota" in error_message.lower():
                logger.error(f"OpenAI API quota exceeded: {error_message}")
            else:
                logger.error(f"Error getting AI response: {error_message}")

            return self._get_fallback_response(user_message)

    def _get_fallback_response(self, user_message: str) -> str:
        """Provide fallback responses when OpenAI is not available"""
        message_lower = user_message.lower()

        # Check for Tulsa-specific keywords - if none found, provide guardrail response
        tulsa_keywords = [
            "tulsa",
            "city",
            "council",
            "meeting",
            "agenda",
            "minutes",
            "campaign",
            "petition",
            "initiative",
            "vote",
            "civic",
            "government",
            "local",
            "mayor",
            "election",
            "notification",
            "alert",
            "remind",
        ]

        if not any(keyword in message_lower for keyword in tulsa_keywords):
            return "I focus on **Tulsa, Oklahoma** civic matters. What can I help you with regarding Tulsa government?"

        # Meeting-related queries
        if any(
            word in message_lower
            for word in ["meeting", "council", "agenda", "minutes"]
        ):
            return "Check the Meetings page for **Tulsa City Council** agendas and minutes. What specific meeting info do you need?"

        # Campaign-related queries
        if any(
            word in message_lower
            for word in ["campaign", "petition", "initiative", "vote"]
        ):
            return "Visit the Campaigns page to see active **Tulsa** initiatives and petitions. Which campaign interests you?"

        # Notification queries
        if any(word in message_lower for word in ["notification", "alert", "remind"]):
            return "Set up **notifications** in your Profile settings for **Tulsa** meetings and campaigns. Need help with that?"

        # General greeting
        if any(word in message_lower for word in ["hello", "hi", "help", "start"]):
            return "Hi! I'm your **CityCamp AI** assistant for **Tulsa** civic engagement. I can help with meetings, campaigns, and notifications. What do you need?"

        # Default response
        return "I help with **Tulsa** civic engagement - meetings, campaigns, and community involvement. What can I assist you with?"
