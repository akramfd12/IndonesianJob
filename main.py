# from agents.chatbot_agent import *

# conversation_history = []

# while True:
#     user_input = input("\nUser: ").strip()

#     if not user_input:
#         continue

#     if user_input.lower() in ["exit", "quit", "keluar"]:
#         print("Bye 👋")
#         break

#     # Tambahkan input user ke history
#     conversation_history.append(
#         {"role": "user", "content": user_input}
#     )

#     result = agent.invoke(
#         {
#             "messages": conversation_history
#         },
#         context={"user_role": "expert"}
#     )

#     # Ambil jawaban terakhir agent
#     agent_reply = result["messages"][-1].content

#     print("\nAgent:", agent_reply)

#     # Simpan jawaban agent ke history
#     conversation_history.append(
#         {"role": "assistant", "content": agent_reply}
#     )

from fastapi import FastAPI
from pydantic import BaseModel
from agents.chatbot_agent import run_agent
import os

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def health_check():
    return{"status": "Running"}

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    results= run_agent(request.message)
    return {"response": results}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

