from langchain_ollama import OllamaEmbeddings, ChatOllama

llm = ChatOllama(
    model="llama3",
    temperature=0.1,
)

embeddings = OllamaEmbeddings(
    model="llama3",
)

tasks = [
    "Task: Work on Attribution Reporting API integration",
    "Task: Complete the integrations with UET in pixie-ui",
    "Task: Update the library_dmp-ui component to accept MAX_REACH in modeled segments",
    "Task: Clean off my computer desk",
    "Task: Move the workbench back to the other corner of the living room",
    "Task: Box up unused equipment around the house",
    "Task: Move boxed up equipment to self-storage",
    "Task: Check on tax rebates",
    "Task: Check on payment status for municipal taxes",
    "Task: Verify the shared bank account has been closed and ex-wife was removed from it entirely",
    "Task: Install the new wireless router",
    "Task: Read the estimate from Heartfelt Vets on dental work for the cats",
    "Task: Buy new air filters for the air purifier",
    "Task: Install new windshield wipers"
]
#embeddings.embed_documents(tasks)

# Tool to fetch task lists
# Embedding refresh

messages = [
    (
        "system",
        "You are a tool that helps organize todo lists and task lists. Do not offer additional suggestions. Do not provide introductory descriptions or summaries.",
    ),
    *(("human", t) for t in tasks),
    ("human", "Prioritize my tasks based on inferred importance. Give each task a value between 0 and 9, where 0 is lowest, and 9 is highest. "),
]

ai_msg = llm.invoke(messages)
print(ai_msg.content)




# # Create a vector store with a sample text
# from langchain_core.vectorstores import InMemoryVectorStore

# vectorstore = InMemoryVectorStore.from_texts(
#     tasks,
#     embedding=embeddings,
# )

# # Use the vectorstore as a retriever
# retriever = vectorstore.as_retriever()

# retriever = 

# # Retrieve the most similar text
# retrieved_documents = retriever.invoke("Give me the top three categories that my tasks fall under.")

# # show the retrieved document's content
# print(retrieved_documents[0].page_content)