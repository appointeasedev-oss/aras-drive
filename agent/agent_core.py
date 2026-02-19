#!/usr/bin/env python3
"""
ARAS - Multi-Agent Orchestration Core
Optimized for Gemma 2 4B, 8GB RAM, and large codebases.
Features: Task Decomposition, Specialized Specialists, and Chunked Processing.
"""

import os
import json
import requests
import re
import time
try:
    from .tools.base import ShellTool, FileTool
    from .tools.developer import ToolCreator
    from .tools.optimizer import OptimizerTool
    from .tools.codebase import CodebaseManager
    from .agents.orchestrator import Orchestrator
    from .agents.specialists import get_explorer_agent, get_coder_agent, get_reviewer_agent
    from .memory import add_to_memory, get_memory_context, remember_fact, recall_fact
    from .minimax_auth import MiniMaxClient
except ImportError:
    from tools.base import ShellTool, FileTool
    from tools.developer import ToolCreator
    from tools.optimizer import OptimizerTool
    from tools.codebase import CodebaseManager
    from agents.orchestrator import Orchestrator
    from agents.specialists import get_explorer_agent, get_coder_agent, get_reviewer_agent
    from memory import add_to_memory, get_memory_context, remember_fact, recall_fact
    from minimax_auth import MiniMaxClient

# Config
AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE = os.path.join(AGENT_DIR, "workspace")
OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "gemma2:4b"

os.makedirs(WORKSPACE, exist_ok=True)

# Initialize Tools
shell_tool = ShellTool()
file_tool = FileTool(WORKSPACE)
tool_creator = ToolCreator(os.path.join(AGENT_DIR, "agent", "tools"))
optimizer_tool = OptimizerTool(__file__)
codebase_tool = CodebaseManager(WORKSPACE)

def spawn_sub_agent(name, task, role_description):
    """Dynamically spawns and executes a sub-agent task"""
    print(f"[ARAS] Spawning Sub-Agent: {name} for task: {task}")
    # This leverages the existing agent_loop with a specialized prompt
    specialist_prompt = f"You are {name}, a specialized sub-agent. {role_description}"
    # We use the same model as the main agent for consistency
    return agent_loop(task, model=DEFAULT_MODEL, max_steps=5, system_override=specialist_prompt)

TOOLS = {
    "shell": shell_tool,
    "file_op": file_tool,
    "create_tool": tool_creator,
    "self_optimize": optimizer_tool,
    "codebase_manage": codebase_tool,
    "spawn_sub_agent": spawn_sub_agent
}

def ai_call(prompt, model=DEFAULT_MODEL, timeout=300, retries=3):
    """Robust AI call supporting both Ollama and MiniMax"""
    if model.startswith("minimax/"):
        real_model = model.split("/")[1]
        client = MiniMaxClient()
        return client.call(prompt, model=real_model)
        
    for attempt in range(retries):
        try:
            r = requests.post(OLLAMA_URL, json={"model": model, "prompt": prompt, "stream": False}, timeout=timeout)
            if r.status_code == 200:
                return r.json().get("response", "").strip()
        except Exception:
            if attempt < retries - 1:
                time.sleep(2)
    return None

SYSTEM_PROMPT = """You are ARAS, a multi-agent system by SS Corporations.
You work by decomposing tasks and using specialized sub-agents.

Tools:
- shell(command): System commands.
- file_op(action, path, content): File management.
- codebase_manage(action, query, chunk_index): Large codebase handling.
- create_tool(name, code): Extend capabilities.
- self_optimize(target, new_content): Self-improvement.
- spawn_sub_agent(name, task, role_description): Dynamically create a specialized sub-agent for a specific task.

Format:
Thought: Reason.
Action: {"tool": "name", "parameters": {...}}
Observation: Result.
Final Answer: Final result.
"""

def agent_loop(user_msg, model=DEFAULT_MODEL, max_steps=10, system_override=None):
    """Orchestrated ReAct loop"""
    active_system_prompt = system_override if system_override else SYSTEM_PROMPT
    
    add_to_memory("user", user_msg)
    context = get_memory_context()
    
    # 1. Decompose Task
    print("[ARAS] Decomposing task...")
    orchestrator = Orchestrator(ai_call, model)
    plan = orchestrator.decompose(user_msg, context)
    print(f"[ARAS] Plan: {len(plan)} steps")

    # 2. Execute Plan
    final_results = []
    for step in plan:
        task = step.get("task", "")
        agent_type = step.get("agent", "general")
        print(f"[ARAS] Executing Step: {task} ({agent_type})")
        
        # Select Specialist Prompt
        if agent_type == "explorer":
            agent = get_explorer_agent(ai_call, model, TOOLS)
        elif agent_type == "coder":
            agent = get_coder_agent(ai_call, model, TOOLS)
        elif agent_type == "reviewer":
            agent = get_reviewer_agent(ai_call, model, TOOLS)
        else:
            agent_type = "General"
            
        current_prompt = f"{active_system_prompt}\nRole: {agent_type}\nTask: {task}\nContext: {context[-1000:]}\n"
        
        # Sub-loop for the specific step
        for s in range(5):
            response = ai_call(current_prompt, model)
            if not response: break
            
            if "Final Answer:" in response:
                result = response.split("Final Answer:")[1].strip()
                final_results.append(result)
                context += f"\nStep Result: {result}"
                break
                
            action_match = re.search(r'Action:\s*(\{.*\})', response, re.DOTALL)
            if action_match:
                try:
                    action_data = json.loads(action_match.group(1))
                    tool_name = action_data.get("tool")
                    params = action_data.get("parameters", {})
                    if tool_name in TOOLS:
                        obs = TOOLS[tool_name].execute(**params)
                        obs_str = str(obs)[:1500] # Strict context control
                        current_prompt += f"\n{response}\nObservation: {obs_str}\n"
                except:
                    current_prompt += f"\n{response}\nObservation: Error parsing action.\n"
            else:
                break

    final_summary = "\n".join(final_results)
    add_to_memory("assistant", final_summary)
    return final_summary if final_summary else "Task completed, but no summary generated."

def chat(msg, model=DEFAULT_MODEL):
    return agent_loop(msg, model)
