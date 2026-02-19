# FastAPI routes for Job Intelligence API
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.schemas import ChatRequest, ChatResponse, JobResultResponse
from agents.chatbot_agent import agent
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



def parse_tool_results(agent_result: dict) -> List[JobResultResponse]:
    """
    Parse tool results dari agent output → List[JobResultResponse]
    
    Agent intermediate_steps berisi:
    [(AgentAction, tool_output), ...]
    
    tool_output dari rag_job_search:
    [{"score": 0.95, "input": "job text"}, ...]
    """
    jobs = []

    # Kalau agent gak pakai tool (misal: general question)
    if "intermediate_steps" not in agent_result:
        return jobs

    for step in agent_result["intermediate_steps"]:
        agent_action, tool_output = step

        # Hanya parse output dari rag_job_search
        if agent_action.tool == "rag_job_search" and tool_output:
            for idx, item in enumerate(tool_output):
                if isinstance(item, dict):
                    # Format job text: "Title - Company - Location - WorkType - Salary"
                    job_text = item.get("input", "")
                    parts = [p.strip() for p in job_text.split(" - ")]

                    jobs.append(JobResultResponse(
                        job_title=parts[0] if len(parts) > 0 else "Unknown",
                        company_name=parts[1] if len(parts) > 1 else "Unknown",
                        location=parts[2] if len(parts) > 2 else "Unknown",
                        work_type=parts[3] if len(parts) > 3 else "Unknown",
                        relevance_score=item.get("score", None)
                    ))

    return jobs

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
        if not OPENAI_KEY:
            missing.append("OPENAI_KEY")
        if not QDRANT_URL:
            missing.append("QDRANT_URL")
        if not QDRANT_COLLECTION_NAME:
            missing.append("QDRANT_COLLECTION_NAME")
        if not MIXBREAD_API:
            missing.append("MIXBREAD_API")
        if not HF_TOKEN:
            missing.append("HF_TOKEN")

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
@app.post("/chat", response_model=ChatResponse)
async def agent_chat(query: ChatRequest):
    """
    Chat with AI agent.
    Agent will parse natural language -> choose tool -> return response + job sources.
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent is not initialized")

    try:
        result = agent.invoke({"input": query.user_input})

        # Extract AI response text
        ai_response = result.get("output", "Sorry, I could not process your request.")

        # Parse tool results -> List[JobResultResponse]
        job_sources = parse_tool_results(result)

        logging.info(f"Chat response: {len(job_sources)} job sources found")

        # Return ChatResponse (structured output)
        return ChatResponse(
            response=ai_response,
            source=job_sources
        )

    except Exception as e:
        logging.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to chat: {str(e)}")

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


