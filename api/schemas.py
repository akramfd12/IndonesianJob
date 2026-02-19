# Import library dependencies
from pydantic import BaseModel
from typing import List, Optional

# Create BaseModel 
# Input Class (Request)
# 1. User chat input (Raw string)
class ChatRequest(BaseModel):
    """
    Request: User input in chat format.
    """
    user_input: str
    top_k: int = 5


# # 2. Parsed query from user input (SQL + RAG)
# class JobQueryRequest(BaseModel):
#     """
#     Request: Input to SQL + RAG from parsed user input -> Executed by Agent
#     Input for JobResultResponses
#     """
#     job_title: Optional[str]
#     company_name: Optional[str]
#     location: Optional[str]
#     work_type: Optional[str]
#     job_description: Optional[str]
#     salary_min: Optional[int]
#     salary_max: Optional[int]

# Output Class (Response)
# 1. Job searched result from Input query (SQL + RAG)
class JobResultResponse(BaseModel):
    """
    Response: Job searched from DB (SQL + RAG) by Agent instruction
    Input for ChatResponses
    """
    job_title: str
    company_name: str
    location: str
    work_type: str
    job_description: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    relevance_score: Optional[float] = None

# 2. Final response from chatbot agent (AI Message from invoke responses)
class ChatResponse(BaseModel):
    """
    Response: Final response from chatbot agent (AI Message from invoke responses)
    """
    response: str
    source: List[JobResultResponse] = []
    