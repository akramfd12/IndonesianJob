from langchain.tools import tool
from langchain.agents import create_agent
from agents.tools import sql_readonly_query
from config import *

# =========================================================
# SQL SUB-AGENT CONFIGURATION
# =========================================================
# This agent is responsible for:
# - Generating SAFE SQLite SELECT queries
# - Performing statistical & aggregation analysis
# - Returning computed numerical results ONLY
#
# It must follow strict validation & formatting rules.
# =========================================================


# ---------------------------------------------------------
# SYSTEM PROMPT FOR SQL STATISTICAL ENGINE
# ---------------------------------------------------------
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


QUERY VALIDATION:
- If any salary calculation does NOT include all required salary filters,
  the query is invalid and must be rewritten.
- If midpoint formula is not used, the query is invalid.

OUTPUT RULES:
- Return ONLY the final result.
- Do NOT include explanations.
- Do NOT include notes.
- Do NOT describe filtering logic.
- If result is NULL, return: Tidak ada data.
"""


# ---------------------------------------------------------
# CREATE SQL SUB-AGENT
# ---------------------------------------------------------
# - model → LLM defined in config
# - tools → sql_readonly_query (safe SELECT execution only)
#
# This sub-agent is focused on structured SQL-based analysis.
sql_subagent = create_agent(
               model= llm,
               tools=[sql_readonly_query] 
)


# ---------------------------------------------------------
# TOOL WRAPPER FOR MAIN AGENT
# ---------------------------------------------------------
# This function wraps the SQL sub-agent so it can be
# called as a tool inside a higher-level orchestration agent.
#
# It handles:
# - Statistical queries
# - Aggregations (AVG salary, COUNT jobs, etc.)
# - Numerical insights
@tool("job_statistics", description="Handle statistical and numerical analysis of job listing data including counts, averages, and aggregations.")
def call_sql_agent(query: str):
    """
    Docstring for call_sql_agent
    
    :param query: Description
    :type query: str
    """

    # Invoke SQL sub-agent using LangChain message format
    result = sql_subagent.invoke({
        "messages": [
            {"role": "user", "content": query}
        ]
    })

    # Return ONLY the final computed result
    # (No explanations, strictly controlled by system prompt)
    return result["messages"][-1].content