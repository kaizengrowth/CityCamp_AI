import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from app.core.config import Settings
from app.models.campaign import Campaign
from app.models.meeting import Meeting
from app.services.research_service import ResearchService
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

    def get_system_prompt(self) -> str:
        """Get the enhanced system prompt for the chatbot"""
        return """You are CityCamp AI, a specialized assistant for Tulsa, Oklahoma civic engagement and local government.

IMPORTANT GUARDRAILS:
- You ONLY answer questions related to Tulsa, Oklahoma local government, civic engagement, and municipal services
- If asked about other cities, states, or non-Tulsa topics, politely redirect to Tulsa-specific matters
- Always emphasize "Tulsa" in your responses to maintain local focus
- Do not provide information about other municipalities unless directly comparing to Tulsa

You can help with:
- Information about Tulsa City Council meetings, agendas, and minutes
- Details about local Tulsa campaigns and civic initiatives
- Guidance on civic participation and engagement in Tulsa
- General information about Tulsa city government
- How to use the CityCamp AI platform
- Current events and news related to Tulsa government

ENHANCED CAPABILITIES:
- You can search the web for current information about Tulsa government
- You can retrieve and analyze official documents, PDFs, and meeting minutes
- You can provide links to relevant resources and documents
- Use **bold** text for emphasis and proper markdown formatting
- Always provide clickable links in markdown format: [text](url)

Key guidelines:
- Be helpful, friendly, and encouraging about civic engagement in Tulsa
- Provide accurate, up-to-date information about local government processes
- Encourage users to participate in democracy and civic activities
- When you find relevant documents or web pages, always provide the links
- Use markdown formatting for better readability
- Break up long responses into clear paragraphs with proper spacing

If asked about non-Tulsa topics, respond with: "I'm specifically designed to help with **Tulsa, Oklahoma** civic engagement and local government matters. Please ask me about Tulsa-specific topics!\""""

    def get_function_definitions(self) -> List[Dict[str, Any]]:
        """Define available functions for OpenAI function calling"""
        return [
            {
                "name": "search_web",
                "description": "Search the web for current information about Tulsa government, meetings, ordinances, or civic matters",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query related to Tulsa government or civic matters",
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Number of search results to return (default: 5)",
                            "default": 5,
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
            {
                "name": "search_tulsa_documents",
                "description": "Search specifically for Tulsa government documents, PDFs, meeting minutes, and official records",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for Tulsa government documents",
                        }
                    },
                    "required": ["query"],
                },
            },
        ]

    async def process_function_call(
        self, function_name: str, arguments: Dict[str, Any]
    ) -> str:
        """Process function calls from OpenAI"""
        try:
            if function_name == "search_web":
                query = arguments.get("query", "")
                num_results = arguments.get("num_results", 5)

                results = await self.research_service.search_web(query, num_results)
                return self.research_service.format_search_results(results)

            elif function_name == "retrieve_document":
                url = arguments.get("url", "")

                document = await self.research_service.retrieve_document(url)
                return self.research_service.format_document_content(document)

            elif function_name == "search_tulsa_documents":
                query = arguments.get("query", "")

                documents = await self.research_service.search_tulsa_documents(query)
                return self.research_service.format_search_results(documents)

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
                max_tokens=1000,
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
                    max_tokens=1000,
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
            return """I'm specifically designed to help with **Tulsa, Oklahoma** civic engagement and local government matters.

I can assist you with:
• **Tulsa City Council** meetings and agendas
• Local **Tulsa** campaigns and initiatives
• **Tulsa** civic participation opportunities
• **Tulsa** government services and information

Please ask me about **Tulsa-specific** topics! For general information, visit the [City of Tulsa website](https://www.cityoftulsa.org/)."""

        # Meeting-related queries
        if any(
            word in message_lower
            for word in ["meeting", "council", "agenda", "minutes"]
        ):
            return """I can help you find information about **Tulsa City Council meetings**!

You can:
• View upcoming meetings and agendas on the Meetings page
• Read past meeting minutes and summaries
• Get notifications about meetings that interest you

For official information, visit:
• [Tulsa City Council](https://www.cityoftulsa.org/government/city-council/)
• [City Clerk's Office](https://www.cityoftulsa.org/government/city-clerk/)

What specific **Tulsa** meeting information are you looking for?"""

        # Campaign-related queries
        if any(
            word in message_lower
            for word in ["campaign", "petition", "initiative", "vote"]
        ):
            return """**CityCamp AI** helps you stay informed about local **Tulsa** campaigns and civic initiatives!

Check out the Campaigns page to:
• See active petitions and initiatives in **Tulsa**
• Learn about local ballot measures
• Find ways to get involved in your **Tulsa** community

For election information, visit:
• [Tulsa Elections](https://www.cityoftulsa.org/government/city-clerk/elections/)
• [Tulsa County Election Board](https://www.tulsacounty.org/election-board/)

Is there a specific **Tulsa** campaign or issue you're interested in?"""

        # Notification queries
        if any(word in message_lower for word in ["notification", "alert", "remind"]):
            return """You can set up **personalized notifications** to stay engaged with **Tulsa** local government!

Go to your Profile settings to:
• Get alerts about upcoming **Tulsa** meetings
• Receive updates on **Tulsa** campaigns you care about
• Set preferences for topics that matter to you

For city services, you can also use:
• [Tulsa 311 Services](https://www.cityoftulsa.org/services/311/)

Would you like help setting up notifications for **Tulsa** civic activities?"""

        # General greeting
        if any(word in message_lower for word in ["hello", "hi", "help", "start"]):
            return """Hello! I'm your **CityCamp AI assistant**, here to help you stay engaged with **Tulsa local government**.

I can help you with:
🏛️ **Tulsa City Council** meetings and agendas
📋 Local **Tulsa** campaigns and initiatives
🔔 Setting up notifications for **Tulsa** civic activities
🗳️ **Tulsa** civic participation opportunities

For official information, visit the [City of Tulsa website](https://www.cityoftulsa.org/)

What would you like to know about **Tulsa** local government?"""

        # Default response
        return """I'm here to help you stay informed about **Tulsa local government** and civic engagement.

You can ask me about:
• Upcoming **Tulsa City Council** meetings
• Local **Tulsa** campaigns and initiatives
• How to get more involved in your **Tulsa** community
• Using the CityCamp AI platform

Helpful resources:
• [City of Tulsa](https://www.cityoftulsa.org/)
• [Tulsa City Council](https://www.cityoftulsa.org/government/city-council/)
• [Tulsa 311 Services](https://www.cityoftulsa.org/services/311/)

You can also explore the Meetings and Campaigns pages for the latest information. What would you like to know about **Tulsa**?"""
