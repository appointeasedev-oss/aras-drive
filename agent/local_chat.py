#!/usr/bin/env python3
"""
ARAS Local Chat Interface
Chat with ARAS directly in command prompt
"""

import os
import sys

# Get correct paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

print("=" * 50)
print("🤖 ARAS - AI Agent by SS Corporations")
print("=" * 50)
print()
print(f"Script dir: {SCRIPT_DIR}")
print(f"Project dir: {PROJECT_DIR}")

# Import from agent_core directly
sys.path.insert(0, SCRIPT_DIR)

print("Loading agent_core...")

# Import agent
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("agent_core", os.path.join(SCRIPT_DIR, "agent_core.py"))
    agent_core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(agent_core)
    
    chat = agent_core.chat
    WORKSPACE = agent_core.WORKSPACE
    
    print(f"[OK] Agent loaded")
    print(f"    Workspace: {WORKSPACE}")
except Exception as e:
    print(f"[ERROR] Loading: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Get model
model = "gemma2:4b" # Default optimized model
if len(sys.argv) > 1:
    model = sys.argv[1]

print(f"    Model: {model}")
if model.startswith("minimax"):
    print("    [Tip] Ensure MINIMAX_API_KEY is set or follow the OAuth flow.")
print()
print("Commands:")
print("  quit / exit - Stop")
print("  clear - Clear chat")
print()
print("-" * 50)

# Chat loop
while True:
    try:
        user_input = input("\nYou: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ["quit", "exit", "q"]:
            print("\n👋 Goodbye!")
            break
        
        if user_input.lower() == "clear":
            print("\n" + "=" * 50)
            print("Chat cleared")
            print("=" * 50)
            continue
        
        # Get response
        print("ARAS: ", end="", flush=True)
        response = chat(user_input, model)
        print(response)
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        break
    except Exception as e:
        print(f"\nError: {e}")
