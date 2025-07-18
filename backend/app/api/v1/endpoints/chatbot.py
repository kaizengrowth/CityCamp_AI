from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.services.chatbot_service import ChatbotService

router = APIRouter()

class ChatMessage(BaseModel):
    text: str
    sender: str  # 'user' or 'bot'

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = None

class ChatResponse(BaseModel):
    response: str
    success: bool
    error: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Send a message to the AI chatbot and get a response
    """
    try:
        chatbot_service = ChatbotService(db)
        
        # Convert conversation history to the format expected by the service
        history = None
        if request.conversation_history:
            history = [
                {"text": msg.text, "sender": msg.sender}
                for msg in request.conversation_history
            ]
        
        # Get AI response
        ai_response = await chatbot_service.get_ai_response(
            user_message=request.message,
            conversation_history=history
        )
        
        return ChatResponse(
            response=ai_response,
            success=True
        )
        
    except Exception as e:
        return ChatResponse(
            response="I'm sorry, I'm having trouble responding right now. Please try again later.",
            success=False,
            error=str(e)
        ) 