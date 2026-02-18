# ARAS AI Agent Enhancement Strategy

## Current Limitations
- **Basic Tooling**: Only supports simple file read/write and listing.
- **Rigid Workflow**: Hardcoded paths for "website" and "python" project creation.
- **Weak Reasoning**: Single-pass or simple 3-step reasoning without self-correction.
- **Limited Interaction**: Only supports text-based chat and basic file operations.
- **No Self-Improvement**: The agent doesn't learn from its own mistakes or create new tools.
- **Context Management**: Memory is simple and doesn't handle large contexts well for small models.

## Enhancement Goals
1.  **Dynamic Tool System**: Implement a modular tool system where the agent can call specialized functions (shell execution, web search, advanced file manipulation).
2.  **Advanced Reasoning (ReAct)**: Implement a Reasoning + Acting loop to allow the agent to think, act, observe, and refine.
3.  **Self-Correction**: Add a verification step where the agent checks its own code or output for errors before finalizing.
4.  **Local Model Optimization**: 
    - Use smaller, more efficient prompts.
    - Implement prompt compression or selective context loading.
    - Leverage few-shot examples for better performance on 3B-7B models.
5.  **New Features**:
    - **Shell Access**: Allow the agent to run commands (safely or with confirmation).
    - **Project Analysis**: Better understanding of existing codebases.
    - **Dependency Management**: Automatically identify and suggest missing packages.
    - **Memory Augmentation**: RAG-lite for long-term memory retrieval.

## Implementation Plan

### 1. Core Architecture Refactor
- Create a `tools` directory for modular tools.
- Implement a `ToolManager` to handle tool registration and execution.
- Update `agent_core.py` to use a ReAct loop.

### 2. Tool Development
- `shell_tool`: Execute system commands.
- `file_tool`: Advanced file operations (grep, sed-like edits).
- `web_tool`: (Optional/Simulated) for searching if possible.

### 3. Intelligence Boost
- Implement "Chain of Thought" prompting optimized for Qwen2.5-Coder.
- Add a "Reviewer" agent persona that checks the "Coder" agent's output.

### 4. Integration
- Update `telegram_agent.py` to support new capabilities.
- Update `local_chat.py` for better developer experience.
