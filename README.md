# ARAS-Drive 🐦 (Enhanced Edition)

## What is ARAS-Drive?

ARAS-Drive is a portable, high-performance AI agent system designed to run locally on small models (3B-7B) while delivering capabilities that rival much larger systems. It is now powered by an advanced **ReAct (Reasoning + Acting) loop**, allowing it to think, plan, execute tools, and self-correct.

## 🚀 Key Enhancements

- **Multi-Agent Orchestration**: Complex tasks are automatically decomposed into small steps executed by specialized sub-agents (Explorer, Coder, Reviewer).
- **8GB RAM Optimization**: Uses chunked file reading and grep-based searching to handle massive codebases without memory pressure.
- **Dynamic Tool System**:
  - `codebase_manage`: Specialized tool for searching and reading large projects in chunks.
  - `shell`: Full system command execution.
  - `file_op`: Advanced file manipulation.
  - `create_tool`: Self-extension capability to write new Python tools.
  - `self_optimize`: Autonomous self-improvement of internal prompts and logic.
- **Optimized for Gemma 2 4B**: Specifically tuned for ultra-small local models, ensuring high intelligence with low power.
- **Self-Evolution**: ARAS can reflect on its performance and autonomously optimize its own core logic.

## 📁 Repository Structure

| Directory | Purpose |
|-----------|---------|
| `agent/` | Core agent logic and ReAct implementation |
| `agent/tools/` | Modular tool definitions |
| `memory/` | Persistent SQLite and JSON memory storage |
| `workspace/` | The agent's active working area |

## 🛠️ Getting Started

### 1. Prerequisites
- [Ollama](https://ollama.com/) installed and running.
- Recommended model: `ollama pull qwen2.5-coder:3b` (or `7b`).

### 2. Run Locally
```bash
python agent/local_chat.py
```

### 3. Run via Telegram
Configure your `TOKEN` and `USER_ID` in `start.bat` or run:
```bash
python agent/telegram_agent.py <TOKEN> <USER_ID> <MODEL_NAME>
```

## 🧠 How to use the Agent

ARAS is now a true autonomous agent. You can give it complex tasks like:
- "Create a web scraper for news and save the results to a CSV."
- "Analyze the files in my workspace and suggest improvements."
- "Write a python script, test it, and if it fails, fix the bugs."

ARAS will **Think**, take an **Action**, observe the **Result**, and iterate until the task is complete.

---
*Developed by SS Corporations - Making local AI smarter.*
