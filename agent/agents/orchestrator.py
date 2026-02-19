import json
import re

class Orchestrator:
    """
    The brain of ARAS. Decomposes complex tasks into smaller, 
    manageable sub-tasks for specialized agents.
    """
    def __init__(self, ai_call_func, model):
        self.ai_call = ai_call_func
        self.model = model

    def decompose(self, user_goal, context):
        prompt = f"""You are the ARAS Orchestrator. 
Your goal is to take a complex request and break it into a sequence of small, efficient steps.
Each step should be simple enough for a small 4B model to execute perfectly.

User Goal: {user_goal}
Current Context Summary: {context[:500]}

Respond ONLY with a JSON list of steps. 
Example: [{{"step": 1, "task": "Scan directory structure", "agent": "explorer"}}, {{"step": 2, "task": "Read core logic", "agent": "coder"}}]

JSON Plan:"""
        response = self.ai_call(prompt, self.model)
        try:
            # Extract JSON from response
            match = re.search(r'(\[.*\])', response, re.DOTALL)
            if match:
                return json.loads(match.group(1))
        except:
            pass
        
        # Fallback to a single step if decomposition fails
        return [{"step": 1, "task": user_goal, "agent": "general"}]

class SubAgent:
    """Base class for specialized sub-agents"""
    def __init__(self, name, system_prompt, ai_call_func, model, tools):
        self.name = name
        self.system_prompt = system_prompt
        self.ai_call = ai_call_func
        self.model = model
        self.tools = tools

    def execute(self, task, context):
        prompt = f"{self.system_prompt}\n\nContext:\n{context}\n\nCurrent Task: {task}\n"
        # The actual execution logic remains similar to the ReAct loop but focused on the specific sub-task
        return prompt # Return the prepared prompt for the core loop
