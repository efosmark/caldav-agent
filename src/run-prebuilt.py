"""Exploring a simple conversation loop with a task management agent.

This script sets up a basic conversation loop where a user can interact with an
AI agent designed to manage tasks using a calendar service.
"""
import pprint
from typing import Any, cast
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain.chat_models import init_chat_model

# Local project imports
import dav
import config

from langchain_core.tools import tool, BaseTool
from dav import TaskDAVClient

def get_taskdav_tools(client: 'TaskDAVClient') -> list[BaseTool]:
    """Return all LangChain tools for the given TaskDAVClient instance."""
    return [
        tool(client.task_get_by_id, parse_docstring=True),
        tool(client.task_list_by_calendar, parse_docstring=True),
        tool(client.task_list_overdue, parse_docstring=True),
        tool(client.calendar_list_ids, parse_docstring=True),
        tool(client.task_add_to_calendar, parse_docstring=True),
        tool(client.task_mark_complete, parse_docstring=True),
        tool(client.task_mark_incomplete, parse_docstring=True),
        tool(client.task_update_summary, parse_docstring=True),
        tool(client.task_update_priority, parse_docstring=True),
        tool(client.task_update_due_date, parse_docstring=True),
        tool(client.task_update_description, parse_docstring=True),
        tool(client.task_update_start_date, parse_docstring=True),
        tool(client.task_update_end_date, parse_docstring=True),
    ]



def build_full_prompt(client: dav.TaskDAVClient, user_prompt:str):
    system_prompt:list[str] = [
        "You are a terse agent for managing tasks.",
        "Respond with only the direct output.",
        "Do not include follow-ups, explanations, or conversational tone.",
        "No questions or suggestions unless explicitly asked for.",
        "Do not use markdown formatting.",
        f"Available calendar IDs are: {', '.join(client.calendar_list_ids())}"
    ]
    return {
        "messages": [
            ("system", " ".join(system_prompt)),
            ("human", user_prompt),
        ],
    }

def build_agent(client: dav.TaskDAVClient):
    return create_react_agent(
        model=init_chat_model(config.ai_model),
        tools=get_taskdav_tools(client),
        checkpointer=MemorySaver(),
    )

def handle_response(content):
    """Handle the response from the agent."""
    if content is None:
        print("No response from agent.")
    elif content == "":
        print("Agent did not provide a response.")
    elif isinstance(content, list):
        print("\n".join(content))
    elif isinstance(content, dict):
        #pprint.pprint(content, indent=2)
        try:
            if "messages" in content and isinstance(content["messages"], list):
                print(content["messages"][-1].content)
        except KeyError:
            print("Could not extract messages from content.")
    else:
        print(str(content))

def run_conversation_loop(client: dav.TaskDAVClient):
    """ Run a simple conversation loop with the agent."""
    agent = build_agent(client)
    
    print("Type 'exit' or 'quit' to stop the conversation.")
    while True:
        
        print("-" * 80)
        user_prompt = input("You: ").strip()
        print()
        if user_prompt.lower() in ["exit", "quit"]:
            break
        elif user_prompt == "":
            continue
        
        response = agent.invoke(build_full_prompt(client, user_prompt), {"configurable": {"thread_id": "123456"}})
        if "messages" in response:
            handle_response(response)
            continue
        
        response = cast(Any, response)
        if hasattr(response, "error") and response.error:
            print(f"Error: {response.error}")
            continue
        elif hasattr(response, "content") and response.content is not None and response.content != "":
            handle_response(response.content)
            continue
        print("Unknown response")
        pprint.pprint(response)


if __name__ == "__main__":
    client = dav.TaskDAVClient(
        url=config.caldav_url,
        username=config.caldav_username,
        password=config.caldav_password
    )

    run_conversation_loop(client)
