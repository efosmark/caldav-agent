from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain.chat_models import init_chat_model

from datetime import datetime
import dav, tools
import config

if __name__ == "__main__":
    import time

    client = dav.TaskDAVClient(
        url=config.url,
        username=config.username,
        password=config.password
    )

    memory = MemorySaver()
    model = init_chat_model("llama3.1", model_provider="ollama", temperature=0)
    agent = create_react_agent(
        model=model,
        tools=tools.get_taskdav_tools(client),
        checkpointer=memory
    )
    
    
    prompt:list[str] = [
        "You are a terse agent for managing tasks.",
        "Respond with only the direct output.",
        "Do not include follow-ups, explanations, or conversational tone.",
        "No questions or suggestions unless explicitly asked for.",
        "Do not use markdown formatting.",
        f"Available calendar IDs are: {', '.join(client.calendar_list_ids())}"
    ]

    for step in agent.stream({
        "messages": [
            ("system", " ".join(prompt)),
            ("human", "Bump up the priority on the CORS explainer work task."),
        ],
    }, {"configurable": {"thread_id": "abc123"}}, stream_mode="values"):
        step["messages"][-1].pretty_print()

    # start_time = None
    # end_time = None
    # while True:
    #     print("-" * 80)
    #     if start_time is not None and end_time is not None:
    #         print(f"({int(end_time - start_time)}s) ", end="")
    #     val = input("::>")
    #     if val.strip() == "":
    #         continue
    #     start_time = time.time()
    #     result = agent_executor.invoke({
    #         "input": val,
    #         "date": datetime.now(),
    #         "client_url": config.url
    #     })
    #     end_time = time.time()
    #     print("-" * 80)
    #     print(result)
