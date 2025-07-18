from fastapi import APIRouter
from .endpoints import auth, meetings, scraper, chatbot

api_router = APIRouter()

# Include existing endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(meetings.router, prefix="/meetings", tags=["meetings"])
api_router.include_router(scraper.router, prefix="/scraper", tags=["scraper"])
api_router.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"])

# TODO: Add other routers as they are created
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
# api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
# api_router.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"]) 