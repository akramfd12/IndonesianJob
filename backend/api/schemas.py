# =========================================================
# Pydantic Schema Definitions
# =========================================================
# This file defines request/response models
# used by FastAPI for validation and documentation.
# =========================================================

# Import library dependencies
from pydantic import BaseModel
from typing import List, Optional


# =========================================================
# Chat Request Schema
# =========================================================
# Represents the request body for /chat endpoint.
#
# Fields:
# - user_input : Raw text entered by the user
# - user_id    : Unique session identifier (used for memory isolation)
# - top_k      : Optional override for number of job results
#                returned by RAG system
#
# Notes:
# - If top_k is None → backend will use default value
# - Backend also enforces max limit for safety
# =========================================================
class ChatRequest(BaseModel):
    user_input: str      # User query text
    user_id: str         # Unique session ID for conversation thread
    top_k: Optional[int] = None  # Optional result size override