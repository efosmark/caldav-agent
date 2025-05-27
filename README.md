# Let's Explore Agentic AI

## Objective

- To build an agentic AI chat bot for managing tasks and calendar events.

## Setup

1. Set up a virtual environment

    ```shell
    python -m venv .venv
    ```

2. Install requirements

    ```shell
    ./venv/bin/pip -r requirements.txt
    ```

3. Set up a config file

    ```shell
    cp src/config.py.example src/config.py
    ```

    And edit it for your CalDAV settings.

## Model Selection

If running locally, be sure to install [Ollama](https://ollama.com/). I find that `llama3.1` works well with tool-calling. It can be installed with `ollama pull llama3.1`.

If using a different model, choose the proper library from `langchain`: <https://python.langchain.com/docs/integrations/chat/>

### Example (OpenAI)

1. Configure your OpenAI API key

    <https://platform.openai.com/settings/organization/api-keys>

2. Install the necesary module

    ```shell
    ./venv/bin/pip install langchain-openai
    ```

3. Set your model in `config.py`. For example, to use GPT-4, set `ai_model='openai:gpt-4.1'`.

4. Run it with your API key in the environment variable

    LangChain expects the API key to be set in `OPENAI_API_KEY`, so run it like:

    ```shell
    OPENAI_API_KEY=your-api-key-here ./.venv/bin/python src/conversation.py
    ```
