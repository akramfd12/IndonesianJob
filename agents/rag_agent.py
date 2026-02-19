from langchain.tools import tool
from langchain.agents import create_agent
from agents.tools import search_jobs
from config import *


system_prompt = """
    You are a job recommendation agent.

    When returning job results:
    - You MUST return ONLY valid JSON.
    - Return a list of objects.
    - Each object MUST contain:
        job_title
        company_name
        location
        work_type
        salary
        job_description
    - Do NOT omit any field.
    - Do NOT return explanations.
    - Do NOT wrap the JSON in markdown.
    
    Regardless of whether the query is broad or specific,
    you MUST always return results in the exact same JSON structure.

    Do NOT change formatting style.
    Do NOT switch to bullet points.
    Do NOT provide career advice.
    Return only structured job objects retrieved from the Qdrant.

"""

rag_subagent = create_agent(
               model= llm,
               tools=[search_jobs],
               system_prompt=system_prompt
)

@tool("job_recommendation", description="Handle job search and job-related insights using internal knowledge.")
def call_rag_agent(query: str):
    """
    Docstring for call_rag_agent
    
    :param query: User Typing
    :type query: str
    """
    result = rag_subagent.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].content



