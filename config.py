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

from huggingface_hub import login
from mixedbread import Mixedbread

from dotenv import load_dotenv

load_dotenv()

# config the logging
logging.basicConfig(
    level=logging.INFO, # Set the minimum logging level to capture (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s', # Define the log message format
    datefmt='%Y-%m-%d %H:%M:%S' # Define the timestamp format
)

# load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-5-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")

MIXBREAD_API = os.getenv("MIXBREAD_API")
HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY")
RERANKER_MODEL = os.getenv("RERANKER_MODEL")


client = OpenAI(api_key=OPENAI_API_KEY)

# initialize LLM and embeddings
llm = ChatOpenAI(model=CHAT_MODEL, api_key=OPENAI_API_KEY, temperature=0)
embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=OPENAI_API_KEY)
logging.info(f"Using chat model: {CHAT_MODEL} and embedding model: {EMBEDDING_MODEL}")

mxbai = Mixedbread(api_key=MIXBREAD_API)
reranker = "mixedbread-ai/mxbai-rerank-base-v2"
logging.info(f"Initialized reranker model: {reranker}")
# initialize cross-encoder for reranking
# reranker = CrossEncoder(RERANKER_MODEL) 
# logging.info(f"Initialized reranker CrossEncoder with model: {RERANKER_MODEL}")



