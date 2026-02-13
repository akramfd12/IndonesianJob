from config import *
from langchain_core.documents import Document
import logging

def create_document_jobs(rows: list):
    documents = []

    for row in rows:
        job_id, job_title, company_name, location, work_type, salary,salary_min, salary_max,job_description = row

        content = f"""
        Job Title: {job_title}

        Job Description:{job_description}
        """.strip()

        doc = Document(
            page_content=content,
            metadata={
                "id": str(job_id),
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


def create_qdrant_collection(collection_name: str, documents: list):
    """
    Insert document into qdrant and create collection
    """
    try:
        uuids = [str(uuid4()) for _ in range(len(documents))]

        return QdrantVectorStore.from_documents(
            documents=documents,
            embedding=embeddings,
            ids=uuids,
            prefer_grpc=True,
            api_key=QDRANT_API_KEY,
            url=QDRANT_URL,
            collection_name=collection_name
        )
    except Exception as e:
        raise RuntimeError(f"[QDRANT] create collection failed: {e}")


# intialize Qdrant vector store
def get_vector_store(collection_name: str):
    """
    Connect to an existing collection for retrieval.
    """
    vector_store =  QdrantVectorStore.from_existing_collection(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        collection_name=collection_name,
        embedding=embeddings
    )
    logging.info(f"Connected to Qdrant at {QDRANT_URL}, collection: {QDRANT_COLLECTION_NAME}")\
    
    return vector_store