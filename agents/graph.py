import os
from dotenv import load_dotenv
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from agents.tools import search_knowledge_base, get_order_status, get_inventory_levels, get_shipment_tracking


load_dotenv()

SYS_PROMPT = """
    You are a Fulfillment Operations Copilot.
    Your role is to assist warehouse staff with order statuses, inventory levels, and shipment tracking.
    Always use the provided tools to fetch real data. Never guess, assume, or hallucinate information.
    If an order is delayed, check the knowledge base for the appropriate policy.
"""


# State Definition
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# Nodes
def agent_node(state: AgentState):
    system_msg = SystemMessage(
        content = SYS_PROMPT
    )
    messages_to_process = [system_msg] + list(state["messages"])
    response = llm_with_tools.invoke(messages_to_process)
    
    return {"messages": [response]}


# Routing logic
def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "action"

    return "end"


def guardrail_node(state: AgentState):
    # This node acts as a pass-through entry point. 
    # The actual evaluation happens in the conditional edge below.
    return state


def refusal_node(state: AgentState):
    return {
        "messages": [AIMessage(content = "I can only assist with warehouse fulfillment operations.")]
    }


def check_guardrail(state: AgentState) -> str:
    last_message = state["messages"][-1].content.lower()
    
    # Lightweight keyword check for ops context
    ops_keywords = [
        "order", "ord", "status", "sku", "inventory", "shipment", 
        "tracking", "warehouse", "delay", "stock", "policy", "carrier"
    ]
    
    if any(word in last_message for word in ops_keywords):
        return "valid"
    
    return "invalid"


# Tools and LLM Initialization
tools = [
    search_knowledge_base,
    get_order_status,
    get_inventory_levels,
    get_shipment_tracking
]
llm = ChatGoogleGenerativeAI(model = os.environ.get("GEMINI_MODEL"))
llm_with_tools = llm.bind_tools(tools)

tool_node = ToolNode(tools)

# Graph compilation
workflow = StateGraph(AgentState)
# 1. Add all nodes
workflow.add_node("guardrail", guardrail_node)
workflow.add_node("refusal", refusal_node)
workflow.add_node("agent", agent_node)
workflow.add_node("action", tool_node)
# 2. Execution flow
workflow.add_edge(START, "guardrail")
# 3. Guardrail conditional routing
workflow.add_conditional_edges(
    "guardrail",
    check_guardrail,
    {
        "valid": "agent",
        "invalid": "refusal"
    }
)
# 4. Standard ReAct loop
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "action": "action",
        "end": END
    }
)
workflow.add_edge("action", "agent")
workflow.add_edge("refusal", END)

app = workflow.compile()
