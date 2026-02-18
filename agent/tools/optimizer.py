import os
from .base import Tool

class OptimizerTool(Tool):
    def __init__(self, agent_core_path):
        self.agent_core_path = agent_core_path
        super().__init__(
            name="self_optimize",
            description="Optimize the agent's own core logic or prompts based on performance analysis.",
            parameters={
                "target": "The component to optimize (e.g., 'system_prompt', 'reasoning_logic')",
                "new_content": "The optimized content or code to apply"
            }
        )

    def execute(self, target, new_content):
        try:
            with open(self.agent_core_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            if target == "system_prompt":
                # Use regex to find and replace the SYSTEM_PROMPT variable content
                import re
                pattern = r'(SYSTEM_PROMPT = """)(.*?)(""")'
                if re.search(pattern, content, re.DOTALL):
                    new_content_full = re.sub(pattern, f'SYSTEM_PROMPT = """{new_content}"""', content, flags=re.DOTALL)
                    with open(self.agent_core_path, "w", encoding="utf-8") as f:
                        f.write(new_content_full)
                    return "Successfully optimized the system prompt."
                return "Error: Could not find SYSTEM_PROMPT variable in agent_core.py"
            
            return f"Error: Optimization target '{target}' not supported yet."
        except Exception as e:
            return f"Error during self-optimization: {str(e)}"
