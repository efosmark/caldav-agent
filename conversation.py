"""Exploring a simple conversation loop with a task management agent.

This script sets up a basic conversation loop where a user can interact with an AI agent designed to manage tasks using a calendar service.
"""
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain.chat_models import init_chat_model

# Local project imports
import dav
import tools
import config

client = dav.TaskDAVClient(
    url=config.caldav_url,
    username=config.caldav_username,
    password=config.caldav_password
)

system_prompt:list[str] = [
    "You are a terse agent for managing tasks.",
    "Respond with only the direct output.",
    "Do not include follow-ups, explanations, or conversational tone.",
    "No questions or suggestions unless explicitly asked for.",
    "Do not use markdown formatting.",
    f"Available calendar IDs are: {', '.join(client.calendar_list_ids())}"
]

def build_full_prompt(user_prompt:str):
    return {
        "messages": [
            ("system", " ".join(system_prompt)),
            ("human", user_prompt),
        ],
    }, {"configurable": {"thread_id": "123456"}}

def build_agent():
    llm = init_chat_model(config.ai_model)
    agent = create_react_agent(
        llm=llm,
        tools=tools.get_tools(),
        build_prompt=build_full_prompt,
        memory_saver=MemorySaver(),
    )
    return agent

def run_conversation_loop():
    agent = build_agent()
    while True:
        user_prompt = input("You: ").strip()
        if user_prompt.lower() in ["exit", "quit"]:
            break
        if user_prompt == "":
            continue
        
        response = agent.invoke(build_full_prompt(user_prompt))
        if response.error:
            print(f"Error: {response.error}")
            continue
        elif response.content is None:
            print("No response from agent.")
            continue
        elif response.content == "":
            print("Agent did not provide a response.")
            continue
        elif isinstance(response.content, list):
            response.content = "\n".join(response.content)
        elif isinstance(response.content, dict):
            response.content = str(response.content)

        print(f"Agent: {response.content}")


if __name__ == "__main__":
    run_conversation_loop()



