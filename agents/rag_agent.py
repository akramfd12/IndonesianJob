from langchain.tools import tool
from langchain.agents import create_agent
from agents.tools import search_jobs
from config import *


# =========================================================
# RAG SUB-AGENT CONFIGURATION
# =========================================================
# This agent is responsible ONLY for job recommendations.
# It retrieves structured job data from Qdrant via search_jobs tool.
# The output format is STRICTLY controlled via system prompt.
# =========================================================


# ---------------------------------------------------------
# SYSTEM PROMPT (STRICT JSON OUTPUT CONTROL)
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# CREATE RAG SUB-AGENT
# ---------------------------------------------------------
# - model → LLM defined in config
# - tools → search_jobs (retrieval from vector DB)
# - system_prompt → forces structured JSON output
rag_subagent = create_agent(
               model= llm,
               tools=[search_jobs],
               system_prompt=system_prompt
)


# ---------------------------------------------------------
# TOOL WRAPPER FOR MAIN AGENT
# ---------------------------------------------------------
# This function wraps the RAG sub-agent so it can be
# called as a tool inside a higher-level agent system.
@tool("job_recommendation", description="Handle job search and job-related insights using internal knowledge.")
def call_rag_agent(query: str):
    """
    Docstring for call_rag_agent
    
    :param query: User Typing
    :type query: str
    """

    # Invoke RAG sub-agent using LangChain message format
    result = rag_subagent.invoke({
        "messages": [
            {"role": "user", "content": query}
        ]
    })

    # Return ONLY the final message content
    # (Should already be strict JSON based on system prompt)
    return result["messages"][-1].content