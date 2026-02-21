from langchain.tools import tool
from langchain.agents import create_agent
from agents.tools import sql_readonly_query
from config import *

system_agent = """
You are a SQL statistical engine for job listing data.

Your task is to generate safe SQLite SELECT queries
and return the computed result only.

GENERAL RULES:
- Aggregation queries (COUNT, AVG, SUM, MIN, MAX) must NOT use LIMIT.
- Listing queries must use LIMIT 5.
- Use case-insensitive partial matching for text filters:
  LOWER(column) LIKE '%keyword%'.
- Never use exact equality (=) for text matching.

JOB TITLE FILTER:
- Apply job_title filtering ONLY if the user explicitly mentions
  a specific job role or profession.
- If no specific role is mentioned, do NOT filter by job_title.

SALARY RULES (apply ONLY when calculating salary statistics):
- Use salary_min and salary_max only.
- Always CAST them to INTEGER.
- Exclude rows where salary_min or salary_max is NULL, empty, or 0.

OUTPUT RULES:
- Return ONLY the final result.
- Do NOT include explanations.
- Do NOT include notes.
- Do NOT describe filtering logic.
- If result is NULL, return: Tidak ada data.
"""

sql_subagent = create_agent(
               model= llm,
               tools=[sql_readonly_query] 
)

@tool("job_statistics", description="Handle statistical and numerical analysis of job listing data including counts, averages, and aggregations.")
def call_sql_agent(query: str):
    """
    Docstring for call_sql_agent
    
    :param query: Description
    :type query: str
    """
    result = sql_subagent.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].content



