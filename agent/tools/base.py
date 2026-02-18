import subprocess
import os
import json

class Tool:
    def __init__(self, name, description, parameters):
        self.name = name
        self.description = description
        self.parameters = parameters

    def execute(self, **kwargs):
        raise NotImplementedError

class ShellTool(Tool):
    def __init__(self):
        super().__init__(
            name="shell",
            description="Execute a shell command and return the output",
            parameters={"command": "The command to execute"}
        )

    def execute(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except Exception as e:
            return {"error": str(e)}

class FileTool(Tool):
    def __init__(self, workspace):
        self.workspace = workspace
        super().__init__(
            name="file_op",
            description="Perform file operations: read, write, list, delete",
            parameters={
                "action": "read, write, list, delete",
                "path": "Relative path to the file/directory",
                "content": "Content for write action (optional)"
            }
        )

    def execute(self, action, path, content=None):
        full_path = os.path.join(self.workspace, path)
        try:
            if action == "read":
                if os.path.exists(full_path):
                    with open(full_path, "r", encoding="utf-8") as f:
                        return f.read()
                return f"Error: File {path} not found"
            elif action == "write":
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return f"Successfully wrote to {path}"
            elif action == "list":
                if os.path.exists(full_path):
                    return os.listdir(full_path)
                return f"Error: Directory {path} not found"
            elif action == "delete":
                if os.path.exists(full_path):
                    if os.path.isdir(full_path):
                        import shutil
                        shutil.rmtree(full_path)
                    else:
                        os.remove(full_path)
                    return f"Successfully deleted {path}"
                return f"Error: {path} not found"
        except Exception as e:
            return f"Error: {str(e)}"
