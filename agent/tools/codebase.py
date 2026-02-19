import os
from .base import Tool

class CodebaseManager(Tool):
    """
    Handles large codebases by chunking files and searching efficiently.
    Optimized for 8GB RAM environments.
    """
    def __init__(self, workspace):
        self.workspace = workspace
        super().__init__(
            name="codebase_manage",
            description="Efficiently manage large codebases: search, chunked_read, or summary.",
            parameters={
                "action": "search, chunked_read, summary",
                "query": "Search term or file path",
                "chunk_index": "Index for chunked_read (optional)"
            }
        )

    def execute(self, action, query, chunk_index=0):
        try:
            if action == "search":
                # Use grep for fast searching without loading files into RAM
                import subprocess
                cmd = f"grep -rnw '{self.workspace}' -e '{query}' --exclude-dir=.git"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                return result.stdout if result.stdout else "No matches found."

            elif action == "chunked_read":
                path = os.path.join(self.workspace, query)
                if not os.path.exists(path):
                    return f"Error: File {query} not found."
                
                chunk_size = 2000 # Small chunks for small models
                with open(path, 'r', encoding='utf-8') as f:
                    f.seek(chunk_index * chunk_size)
                    content = f.read(chunk_size)
                
                has_more = len(content) == chunk_size
                return {
                    "content": content,
                    "chunk": chunk_index,
                    "has_more": has_more,
                    "next_index": chunk_index + 1 if has_more else None
                }

            elif action == "summary":
                # Provide a high-level tree view
                import subprocess
                cmd = f"find '{self.workspace}' -maxdepth 2 -not -path '*/.*'"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                return result.stdout

        except Exception as e:
            return f"Error in codebase_manage: {str(e)}"
