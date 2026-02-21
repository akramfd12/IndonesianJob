# FastAPI routes for Job Intelligence API
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from api.schemas import ChatRequest
from agents.chatbot_agent import run_agent
from typing import List
import logging
import uvicorn
import os
from config import *





# Initialize FastAPI app
app = FastAPI(
    title="Job Search Service",
    description="Simple LLM Agent to search job vacancies in Indonesia",
    version="0.0.1",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# 1. Startup event
@app.on_event("startup")
async def startup_event():
    """
    Startup event for FastAPI:
    Validate credentials before accepting requests.
    """
    # Validating credentials
    try:
        missing = []
        if not OPENAI_API_KEY:
            missing.append("OPENAI_KEY")
        if not QDRANT_URL:
            missing.append("QDRANT_URL")
        if not MIXBREAD_API:
            missing.append("MIXBREAD_API")
        if not HF_TOKEN:
            missing.append("HF_TOKEN")
        if not RERANKER_MODEL:
            missing.append("RERANKER_MODEL")

        if missing:
            logging.warning(f"Missing credentials: {', '.join(missing)}")
        else:
            print("All credentials validated. Job Search Service ready!")

    except Exception as e:
        logging.error(f"Startup error: {e}")

#2. Root endpoint (starting)
@app.get("/")
async def root():
    return {
        "message": "Welcome to Job Search Service",
        "status": "healthy",
        "endpoints":{
            "chat": "/chat",
            "health": "/health",
            "history": "/history",
            "reset": "/reset",
            "docs": "/docs",
        }
    }

#3. Health endpoint
@app.get("/health")
async def health_check():
    try:
        return {"status": "healthy"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check health: {str(e)}")

#4. Chat endpoint
@app.post("/chat")
async def agent_chat(query: ChatRequest):
    try:
        result = run_agent(query.user_input)

        # Convert to JSON-safe object (important for LangChain objects)
        return jsonable_encoder(result)

    except Exception as e:
        logging.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 5. Chat history endpoint
@app.get("/history")
async def chat_history():
    try:
        return {"history": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chat history: {str(e)}")

# 6. Reset chat history endpoint
@app.post("/reset")
async def reset_chat_history():
    try:
        return {"message": "Chat history reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset chat history: {str(e)}")


