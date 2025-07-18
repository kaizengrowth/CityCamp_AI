import openai
import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.meeting import Meeting, AgendaItem
from app.models.campaign import Campaign

logger = logging.getLogger(__name__)

class ChatbotService:
    """Service to handle AI-powered chatbot conversations about civic engagement"""
    
    def __init__(self, db: Session):
        self.db = db
        self.client = openai.OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the chatbot"""
        return """You are CityCamp AI, a helpful assistant for the Tulsa Civic Engagement Platform. Your role is to help citizens stay informed and engaged with their local government.

You can help with:
- Information about city council meetings, agendas, and minutes
- Details about local campaigns and civic initiatives  
- Guidance on civic participation and engagement
- General information about Tulsa city government
- How to use the CityCamp AI platform

Key guidelines:
- Be helpful, friendly, and encouraging about civic engagement
- Provide accurate information about local government processes
- Encourage users to participate in democracy
- If you don't know specific details, suggest they check the Meetings or Campaigns pages
- Keep responses concise but informative
- Focus on Tulsa, Oklahoma civic matters

Always be encouraging about civic participation and democracy."""

    def _get_context_from_recent_meetings(self) -> str:
        """Get context from recent meetings to help answer questions"""
        try:
            recent_meetings = self.db.query(Meeting).order_by(Meeting.meeting_date.desc()).limit(5).all()
            
            if not recent_meetings:
                return "No recent meeting data available."
            
            context = "Recent Tulsa City Council meetings:\n"
            for meeting in recent_meetings:
                context += f"- {meeting.title} on {meeting.meeting_date.strftime('%B %d, %Y')}"
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
            active_campaigns = self.db.query(Campaign).filter(Campaign.status == 'active').limit(3).all()
            
            if not active_campaigns:
                return "No active campaigns available."
            
            context = "Active civic campaigns:\n"
            for campaign in active_campaigns:
                context += f"- {campaign.title}: {campaign.description[:100]}...\n"
                
            return context
        except Exception as e:
            logger.error(f"Error fetching campaign context: {e}")
            return "Unable to fetch campaign information."

    async def get_ai_response(self, user_message: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Get AI response using OpenAI"""
        logger.info(f"Getting AI response for message: {user_message[:50]}...")
        
        if not self.client:
            logger.warning("OpenAI client not available, using fallback response")
            return self._get_fallback_response(user_message)
        
        logger.info("OpenAI client available, attempting to get AI response")
        
        try:
            # Build context
            logger.info("Building context...")
            system_prompt = self._get_system_prompt()
            meeting_context = self._get_context_from_recent_meetings()
            campaign_context = self._get_context_from_campaigns()
            
            # Build messages for OpenAI
            messages = [
                {"role": "system", "content": f"{system_prompt}\n\nCurrent context:\n{meeting_context}\n{campaign_context}"}
            ]
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history[-10:]:  # Keep last 10 messages for context
                    messages.append({
                        "role": "user" if msg["sender"] == "user" else "assistant",
                        "content": msg["text"]
                    })
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            logger.info(f"Calling OpenAI API with {len(messages)} messages...")
            
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            logger.info(f"OpenAI API call successful, response length: {len(ai_response)}")
            return ai_response
            
        except Exception as e:
            logger.error(f"Error getting AI response: {e}", exc_info=True)
            return self._get_fallback_response(user_message)

    def _get_fallback_response(self, user_message: str) -> str:
        """Provide fallback responses when OpenAI is not available"""
        message_lower = user_message.lower()
        
        # Meeting-related queries
        if any(word in message_lower for word in ['meeting', 'council', 'agenda', 'minutes']):
            return """I can help you find information about Tulsa City Council meetings! 

You can:
- View upcoming meetings and agendas on the Meetings page
- Read past meeting minutes and summaries
- Get notifications about meetings that interest you

What specific meeting information are you looking for?"""

        # Campaign-related queries
        if any(word in message_lower for word in ['campaign', 'petition', 'initiative', 'vote']):
            return """CityCamp AI helps you stay informed about local campaigns and civic initiatives!

Check out the Campaigns page to:
- See active petitions and initiatives
- Learn about local ballot measures
- Find ways to get involved in your community

Is there a specific campaign or issue you're interested in?"""

        # Notification queries
        if any(word in message_lower for word in ['notification', 'alert', 'remind']):
            return """You can set up personalized notifications to stay engaged with local government!

Go to your Profile settings to:
- Get alerts about upcoming meetings
- Receive updates on campaigns you care about
- Set preferences for the topics that matter to you

Would you like help setting up notifications?"""

        # General greeting
        if any(word in message_lower for word in ['hello', 'hi', 'help', 'start']):
            return """Hello! I'm your CityCamp AI assistant, here to help you stay engaged with Tulsa local government.

I can help you with:
🏛️ City council meetings and agendas
📋 Local campaigns and initiatives  
🔔 Setting up notifications
🗳️ Civic participation opportunities

What would you like to know about?"""

        # Default response
        return """I'm here to help you stay informed about Tulsa local government and civic engagement.

You can ask me about:
- Upcoming city council meetings
- Local campaigns and initiatives
- How to get more involved in your community
- Using the CityCamp AI platform

You can also explore the Meetings and Campaigns pages for the latest information. What would you like to know?""" 