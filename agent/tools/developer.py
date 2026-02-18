import os
from .base import Tool

class ToolCreator(Tool):
    def __init__(self, tools_dir):
        self.tools_dir = tools_dir
        super().__init__(
            name="create_tool",
            description="Create a new tool for the agent to use",
            parameters={
                "name": "Name of the tool file (e.g. web_search.py)",
                "code": "Full Python code for the tool class"
            }
        )

    def execute(self, name, code):
        try:
            path = os.path.join(self.tools_dir, name)
            with open(path, "w", encoding="utf-8") as f:
                f.write(code)
            return f"Successfully created tool at {name}. The agent will need to be restarted to load it, or you can use it in the next session."
        except Exception as e:
            return f"Error creating tool: {str(e)}"
