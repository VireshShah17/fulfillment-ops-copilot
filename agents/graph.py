import os
from dotenv import load_dotenv
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from agents.tools import search_knowledge_base, get_order_status, get_inventory_levels, get_shipment_tracking


load_dotenv()


# State Definition
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# Tools and LLM Initialization
tools = [
    search_knowledge_base,
    get_order_status,
    get_inventory_levels,
    get_shipment_tracking
]
llm = ChatGoogleGenerativeAI(model = os.environ.get("GEMINI_MODEL"))
llm_with_tools = llm.bind_tools(tools)


# Nodes
def agent_node(state: AgentState):
    system_msg = SystemMessage(
        content = "You are a warehouse ops copilot. Never guess statuses. Always use tools."
    )
    
    # Combine the system instruction with the active conversation history
    messages_to_process = [system_msg] + state["messages"]
    
    response = llm_with_tools.invoke(messages_to_process)
    return {"messages": [response]}


tool_node = ToolNode(tools)


# Routing logic
def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "action"

    return "end"


# Graph compilation
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("action", tool_node)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "action": "action",
        "end": END
    }
)
workflow.add_edge("action", "agent")

app = workflow.compile()
