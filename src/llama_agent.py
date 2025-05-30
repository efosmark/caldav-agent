import pprint
from typing import Any, Dict, Callable
import re
import ast
import inspect
import pathlib
import os

import chatml

def get_tool_signature(fn):
    signature = inspect.signature(fn)
    name = fn.__name__
    params_str = ", ".join(str(param) for param in signature.parameters.values())
    return f"{name}({params_str})"

def get_system_prompt(tool_list) -> str:
    with open(pathlib.Path(os.path.dirname(os.path.abspath(__file__)), "system_prompt.txt")) as f:
        return f.read().format(tool_list=tool_list)

class ReActAgent:
    tools: Dict[str, Callable[..., str]]
    
    def __init__(self, model):
        self.model = model
        self.tools = {}
        self.history = []
    
    def add_tool(self, tool:Callable[..., Any]):
        self.tools[tool.__name__] = tool
    
    def get_tool_list(self):
        return '\n'.join([f'- {get_tool_signature(v)}' for v in self.tools.values()])
    
    def add_history(self, role, text):
        pprint.pprint((role, text))
        self.history.append((role, text))
    
    def invoke_agent(self, user_prompt):
        self.add_history('user', user_prompt)
        
        tool_list = self.get_tool_list()
        system_prompt = get_system_prompt(tool_list)
        print(system_prompt)
        
        while True:
            response = self.model.invoke(chatml.chatml_prompt(system_prompt, self.history, user_prompt))
            user_prompt = ""
            text = str(response.content).strip()
            self.add_history('assistant', text)
            
            if "Final Answer:" in text:
                return text.split("Final Answer:")[-1].strip()

            action_match = re.search(r"Tool:\s*(.+)", text)
            input_match = re.search(r"Tool Input:\s*(.+)", text)

            if not action_match or not input_match:
                # Still thinking...
                continue

            action_name = action_match.group(1).strip()
            action_input_raw = input_match.group(1).strip()

            try:
                action_input = ast.literal_eval(action_input_raw)
            except Exception as e:
                print(f"Failed to parse input: {e.args}")
                raise e

            try:
                observation = self.tools[action_name](**action_input)
                print(f"{action_name}(**{action_input}) = {observation}")
            except Exception as e:
                #raise e
                observation = f"ERROR: {' '.join(e.args)}"
            self.add_history('assistant', f"Tool Output: {observation}")
