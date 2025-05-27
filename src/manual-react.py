"""
A scratchpad for manually implementing a ReAct agent using LangChain and Ollama.
"""

from typing import Dict, Callable, cast
from langchain_ollama import ChatOllama
from langchain.tools import StructuredTool
import re

# 1. Define a real tool
def multiply(x: int, y: int) -> str:
    """Multiply two integers and return the result as a string."""
    return str(x * y)

tools: Dict[str, Callable[[str], str]] = {
    "Multiplier": StructuredTool.from_function(multiply)
}

# 2. Set up ChatOllama (or any chat model)
llm = ChatOllama(model="llama3")

# 3. Manual agent loop
def manual_react_agent(question: str) -> str:
    history = []

    while True:
        # Build the prompt
        prompt = (
            "You are a helpful agent. Use the following format:\n"
            "Thought: <your thoughts>\n"
            "Action: <tool name>\n"
            "Action Input: <input for the tool>\n"
            "Observation: <result from the tool>\n"
            "... (you can repeat Thought/Action/Observation) ...\n"
            "Final Answer: <your final answer>\n\n"
        )

        # Add history
        for h in history:
            prompt += h + "\n"

        prompt += f"Question: {question}\n"

        # Ask the model
        response = llm.invoke(cast(str, prompt))
        
        #print("Response:", response)
        text = str(response.content).strip()
        history.append(text)

        # Parse model output
        if "Final Answer:" in text:
            return text.split("Final Answer:")[-1].strip()

        action_match = re.search(r"Action:\s*(.+)", text)
        input_match = re.search(r"Action Input:\s*(.+)", text)

        if not action_match or not input_match:
            raise ValueError("Could not parse Action and Action Input.")

        action_name = action_match.group(1).strip()
        action_input = input_match.group(1).strip()

        # Run the tool manually
        if action_name not in tools:
            raise ValueError(f"Unknown tool: {action_name}")

        tool = tools[action_name]
        observation = tool.invoke(action_input) # type: ignore

        history.append(f"Observation: {observation}")

# 4. Run the agent
if __name__ == "__main__":
    answer = manual_react_agent("What is 8543.22 times 7?")
    print(f"Answer: {answer}")
