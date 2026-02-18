# ARAS-Drive 🐦 (Enhanced Edition)

## What is ARAS-Drive?

ARAS-Drive is a portable, high-performance AI agent system designed to run locally on small models (3B-7B) while delivering capabilities that rival much larger systems. It is now powered by an advanced **ReAct (Reasoning + Acting) loop**, allowing it to think, plan, execute tools, and self-correct.

## 🚀 Key Enhancements

- **ReAct Reasoning Loop**: Instead of simple chat, ARAS now follows a multi-step reasoning process.
- **Dynamic Tool System**:
  - `shell`: Full system command execution for running code and managing environments.
  - `file_op`: Advanced file manipulation (read, write, list, delete).
  - `create_tool`: The agent can now **extend its own capabilities** by writing new Python tools.
- **Optimized for Small Models**: Specifically tuned prompts for `qwen2.5-coder:3b` and similar local models.
- **Self-Correction**: ARAS analyzes errors from its tools and automatically tries alternative solutions.
- **Persistent Memory**: Integrated short-term conversation context and long-term SQLite memory.

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
