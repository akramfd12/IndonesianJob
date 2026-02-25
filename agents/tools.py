from config import *
from db.qdrant import *
from db.sqlite import *
from services.matching_services import parse_cv_with_llm, build_cv_query
from langchain_core.tools import tool
from langchain_community.utilities import SQLDatabase
from langchain_core.runnables import RunnableConfig

# Tools for RAG Agent
@tool
def search_jobs(
    query: str,
    top_k: int = 5,
    retrieve_k: int = 20,
    config: RunnableConfig = None
) -> list:
    """
    Retrieve relevant job postings based on a search query.
    """

    # =====================================================
    # 🔥 Ambil top_k dari runtime config (kalau ada)
    # =====================================================
    if config and "configurable" in config:
        runtime_top_k = config["configurable"].get("top_k")
        if runtime_top_k:
            top_k = runtime_top_k

    # Connect to vector db
    vector_db_conn = get_vector_store(
        collection_name="indonesianjobs_collection"
    )
    
    # Step 1: Retrieve candidates (lebih besar untuk rerank)
    docs = vector_db_conn.similarity_search(query, k=retrieve_k)

    # Step 2: Extract page_content for reranking
    contents = [doc.page_content for doc in docs]

    # Step 3: Rerank pakai top_k final
    reranked = mxbai.rerank(
        model=reranker,
        query=query,
        input=contents,
        top_k=top_k,
        return_input=True
    )
    
    # Step 4: Map rerank indices back to docs
    results = []
    for item in reranked.data:
        doc = docs[item.index]

        results.append({
            "job_title": doc.metadata.get("job_title"),
            "company_name": doc.metadata.get("company_name"),
            "location": doc.metadata.get("location"),
            "work_type": doc.metadata.get("work_type"),
            "salary": doc.metadata.get("salary"),
            "job_description": doc.page_content
        })

    return results


# =========================================================
# 🗄️ READ-ONLY SQL TOOL
# =========================================================
# This tool is used by the SQL Agent to:
# - Execute safe SELECT queries
# - Enforce salary calculation rules
# - Prevent destructive SQL operations
# - Guard against misuse of TEXT salary column
# =========================================================

#Tools For Text To Sql Agent
db = SQLDatabase.from_uri("sqlite:///db/jobs.db?mode=ro",
                          engine_args={"connect_args": {"uri": True}}
                          )

@tool
def sql_readonly_query(query: str) -> str:
    """
    Execute a READ-ONLY SQL query on the jobs database.

    DATABASE SCHEMA:
    jobs.job_title TEXT,
    jobs.company_name TEXT,
    jobs.location TEXT,
    jobs.work_type TEXT,
    jobs.salary TEXT,
    jobs.job_description TEXT,
    jobs.salary_min TEXT,
    jobs.salary_max TEXT

    DIALECT:
    SQLite

    SALARY RULES:
    - The `salary` column is TEXT and MUST NOT be used in calculations.
    - For numerical salary calculations, use `salary_min` and `salary_max`.
    - `salary_min` and `salary_max` are stored as TEXT.
    - Always CAST them to INTEGER before aggregation.
    - Never use `salary` in WHERE, ORDER BY, or aggregation.
    - Never use the salary column.
    - Use salary_min and salary_max only.
    - Always CAST salary_min and salary_max to REAL.
    - Always filter:
    salary_min IS NOT NULL
    AND salary_max IS NOT NULL
    AND salary_min != ''
    AND salary_max != ''
    AND CAST(salary_min AS INTEGER) > 0
    AND CAST(salary_max AS INTEGER) > 0

    QUERY RULES:
    - ONLY SELECT statements are allowed.
    - DO NOT use INSERT, UPDATE, DELETE, DROP, ALTER, or TRUNCATE.
    - DO NOT use SELECT *.

    Input:
    - query: A valid SQL SELECT statement using salary_min / salary_max
    """

    # -----------------------------------------------------
    # 🚫 Block destructive SQL commands
    # -----------------------------------------------------
    forbidden = ["insert", "update", "delete", "drop", "alter", "truncate"]
    if any(word in query.lower() for word in forbidden):
        return "ERROR: This tool only supports SELECT queries."

    # -----------------------------------------------------
    # 🛡 Prevent misuse of raw salary TEXT column
    # -----------------------------------------------------
    # Ensures salary calculations use salary_min / salary_max only
    if "salary" in query.lower() and not any(
        x in query.lower() for x in ["salary_min", "salary_max"]
    ):
        return "ERROR: Use salary_min and salary_max for salary calculations."

    # -----------------------------------------------------
    # 📝 Debug log (helps during development & monitoring)
    # -----------------------------------------------------
    print("Generated SQL:", query)

    # -----------------------------------------------------
    # ▶ Execute validated query (read-only)
    # -----------------------------------------------------
    return db.run(query)


# =========================================================
# 📄 CV-BASED JOB SEARCH TOOL
# =========================================================
# This tool is used to generate job recommendations
# based on the semantic content of a user's CV.
#
# Flow:
# 1️⃣ Parse CV using LLM
# 2️⃣ Convert structured CV into semantic query
# 3️⃣ Perform vector similarity search
# 4️⃣ Return ranked job results with similarity score
# =========================================================

@tool
def cv_search_jobs(cv_text: str, k: int = 5) -> list:
    """
    Search job recommendations based on CV text.
    """

    # -----------------------------------------------------
    # 1️⃣ Parse CV into structured JSON format
    # -----------------------------------------------------
    structured_cv = parse_cv_with_llm(cv_text)

    # -----------------------------------------------------
    # 2️⃣ Build semantic query from structured CV
    # -----------------------------------------------------
    query_text = build_cv_query(structured_cv)

    # -----------------------------------------------------
    # 3️⃣ Connect to vector database (Qdrant)
    # -----------------------------------------------------
    vectorstore = get_vector_store("indonesianjobs_collection")

    # Perform similarity search with score
    # k determines number of results returned
    results = vectorstore.similarity_search_with_score(
        query_text,
        k=k
    )

    # -----------------------------------------------------
    # 4️⃣ Format output into clean JSON structure
    # -----------------------------------------------------
    formatted = []
    for doc, score in results:
        formatted.append({
            "job_title": doc.metadata.get("job_title"),
            "company_name": doc.metadata.get("company_name"),
            "location": doc.metadata.get("location"),
            "work_type": doc.metadata.get("work_type"),
            "salary": doc.metadata.get("salary"),
            "match_score": round(float(score), 4),  # similarity score
            "job_description": doc.page_content
        })

    # Return structured recommendations
    return formatted


if __name__ == "__main__":
    search_jobs()