# 1. Import Library
# Import library dependencies
import os
from dotenv import load_dotenv

# Import Langchain dependencies
from langchain_openai import OpenAI, ChatOpenAI, OpenAIEmbeddings
from openai import AsyncOpenAI

# Import Qdrant dependencies
from qdrant_client import AsyncQdrantClient
from langchain_qdrant import QdrantVectorStore
from sentence_transformer import CrossEncoder

# Import config
from config import *

# 2. Load .env dependencies
load_dotenv()

# Will try using OOP Class code structure to simulate production environment
# Implementation of Separation of Concerns (SoC)

#====== CLASS DEFINITION =====
# 3. Initialize Qdrant class
class QdrantManager:
    def __init__(self):
        """
        Function to initialize Qdrant Manager
        """
        # Setup OpenAI Embedding
        self.embeddings = OpenAIEmbeddings(
            openai_api_key = OPENAI_API_KEY,
            model = EMBEDDING_MODEL,
            dimensions=1536 # reduce the dimension to fit in qdrant
        )
        # Setup Qdrant Async Client
        self.async_client = AsyncQdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY
        )
    def get_vector_store(self):
        """
        Function to get the vector store of Qdrant

        Returns:
            QdrantVectorStore: Vector store of Qdrant
        """
        return QdrantVectorStore(
            client=self.async_client,
            collection_name=QDRANT_COLLECTION_NAME,
            embedding=self.embeddings
        )
    async def close_async_client(self):
        """
        Function to kill the async client if not used
        """
        await self.async_client.close()

# 4. Input SQlite database to Qdrant


class RerankerManager():
    def __init__(self):
        """
        Function to initialize Reranker
        """




class AIChatAssistant:
    def __init__(self):
        """
        Function to initialize AI Chat Assistant
        """

# # ==== Main Function =====\

# db = QdrantManager()
# vector_store = db.get_vector_store()

# # ==== Test Function =====\

# async def test_qdrant():
#     """
#     Function to test Qdrant
#     """
#     vector_store = db.get_vector_store()
#     vector_store.add_texts(
#         texts=["Hello World", "Hello Python"],
#         metadatas=[{"source": "test"}, {"source": "test"}]
#     )
#     print("Qdrant test passed")

# if __name__ == "__main__":
#     asyncio.run(test_qdrant())