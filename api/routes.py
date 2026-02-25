# =========================================================
# FASTAPI ROUTES - JOB INTELLIGENCE API
# =========================================================
# This file defines all HTTP endpoints for:
# - Chat with AI agent
# - Health monitoring
# - Chat history management
# - Reset session
# - CV upload & semantic matching
# =========================================================

# Import required dependencies
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.schemas import ChatRequest
from agents.run_agent import run_agent
from typing import List
import logging
import uvicorn
import os
from agents.langgraph_agent import memory
from services.matching_services import extract_text_from_upload
from agents.tools import cv_search_jobs
from config import *


# =========================================================
# Initialize FastAPI Application
# =========================================================
# Metadata is automatically shown in Swagger docs (/docs)
app = FastAPI(
    title="Job Search Service",
    description="Simple LLM Agent to search job vacancies in Indonesia",
    version="0.0.1",
)


# =========================================================
# CORS Middleware
# =========================================================
# Allows frontend apps (e.g., Streamlit) to call this API.
# "*" means allow all origins (for development).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


# =========================================================
# 1️⃣ Startup Event
# =========================================================
# Runs once when the server starts.
# Used to validate required environment variables.
@app.on_event("startup")
async def startup_event():
    """
    Startup event for FastAPI:
    Validate credentials before accepting requests.
    """
    try:
        missing = []

        # Check required credentials
        if not OPENAI_API_KEY:
            missing.append("OPENAI_KEY")
        if not QDRANT_URL:
            missing.append("QDRANT_URL")
        if not MIXBREAD_API:
            missing.append("MIXBREAD_API")
        # if not HF_TOKEN:
        #     missing.append("HF_TOKEN")
        if not RERANKER_MODEL:
            missing.append("RERANKER_MODEL")

        # Log missing credentials
        if missing:
            logging.warning(f"Missing credentials: {', '.join(missing)}")
        else:
            print("All credentials validated. Job Search Service ready!")

    except Exception as e:
        logging.error(f"Startup error: {e}")


# =========================================================
# 2️⃣ Root Endpoint
# =========================================================
# Provides general information about service status.
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


# =========================================================
# 3️⃣ Health Endpoint
# =========================================================
# Used for uptime monitoring / load balancer checks.
@app.get("/health")
async def health_check():
    try:
        return {"status": "healthy"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check health: {str(e)}")


# =========================================================
# 4️⃣ Chat Endpoint (Main Agent Entry Point)
# =========================================================
# Handles:
# - User chat input
# - Runtime top_k validation
# - Agent execution
# - Return structured response
@app.post("/chat")
async def agent_chat(query: ChatRequest):
    try:
        # =================================================
        # TOP_K HANDLING (SAFE DEFAULT + MAX CAP)
        # =================================================
        DEFAULT_TOP_K = 5
        MAX_TOP_K = 20

        # Use default if top_k not provided
        effective_top_k = query.top_k or DEFAULT_TOP_K

        # Cap maximum value to prevent abuse
        effective_top_k = min(effective_top_k, MAX_TOP_K)

        # =================================================
        # RUN AGENT WITH RUNTIME CONFIG
        # =================================================
        result = run_agent(
            user_input=query.user_input,
            user_id=query.user_id,
            top_k=effective_top_k
        )

        # Get last AI message from LangGraph state
        last_message = result["messages"][-1]

        # Extract token usage metadata (if available)
        token_usage = last_message.response_metadata.get("token_usage", {})

        # Extract tool call info (for debugging / transparency)
        tool_calls = getattr(last_message, "tool_calls", [])

        return {
            "answer": last_message.content,
            "token_usage": token_usage,
            "tool_calls": tool_calls
        }

    except Exception as e:
        logging.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================
# 5️⃣ Chat History Endpoint
# =========================================================
# Retrieves conversation memory from LangGraph MemorySaver.
@app.get("/history")
async def chat_history(user_id: str):
    try:
        state = memory.get(user_id)

        # If no state found, return empty history
        if not state :
            return {"history": []}
        
        messages = state["messages"]

        # Format messages into simple JSON structure
        formated = [
            {
                "role": "user" if m.type == "human" else "assistant",
                "content": m.content
            }
            for m in messages
        ]

        return {"history": formated}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chat history: {str(e)}")


# =========================================================
# 6️⃣ Reset Chat History Endpoint
# =========================================================
# Clears conversation memory for specific user session.
@app.post("/reset")
async def reset_chat_history(user_id: str):
    try:
        memory.delete_thread(user_id)
        return {"message": "Chat history reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset chat history: {str(e)}")


# =========================================================
# 7️⃣ CV Upload Endpoint
# =========================================================
# Handles:
# - PDF upload validation
# - Text extraction
# - CV-based semantic job matching
@app.post("/upload-cv")
async def upload_cv(file: UploadFile = File(...)):

    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    # 1️⃣ Extract text from uploaded PDF
    cv_text = extract_text_from_upload(file)

    # Validate extracted text
    if not cv_text.strip():
        raise HTTPException(status_code=400, detail="CV text empty")

    # 2️⃣ Call CV matching tool
    results = cv_search_jobs.invoke({
        "cv_text": cv_text,
        "k": 5
    })

    return {
        "status": "success",
        "total_results": len(results),
        "recommendations": results
    }