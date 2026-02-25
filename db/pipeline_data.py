from db.sqlite import *
from db.jobs_prepared import *
from db.qdrant import *

# =========================================================
# MANUAL INGESTION SECTION (OPTIONAL / ONE-TIME SETUP)
# =========================================================

# Insert data into SQLite database
# 1. Read raw JSONL scraped data
# 2. Clean & normalize salary fields
# 3. Create SQLite DB and insert data
#
# jobs = read_jsonl("data/jobs.jsonl")
# data = clean_salary()
# create_sqlite(db_name="jobs", table_name="jobs", source_data=data)


# Insert data into Qdrant vector database
# 1. Read structured jobs from SQLite
# 2. Convert rows into LangChain Documents
# 3. Create Qdrant collection & upload embeddings
#
# a = read_sql_jobs(db_name="jobs.db")
# b = create_document_jobs(rows=a)
# create_qdrant_collection(collection_name="indonesianjobs_collection", documents=b)


# =========================================================
# AUTOMATED VECTOR DATABASE BUILDER
# =========================================================
def build_vector_database():
    """
    Build vector database from existing SQLite data.

    Flow:
    SQLite → Convert to Documents → Embed → Store in Qdrant
    """

    # Step 1: Read job records from SQLite database
    a = read_sql_jobs(db_name="db/jobs.db")

    # Step 2: Convert SQL rows into LangChain Document objects
    b = create_document_jobs(rows=a)

    # Step 3: Create Qdrant collection & upload vector embeddings
    create_qdrant_collection(
        collection_name="indonesianjobs_collection",
        documents=b
    )

    # Confirmation message
    print("Vector DB successfully built.")


# =========================================================
# SCRIPT ENTRY POINT
# =========================================================
if __name__ == "__main__":
    # Run vector DB builder only if this file is executed directly
    build_vector_database()