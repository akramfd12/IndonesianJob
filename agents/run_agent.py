from langchain_core.messages import HumanMessage
from agents.langgraph_agent import graph


# =========================================================
# RUN AGENT WRAPPER
# =========================================================
# This function is the execution entry point for the system.
#
# Responsibilities:
# - Receive user input from API layer
# - Inject runtime configuration (thread_id, top_k)
# - Invoke LangGraph workflow
# - Return full graph result
#
# It acts as a bridge between FastAPI and LangGraph.
# =========================================================


def run_agent(user_input: str, user_id: str, top_k: int):
    """
    Execute LangGraph agent with runtime configuration.

    Parameters:
    - user_input: User's text query
    - user_id: Unique session identifier (for memory isolation)
    - top_k: Number of job results to return (retrieval parameter)

    Returns:
    - Full LangGraph result (including messages and metadata)
    """

    # -----------------------------------------------------
    # Runtime Configuration Injection
    # -----------------------------------------------------
    # `thread_id` → ensures conversation memory is separated per user
    # `top_k` → controls retrieval size inside RAG tool
    config = {
        "configurable": {
            "thread_id": user_id,
            "top_k": top_k
        }
    }

    # -----------------------------------------------------
    # Invoke LangGraph
    # -----------------------------------------------------
    # Wrap user input inside HumanMessage
    # Required message format for LangGraph state
    result = graph.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=config
    )

    # Return complete execution result
    return result