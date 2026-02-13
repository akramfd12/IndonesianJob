# 1. Load .env dependencies & Initialize OpenAI, Qdrant, HF model variables
load_dotenv()

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_COLLECTION_NAME = "job_posting_miqdam"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-large" # later will be reduce the dimension to 1536 to fit in qdrant
CHAT_MODEL = "gpt-5-mini"
RERANKER_MODEL = "mixedbread-ai/mxbai-rerank-large-v1"