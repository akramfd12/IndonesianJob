from config import *
from db.qdrant import *
from db.sqlite import *
from services.matching_services import *
from langchain_core.tools import tool
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit


#Tools for RAG Agent
@tool
def search_jobs(query: str, top_k: int = 5, retrieve_k: int = 20) -> list:
    """
    Retrieve relevant job postings based on a search query.

    Args:
        query (str): Job-related search query.
        top_k (int): Number of results to return.
        retrieve_k (int): Number of candidates to retrieve before ranking.

    Returns:
        list: Ranked job results.
    """

    #Conenct to vector db
    vector_db_conn = get_vector_store(collection_name="indonesianjobs_collection")
    
    # Step 1: Retrieve full docs
    docs = vector_db_conn.similarity_search(query, k=retrieve_k)

    # Step 2: Extract page_content for reranking
    contents = [doc.page_content for doc in docs]

    # Step 3 : Rerank
    reranked = mxbai.rerank(model = reranker,
                            query = query,
                            input = contents,
                            top_k = top_k,
                            return_input=True)
    
    # Step 4 : Map rerank indices back to docs
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


#Tools For Text To Sql Agent
db = SQLDatabase.from_uri("sqlite:///db/jobs.db?mode=ro",
                          engine_args={"connect_args": {"uri": True}}
                          )

# toolkit = SQLDatabaseToolkit(db=db, llm=model)

# tools = toolkit.get_tools()

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

    QUERY RULES:
    - ONLY SELECT statements are allowed.
    - DO NOT use INSERT, UPDATE, DELETE, DROP, ALTER, or TRUNCATE.
    - DO NOT use SELECT *.

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
@tool
def cv_search_jobs(query_text:str, upload_cv:str, k: int) -> list:
  """
  Docstring for cv_search_jobs
  
  :param query_text: Description
  :type query_text: str
  :param k: Description
  :type k: int
  :return: Description
  :rtype: list
  """
  cv_text = extract_text_from_pdf(file_path=upload_cv)
  parsing_cv = parse_cv_with_llm(cv_text=cv_text)
  query_text = build_cv_query(structured_cv=parsing_cv)


  vectorstore = get_vector_store("indonesianjobs_collection")

  results = vectorstore.similarity_search_with_score(
        query_text,
        k=5
    )

  return results


if __name__ == "__main__":
    search_jobs()