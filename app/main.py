import sys
import os

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from agents.graph import app as graph_app


app = FastAPI(title = "Fulfillment Ops Co-pilot API")


class ChatRequest(BaseModel):
    query: str


@app.post('/chat')
async def chat(request: ChatRequest):
    try:
        # Format input for langgraph
        initial_state = {
            "messages": [HumanMessage(content = request.query)]
        }
        # Execute the workflow
        result_state = graph_app.invoke(initial_state)
        final_message = result_state['messages'][-1]

        # Extract the text content
        if isinstance(final_message.content, str):
            text_content = final_message.content
        elif isinstance(final_message.content, list):
            text_content = next((item["text"] for item in final_message.content if item.get("type") == "text"), "")
        else:
            text_content = str(final_message.content)

        return {"response": text_content}
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))
