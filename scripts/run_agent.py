import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_core.messages import HumanMessage
from agents.graph import app


def main():
    print("Fulfillment Ops Copilot CLI initialized.")
    print("Type 'exit' or 'quit' to stop.")
    print("-" * 40)

    while True:
        try:
            user_input = input("\nUser: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                break
            if not user_input:
                continue

            initial_state = {"messages": [HumanMessage(content=user_input)]}
            
            # app.invoke blocks until the entire graph finishes (including all tool calls)
            result_state = app.invoke(initial_state)

            final_message = result_state["messages"][-1]
        
            # Ensure we only print the text string to the terminal
            if isinstance(final_message.content, str):
                print(f"\nCopilot:\n{final_message.content}")
            elif isinstance(final_message.content, list):
                # Handles cases where the model returns a block of mixed content parts
                text_content = next((item["text"] for item in final_message.content if item.get("type") == "text"), "")
                print(f"\nCopilot:\n{text_content}")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")


if __name__ == "__main__":
    main()
