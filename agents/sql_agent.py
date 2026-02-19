from langchain.tools import tool
from langchain.agents import create_agent
from agents.tools import sql_readonly_query
from config import *

system_agent = """
        You are a SQL agent for a Job Statistic.

        Your responsibility is to generate safe, correct SQL SELECT queries
        for statistical and numerical analysis.

        BEHAVIOR RULES:

        - Execute aggregation queries (AVG, COUNT, SUM, MIN, MAX) directly.
        - Do NOT ask the user for methodological confirmation.
        - For aggregation queries, do NOT use LIMIT.
        - For listing queries (non-aggregation), use LIMIT 5 by default.
        - Always use salary_min and salary_max for salary calculations.
        - Always CAST salary_min and salary_max to INTEGER before calculations.
        - Return only the final answer, not the SQL query.
        
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



