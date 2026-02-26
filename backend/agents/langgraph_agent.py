from typing import TypedDict, List, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig
from agents.chatbot_agent import agent


# =========================================================
# LANGGRAPH AGENT DEFINITION
# =========================================================
# This file builds the conversation workflow using LangGraph.
#
# Responsibilities:
# - Define state structure
# - Define execution node
# - Compile graph with memory checkpoint
# - Support runtime config injection (e.g., thread_id, top_k)
# =========================================================


# =========================
# 1️⃣ Define State
# =========================
# AgentState represents the graph state.
# It stores a list of conversation messages.
#
# add_messages ensures that new messages
# are appended instead of replacing previous ones.
class AgentState(TypedDict):
      messages: Annotated[List[BaseMessage], add_messages]


# =========================
# 2️⃣ Node Definition
# =========================
# agent_node is the execution unit of the graph.
#
# Parameters:
# - state: current conversation state
# - config: runtime configuration (thread_id, top_k, etc.)
#
# Important:
# We forward `config` to agent.invoke()
# so runtime parameters reach tools (e.g., search_jobs).
def agent_node(state: AgentState, config: RunnableConfig):
    result = agent.invoke(
        {
            "messages": state["messages"]
        },
        config=config   # 🔥 forward config ke agent
    )

    # Extract latest AI message from result
    ai_message = result["messages"][-1]

    # Return new state update
    return {
        "messages": [ai_message]
    }


# =========================
# 3️⃣ Build Graph
# =========================
# Create StateGraph with defined state structure
builder = StateGraph(AgentState)

# Add agent execution node
builder.add_node("agent", agent_node)

# Set entry point of workflow
builder.set_entry_point("agent")

# After agent runs → end execution
builder.add_edge("agent", END)


# =========================
# 4️⃣ Memory Checkpointer
# =========================
# MemorySaver stores conversation history
# per thread_id (runtime configurable).
#
# This enables:
# - Multi-user support
# - Persistent chat sessions
memory = MemorySaver()


# =========================
# 5️⃣ Compile Graph
# =========================
# Compile graph with memory support.
# The resulting `graph` is invoked in run_agent().
graph = builder.compile(checkpointer=memory)