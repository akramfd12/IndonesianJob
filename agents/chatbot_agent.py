from config import *
from langchain.agents import create_agent
from agents.rag_agent import call_rag_agent
from agents.sql_agent import call_sql_agent

system_prompt=(
    """
   You are the main orchestrator.

    Available tools:
    - rag_agent: for job search and recommendations.
    - sql_agent: for statistics and numeric aggregations.

    Rules:
    - Always use a tool to answer.
    - If the user is searching for jobs, use rag_agent.
    - If the user asks for statistics or numbers, use sql_agent.
    - Do not add filters or assumptions that the user did not mention.
    - Do not ask unnecessary clarification.
    - Do not generate forms.
    """
)

agent = create_agent(
    model=llm,
    tools=[call_rag_agent,call_sql_agent],
    system_prompt=system_prompt    
    )

def run_agent(user_input: str):
    result = agent.invoke({
        "messages": [
            {"role": "user", "content": user_input}
        ]
    })

    return result