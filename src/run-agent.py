

if __name__ == "__main__":
    import pprint
    from langchain_ollama import ChatOllama

    import llama_agent
    import dav
    import config

    llm = ChatOllama(model="llama3.1", temperature=0.1)

    client = dav.TaskDAVClient(
        url=config.caldav_url,
        username=config.caldav_username,
        password=config.caldav_password
    )

    llama_agent = llama_agent.ReActAgent(llm)
    llama_agent.add_tool(client.calendar_list_ids)
    llama_agent.add_tool(client.task_list_by_calendar)
    
    while True:
        user_prompt = input("Ask: ").strip()
        if user_prompt == "":
            continue
        elif user_prompt.lower() in ['quit', 'exit', 'q']:
            break
        answer = llama_agent.invoke_agent(user_prompt)
    
        pprint.pprint(llama_agent.history)
        print("----------")
        print(answer)
