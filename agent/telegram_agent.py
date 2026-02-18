#!/usr/bin/env python3
"""
ARAS Telegram Agent
True AI Agent - Developed by SS Corporations
"""

import os
import sys

# Get correct paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

sys.path.insert(0, SCRIPT_DIR)

print("[ARAS] Starting...")

# Import agent
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("agent_core", os.path.join(SCRIPT_DIR, "agent_core.py"))
    agent_core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(agent_core)
    
    chat = agent_core.chat
    WORKSPACE = agent_core.WORKSPACE
    
    print("[OK] Agent loaded")
except Exception as e:
    print(f"[ERROR] {e}")
    WORKSPACE = os.path.join(PROJECT_DIR, "workspace")
    def chat(m, model): return f"Error: {e}"

# Telegram imports
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    model = context.bot_data.get("model_name", "?")
    await update.message.reply_text(
        "🤖 *ARAS - True AI Agent*\n"
        "_by SS Corporations_\n\n"
        f"Model: {model}\n\n"
        "*I think, plan, then execute!*\n\n"
        "*Commands:*\n"
        "• `list workspace` - Show files\n"
        "• `read filename` - Read file\n\n"
        "*Create:*\n"
        "• `make website about X`\n"
        "• `python script for X`\n\n"
        "*Improve:*\n"
        "• `improve it` - Improve current project\n\n"
        "_Just ask me anything!_",
        parse_mode="Markdown"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*Commands:*\n"
        "• `list workspace`\n"
        "• `read filename`\n"
        "• `delete filename`\n\n"
        "*Create:*\n"
        "• `make website about X`\n"
        "• `python script for X`\n\n"
        "*Improve:*\n"
        "• `improve it`\n\n"
        "_I read files first, then improve them!_",
        parse_mode="Markdown"
    )


async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    print(f"[MSG] {user_msg[:50]}...")
    
    # Auth
    user_id = str(update.effective_user.id)
    auth_id = context.bot_data.get("authorized_user_id", "")
    if auth_id and user_id != auth_id:
        await update.message.reply_text("⛔ Unauthorized")
        return
    
    # Typing
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Get response
    model = context.bot_data.get("model_name", "qwen2.5-coder:3b")
    response = chat(user_msg, model)
    
    print(f"[REPLY] {response[:50]}...")
    await update.message.reply_text(response)


def main():
    if len(sys.argv) < 4:
        print("Usage: python telegram_agent.py <TOKEN> <USER_ID> <MODEL>")
        input()
        sys.exit(1)
    
    token = sys.argv[1]
    user_id = sys.argv[2]
    model = sys.argv[3]
    
    print(f"🤖 ARAS - SS Corporations")
    print(f"   Model: {model}")
    print(f"   Workspace: {WORKSPACE}")
    print()
    
    try:
        app = Application.builder().token(token).build()
    except Exception as e:
        print(f"❌ {e}")
        input()
        sys.exit(1)
    
    app.bot_data["authorized_user_id"] = user_id
    app.bot_data["model_name"] = model
    
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
    
    print("✅ ARAS running. Message me!")
    print("=" * 40)
    
    try:
        app.run_polling(poll_interval=1.0, drop_pending_updates=True)
    except KeyboardInterrupt:
        print("\n👋 Stopped")
    except Exception as e:
        print(f"Error: {e}")
        input()


if __name__ == "__main__":
    main()
