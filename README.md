# ARAS-Drive 🐦

Portable AI Agent Setup for USB/Local Machines

## What is ARAS-Drive?

A clean, reversible setup system to run a Telegram bot connected to Ollama (local AI). Everything installs user-level (no admin required) and tracks what was added for clean removal.

## Files

| File | Purpose |
|------|---------|
| `setup.bat` | Install Python, Ollama, and required packages |
| `start.bat` | Start Ollama + Telegram bot |
| `clean.bat` | Remove only what setup.bat installed |
| `requirements.txt` | Python dependencies |
| `agent/telegram_agent.py` | Telegram bot that connects to Ollama |

## Quick Start

### 1. Run Setup
```
Double-click setup.bat
```

This will:
- Check for Python (prompt to install if missing)
- Install Ollama if not present
- Install required Python packages

### 2. Get Telegram Credentials

1. **Bot Token**: Message @BotFather on Telegram → `/newbot` → Follow prompts
2. **User ID**: Message @userinfobot on Telegram → Get your ID

### 3. Start ARAS
```
Double-click start.bat
```

Enter your Bot Token and User ID when prompted.

### 4. Chat!

Open Telegram and message your bot. It will respond using Ollama's AI.

## Cleanup

To remove everything ARAS-Drive installed:
```
Double-click clean.bat
```

This reads `install_log.txt` and removes only what was added.

## Configuration

### Change Ollama Model

Edit `agent/telegram_agent.py` and change:
```python
DEFAULT_MODEL = "llama3.2"
```

To another model like `mistral`, `codellama`, etc.

### OpenClaw Integration

The `start.bat` includes full path to OpenClaw:
```
C:\Users\satvi\AppData\Roaming\npm\node_modules\openclaw\openclaw.mjs
```

Modify this in `start.bat` if your OpenClaw is installed elsewhere.

## Troubleshooting

### "Python not found"
Install Python from https://www.python.org/downloads/
- Check "Add Python to PATH"
- Choose "Install for current user only"

### "Cannot connect to Ollama"
Make sure Ollama is running:
```cmd
ollama serve
```

### "python-telegram-bot not installed"
Run `setup.bat` again to install dependencies.

## Requirements

- Windows 10/11
- Internet connection (for downloading installers)
- Telegram account

## License

MIT
