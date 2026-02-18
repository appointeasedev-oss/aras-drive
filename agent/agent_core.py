#!/usr/bin/env python3
"""
ARAS - Advanced AI Agent Core
Enhanced with ReAct reasoning, modular tools, and self-correction.
Optimized for small local models like Qwen2.5-Coder.
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
    from .memory import add_to_memory, get_memory_context, remember_fact, recall_fact
except ImportError:
    from tools.base import ShellTool, FileTool
    from tools.developer import ToolCreator
    from tools.optimizer import OptimizerTool
    from memory import add_to_memory, get_memory_context, remember_fact, recall_fact

# Config
AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE = os.path.join(AGENT_DIR, "workspace")
OLLAMA_URL = "http://localhost:11434/api/generate"

os.makedirs(WORKSPACE, exist_ok=True)

# Initialize Tools
shell_tool = ShellTool()
file_tool = FileTool(WORKSPACE)
tool_creator = ToolCreator(os.path.join(AGENT_DIR, "agent", "tools"))
optimizer_tool = OptimizerTool(__file__)

TOOLS = {
    "shell": shell_tool,
    "file_op": file_tool,
    "create_tool": tool_creator,
    "self_optimize": optimizer_tool
}

def ai_call(prompt, model="qwen2.5-coder:3b", timeout=120):
    """Make AI call to Ollama"""
    try:
        r = requests.post(OLLAMA_URL, json={"model": model, "prompt": prompt, "stream": False}, timeout=timeout)
        if r.status_code == 200:
            return r.json().get("response", "").strip()
    except Exception as e:
        print(f"[AI Error] {e}")
    return None

def extract_json(text):
    """Extract JSON from AI response"""
    try:
        # Look for JSON block
        match = re.search(r'```json\n(.*?)\n```', text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        # Try raw JSON if no block
        match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    except:
        pass
    return None

SYSTEM_PROMPT = """You are ARAS, a self-evolving AI Agent by SS Corporations.
You are optimized for small local models and excel at complex reasoning.

Available Tools:
- shell(command): Run terminal commands. Use for code execution, environment setup, and system exploration.
- file_op(action, path, content=None): File manager. Actions: 'read', 'write', 'list', 'delete'. Use relative paths.
- create_tool(name, code): Create a new Python tool to extend your capabilities.
- self_optimize(target, new_content): Update your own system prompt or core logic. Target: 'system_prompt'.

Response Format:
Thought: Plan your next move.
Action: {"tool": "tool_name", "parameters": {...}}
Observation: (System output)

Final Answer: Clear, detailed solution.

Principles:
1. **Minimalist Reasoning**: For small models, be concise but logical.
2. **Self-Correction**: If a tool fails, explain why and try a new way.
3. **Autonomy**: Solve tasks completely. Install missing dependencies using `shell`.
4. **Self-Evolution**: Use `create_tool` and `self_optimize` to improve your own efficiency.
"""

def agent_loop(user_msg, model, max_steps=10):
    """The main ReAct loop for the agent"""
    add_to_memory("user", user_msg)
    context = get_memory_context()
    
    # Dynamic context window for small models
    if len(context) > 1500:
        context = context[-1500:]
        
    current_prompt = f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nUser: {user_msg}\n"
    
    for step in range(max_steps):
        print(f"[ARAS] Step {step+1}/{max_steps}")
        
        response = ai_call(current_prompt, model)
        if not response:
            return "Error: Could not reach AI model."
        
        print(f"[AI] {response[:100]}...")
        
        if "Final Answer:" in response:
            final_answer = response.split("Final Answer:")[1].strip()
            add_to_memory("assistant", final_answer)
            return final_answer
        
        # Try to extract action
        action_match = re.search(r'Action:\s*(\{.*\})', response, re.DOTALL)
        if action_match:
            try:
                action_data = json.loads(action_match.group(1))
                tool_name = action_data.get("tool")
                params = action_data.get("parameters", {})
                
                if tool_name in TOOLS:
                    print(f"[TOOL] Executing {tool_name} with {params}")
                    observation = TOOLS[tool_name].execute(**params)
                    obs_str = json.dumps(observation) if isinstance(observation, (dict, list)) else str(observation)
                    
                    # Truncate long observations
                    if len(obs_str) > 2000:
                        obs_str = obs_str[:2000] + "...(truncated)"
                    
                    print(f"[OBS] Got {len(obs_str)} chars")
                    current_prompt += f"\n{response}\nObservation: {obs_str}\n"
                    continue
                else:
                    current_prompt += f"\n{response}\nObservation: Error: Tool {tool_name} not found.\n"
            except Exception as e:
                current_prompt += f"\n{response}\nObservation: Error parsing action: {str(e)}\n"
        else:
            # If no action and no final answer, try to nudge the AI
            current_prompt += f"\n{response}\nObservation: Please provide an Action or a Final Answer.\n"

    return "I reached the maximum number of steps without finding a final answer. Please try to be more specific."

def chat(msg, model="qwen2.5-coder:3b"):
    """Compatibility wrapper for the agent loop"""
    # Simple check for direct commands to bypass the loop if needed
    msg_lower = msg.lower().strip()
    
    # Example of a fast path for simple queries
    if msg_lower in ["ls", "list workspace", "files"]:
        files = os.listdir(WORKSPACE)
        return f"📁 Workspace Files:\n" + "\n".join([f"- {f}" for f in files]) if files else "Workspace is empty."

    return agent_loop(msg, model)
