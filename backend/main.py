# backend/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Add CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (you can restrict this to specific domains)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model for chat endpoint
class ChatRequest(BaseModel):
    question: str

@app.post("/chat")
async def chat(request: ChatRequest):
    # Simple response for testing purposes
    # In production, use OpenAI, Qdrant, and DB connections
    user_message = request.question.lower()

    if "hello" in user_message or "hi" in user_message:
        bot_response = "Hello! How can I help you with the book today?"
    elif "chapter" in user_message:
        bot_response = "This textbook covers chapters on Physical AI and Humanoid Robotics. Which specific topic would you like to discuss?"
    elif "robot" in user_message:
        bot_response = "Humanoid robots are robots with human-like form and capabilities. They're designed to navigate human environments."
    else:
        bot_response = f"I received your message: '{request.question}'. This is a sample response from the chatbot. In a full implementation, I would use OpenAI and Qdrant to provide a contextual answer based on the textbook content."

    return {"answer": bot_response}
