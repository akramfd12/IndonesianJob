from config import *
from langchain_core.documents import Document
import logging


# =========================================================
# CONVERT SQL ROWS → LANGCHAIN DOCUMENT OBJECTS
# =========================================================
def create_document_jobs(rows: list):
    """
    Transform SQL query result (list of tuples)
    into LangChain Document objects.

    Each row represents one job record.

    Returns:
    - List[Document] → ready for embedding & vector storage
    """

    documents = []

    for row in rows:
        # Unpack database row
        job_id, job_title, company_name, location, work_type, salary, salary_min, salary_max, job_description = row

        # Text content that will be embedded
        # (This is what the vector embedding model "reads")
        content = f"""
        Job Title: {job_title}

        Job Description: {job_description}
        """.strip()

        # Create LangChain Document object
        # page_content → used for semantic search
        # metadata → structured filtering later (location, salary, etc.)
        doc = Document(
            page_content=content,
            metadata={
                "id": str(job_id),  # always safe to cast to string
                "job_title": job_title,
                "company_name": company_name,
                "location": location,
                "work_type": work_type,
                "salary": salary,
                "salary_min": salary_min,
                "salary_max": salary_max,
            }
        )

        documents.append(doc)

    return documents


# =========================================================
# CREATE QDRANT COLLECTION & INSERT DOCUMENTS
# =========================================================
def create_qdrant_collection(collection_name: str, documents: list):
    """
    Create a new Qdrant collection and insert embedded documents.

    Logic:
    - If collection already exists → skip ingestion
    - If not → create new collection & upload vectors
    """

    # Initialize Qdrant client
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        prefer_grpc=True,   # faster communication
        timeout=60
    )

    # Check existing collections
    collections = client.get_collections().collections
    existing_names = [c.name for c in collections]

    # Safety guard: prevent duplicate ingestion
    if collection_name in existing_names:
        print(f"Collection '{collection_name}' already exists. Skipping ingestion.")
        return  # 🔒 Stop execution if already exists

    # If collection does not exist → create & insert
    print(f"Creating collection '{collection_name}'...")

    try:
        # Generate unique IDs for each document
        uuids = [str(uuid4()) for _ in range(len(documents))]

        # Create collection and upload vectors
        return QdrantVectorStore.from_documents(
            documents=documents,
            embedding=embeddings,   # embedding model from config
            ids=uuids,
            prefer_grpc=True,
            api_key=QDRANT_API_KEY,
            url=QDRANT_URL,
            collection_name=collection_name,
            batch_size=16   # upload in batches (performance tuning)
        )

    except Exception as e:
        # Wrap error for better debugging visibility
        raise RuntimeError(f"[QDRANT] create collection failed: {e}")


# =========================================================
# CONNECT TO EXISTING QDRANT COLLECTION
# =========================================================
def get_vector_store(collection_name: str):
    """
    Connect to an existing Qdrant collection.

    Used for:
    - Semantic search
    - Retrieval in RAG pipeline
    """

    vector_store = QdrantVectorStore.from_existing_collection(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        collection_name=collection_name,
        embedding=embeddings
    )

    # Logging for monitoring connection
    logging.info(
        f"Connected to Qdrant at {QDRANT_URL}, collection: {collection_name}"
    )

    return vector_store