import pytest
from langchain_core.messages import HumanMessage, AIMessage
from agents.graph import check_guardrail, should_continue


def test_guardrail_valid():
    # Provide a mock AgentState containing the keyword "order"
    state = {"messages": [HumanMessage(content = "Can you check the status of my order?")]}
    result = check_guardrail(state)

    assert result == "valid", f"Expected 'valid', but got '{result}'"


def test_guardrail_invalid():
    # Provide a mock AgentState with no ops-related keywords
    state = {"messages": [HumanMessage(content = "Write a poem about the ocean.")]}
    result = check_guardrail(state)

    assert result == "invalid", f"Expected 'invalid', but got '{result}'"


def test_should_continue_with_tool():
    # Provide a mock AgentState where the last message contains tool_calls
    mock_tool_call = {
        "name": "get_order_status",
        "args": {"order_id": "ORD-1234"},
        "id": "mock_call_id"
    }
    
    message_with_tool = AIMessage(
        content = "", 
        tool_calls = [mock_tool_call]
    )
    
    state = {"messages": [message_with_tool]}
    result = should_continue(state)

    assert result == "action", f"Expected 'action', but got '{result}'"
