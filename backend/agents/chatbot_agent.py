from config import *
from langchain.agents import create_agent
from agents.rag_agent import call_rag_agent
from agents.sql_agent import call_sql_agent


# =========================================================
# MAIN ORCHESTRATOR AGENT
# =========================================================
# This agent acts as the central router for the system.
#
# Responsibilities:
# - Decide whether to use RAG agent (job search)
# - Decide whether to use SQL agent (statistics)
# - Answer directly for small talk or non-tool queries
#
# It does NOT perform retrieval or SQL itself.
# It only delegates to sub-agents when needed.
# =========================================================


# ---------------------------------------------------------
# SYSTEM PROMPT (ROUTING LOGIC RULES)
# ---------------------------------------------------------
# Defines strict behavioral rules for:
# - Tool selection
# - When to answer directly
# - Avoiding unnecessary assumptions
# - Preventing over-filtering
# - Preventing unnecessary clarification questions
system_prompt=(
    """
   You are the main orchestrator for a job matching system.

    Available tools:
    - rag_agent: for job search and recommendations.
    - sql_agent: for statistics and numeric aggregations.

    Rules:
    - Use a tool ONLY if needed.
    - If the user is searching for jobs, use rag_agent.
    - If the user asks for statistics or numbers, use sql_agent.
    - If the question is unrelated to jobs:
        - If it is greeting or light small talk, respond briefly.
        - Otherwise, politely say that you specialize in job-related assistance.
        - Do not use any tool.
    - Do not add filters or assumptions that the user did not mention.
    - Do not ask unnecessary clarification.
    - Do not generate forms.
    """
)


# ---------------------------------------------------------
# CREATE MAIN AGENT
# ---------------------------------------------------------
# - model → LLM initialized in config
# - tools → wrapper functions for RAG & SQL sub-agents
# - system_prompt → controls orchestration logic
#
# This agent routes user intent dynamically.
agent = create_agent(
    model=llm,
    tools=[call_rag_agent,call_sql_agent],
    system_prompt=system_prompt    
)