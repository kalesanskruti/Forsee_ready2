from typing import Any, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import google.generativeai as genai
from app.core.config import settings
from app.api import deps
from app.db.models import User
from loguru import logger

router = APIRouter()

class ChatMessage(BaseModel):
    role: str # 'user' or 'model'
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []

class ChatResponse(BaseModel):
    response: str

# System prompt to give Gemini context about Forsee AI
SYSTEM_PROMPT = """
You are the Forsee AI Assistant, an expert in industrial predictive maintenance, 
health monitoring, and equipment reliability. 

Your goal is to help users understand their asset health, interpret RUL (Remaining Useful Life) 
predictions, and provide guidance on maintenance scheduling.

Context: Forsee AI is a state-of-the-art software that monitors industrial assets (pumps, turbines, etc.) 
using physically-grounded ML models.

Tone: Professional, intelligent, helpful, and technically accurate.

Constraint: If asked about things completely unrelated to Forsee AI or industrial reliability, 
politely steer the conversation back to those topics.
"""

@router.post("/", response_model=ChatResponse)
async def chat_with_gemini(
    request: ChatRequest,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Generate a response using Google Gemini
    """
    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API Key not configured")

    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-flash-latest', system_instruction=SYSTEM_PROMPT)
        
        # Convert history to Gemini format
        chat_history = []
        for msg in request.history:
            chat_history.append({
                "role": "user" if msg.role == "user" else "model",
                "parts": [msg.content]
            })

        # Start a chat session with history
        chat = model.start_chat(history=chat_history)
        
        # Send the user's message
        response = chat.send_message(request.message)
        
        # Handle cases where response.text might be unavailable/blocked
        try:
            bot_text = response.text
        except Exception:
            bot_text = "I'm sorry, I cannot answer that request due to safety or technical restrictions."

        return ChatResponse(response=bot_text)
        
    except Exception as e:
        import traceback
        logger.error(f"Gemini Error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")
