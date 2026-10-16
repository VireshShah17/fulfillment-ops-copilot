import sys
import os
import logging

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_core.messages import HumanMessage
from agents.graph import app

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger("AgentRunner")


def main():
    logger.info("Fulfillment Ops Copilot CLI initialized.")
    logger.info("Type 'exit' or 'quit' to stop.")
    logger.info("-" * 40)

    while True:
        try:
            user_input = input("\nUser: ").strip()

            if user_input.lower() in ['exit', 'quit']:
                break

            if not user_input:
                continue

            initial_state = {"messages": [HumanMessage(content=user_input)]}
            logger.info("\nThinking...")
            result_state = app.invoke(initial_state)
            final_message = result_state["messages"][-1]
            
            # Extract content
            if isinstance(final_message.content, str):
                text_content = final_message.content
            elif isinstance(final_message.content, list):
                text_content = next((item["text"] for item in final_message.content if item.get("type") == "text"), "")
            else:
                text_content = str(final_message.content)
                
            logger.info(f"\nCopilot:\n{text_content}")

            # Extract usage metadata
            usage = getattr(final_message, "usage_metadata", None)

            if usage:
                in_tokens = usage.get("input_tokens", 0)
                out_tokens = usage.get("output_tokens", 0)
                logger.info(f"\n[Tokens Used: In={in_tokens}, Out={out_tokens}]")

        except KeyboardInterrupt:
            logger.exception("\nExiting...")
            break
        except Exception as e:
            logger.exception(f"\nAn error occurred: {e}")


if __name__ == "__main__":
    main()
