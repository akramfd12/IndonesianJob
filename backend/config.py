import os
import logging

import pandas as pd
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from openai import OpenAI

from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from uuid import uuid4

# from huggingface_hub import login
from mixedbread import Mixedbread

from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================
# Loads variables from .env file into environment
# Used for API keys and configuration values
load_dotenv()


# =========================================================
# LOGGING CONFIGURATION
# =========================================================
# Configure global logging behavior for the application
# This ensures consistent log format across modules
logging.basicConfig(
    level=logging.INFO,  # Minimum level to capture (DEBUG < INFO < WARNING < ERROR < CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
    datefmt='%Y-%m-%d %H:%M:%S'  # Timestamp format
)


# =========================================================
# LOAD ENVIRONMENT VARIABLES (CONFIGURATION VALUES)
# =========================================================
# API Keys & Model Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-5-mini")  # Default chat model
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")  # Default embedding model
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")

# Reranking / Hybrid Search Configuration
MIXBREAD_API = os.getenv("MIXBREAD_API")
# HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY")
RERANKER_MODEL = os.getenv("RERANKER_MODEL")


# =========================================================
# INITIALIZE OPENAI CLIENT
# =========================================================
# Direct OpenAI client (if needed outside LangChain)
client = OpenAI(api_key=OPENAI_API_KEY)


# =========================================================
# INITIALIZE LLM & EMBEDDINGS (CORE AI COMPONENTS)
# =========================================================
# LLM → used for reasoning, agent logic, formatting
# Embeddings → used for vector search in Qdrant

llm = ChatOpenAI(
    model=CHAT_MODEL,
    api_key=OPENAI_API_KEY,
    temperature=0  # Deterministic output (important for structured agents)
)

embeddings = OpenAIEmbeddings(
    model=EMBEDDING_MODEL,
    api_key=OPENAI_API_KEY
)

logging.info(f"Using chat model: {CHAT_MODEL} and embedding model: {EMBEDDING_MODEL}")


# =========================================================
# INITIALIZE RERANKING MODEL (HYBRID SEARCH ENHANCEMENT)
# =========================================================
# Mixedbread reranker improves search relevance
# after vector retrieval (semantic + rerank pipeline)

mxbai = Mixedbread(api_key=MIXBREAD_API)

# Default reranker model (string reference)
reranker = RERANKER_MODEL

logging.info(f"Initialized reranker model: {RERANKER_MODEL}")


# =========================================================
# OPTIONAL: CROSS-ENCODER RERANKER (COMMENTED OUT)
# =========================================================
# Alternative approach using HuggingFace CrossEncoder
# Uncomment if switching to local reranking model

# reranker = CrossEncoder(RERANKER_MODEL) 
# logging.info(f"Initialized reranker CrossEncoder with model: {RERANKER_MODEL}")