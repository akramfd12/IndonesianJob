from config import *
from db.qdrant import *
from db.sqlite import *
from services.matching_services import build_cv_query, split_cv_into_sections
from langchain_core.tools import tool
from langchain_community.utilities import SQLDatabase


#Tools for RAG
@tool
def search_jobs(query:str, top_k: int = 5, retrieve_k: int = 20) -> list: 
    """
    Retrieve and rerank job vacancies relevant to a user query.

    Purpose:
    - Use this tool when the user asks for job recommendations,
      suitable roles, or similar job positions.
    - This tool performs semantic retrieval and relevance reranking.

    IMPORTANT USAGE RULES:
    - Use ONLY for job discovery, job matching, or job descriptions.
    - Do NOT use this tool for salary statistics, counting jobs,
      or numerical aggregation (use text_to_sql instead).

    DATA INTEGRITY RULES:
    - ONLY use information explicitly present in the retrieved job data.
    - Do NOT infer seniority, eligibility, or experience level unless stated.
    - Do NOT assume fresh graduate acceptance unless explicitly mentioned.
    - You MAY summarize or rephrase job information,
      but MUST NOT add new facts.

    OUTPUT GUIDELINES:
    - Prefer structured, human-readable output.
    - Summarize long descriptions into key responsibilities and qualifications.
    - Avoid raw JSON or unformatted text dumps.

    BEHAVIOR RULE:
    - Do NOT ask clarification questions if a reasonable default interpretation exists.
    - Return the most relevant job results directly.
    """
    #Conenct to vector db
    vector_db_conn = get_vector_store(collection_name="indonesianjobs_collection")
    
    #Retrieval 
    get_jobs = vector_db_conn.similarity_search(query, k=retrieve_k)
    jobs_doc = [doc.page_content for doc in get_jobs]

    #Rerank
    reranked = mxbai.rerank(model = reranker,
                            query = query,
                            input = jobs_doc,
                            top_k = top_k,
                            return_input=True)
    return reranked


#Tools For Text To Sql
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
    
    IMPORTANT SALARY RULES:
    - The `salary` column is TEXT and MUST NOT be used for calculations.
    - For ALL numerical or statistical calculations involving salary,
      you MUST use:
        - `salary_min` for minimum salary
        - `salary_max` for maximum salary
    - Never use the `salary` column in WHERE, ORDER BY, or aggregation.

    Use this tool ONLY for:
    - AVG, MAX, MIN, COUNT, SUM
    - Salary statistics
    - Grouped numerical analysis

    SQL Rules:
    - ONLY SELECT statements are allowed
    - DO NOT use INSERT, UPDATE, DELETE, DROP, ALTER, or TRUNCATE
    - DO NOT use SELECT *
    - Always use LIMIT 5 unless the user explicitly asks otherwise

    Input:
    - query: A valid SQL SELECT statement using salary_min / salary_max
    """
    forbidden = ["insert", "update", "delete", "drop", "alter", "truncate"]
    if any(word in query.lower() for word in forbidden):
        return "ERROR: This tool only supports SELECT queries."

    if "salary" in query.lower() and not any(
        x in query.lower() for x in ["salary_min", "salary_max"]
    ):
        return "ERROR: Use salary_min and salary_max for salary calculations."

    return db.run(query)


# #tools for cv match
# query_text = build_cv_query(structured_cv)

# vectorstore = get_vector_store("indonesianjobs_collection")

# results = vectorstore.similarity_search_with_score(
#     query_text,
#     k=5
# )