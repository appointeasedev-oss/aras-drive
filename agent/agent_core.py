#!/usr/bin/env python3
"""
ARAS - True AI Agent
Multi-step reasoning, verification, file operations
"""

import os
import json
import requests
import re

# Config
AGENT_DIR = os.path.dirname(os.path.dirname(__file__))
WORKSPACE = os.path.join(AGENT_DIR, "workspace")
MEMORY_DIR = os.path.join(AGENT_DIR, "memory")
OLLAMA_URL = "http://localhost:11434/api/generate"

os.makedirs(WORKSPACE, exist_ok=True)
os.makedirs(MEMORY_DIR, exist_ok=True)

print(f"[ARAS] Workspace: {WORKSPACE}")


# === MEMORY ===
class Memory:
    def __init__(self):
        self.short = {"messages": [], "current_project": None}
        self.long = {}
        self.load()
    
    def load(self):
        try:
            s = os.path.join(MEMORY_DIR, "short.json")
            if os.path.exists(s):
                data = json.load(open(s))
                self.short = {"messages": data.get("messages", []), "current_project": data.get("current_project")}
        except: 
            self.short = {"messages": [], "current_project": None}
        try:
            l = os.path.join(MEMORY_DIR, "long.json")
            if os.path.exists(l):
                self.long = json.load(open(l))
        except: 
            self.long = {}
    
    def save(self):
        json.dump(self.short, open(os.path.join(MEMORY_DIR, "short.json"), "w"))
        json.dump(self.long, open(os.path.join(MEMORY_DIR, "long.json"), "w"))
    
    def add_msg(self, role, text):
        self.short["messages"].append({"role": role, "text": text})
        if len(self.short["messages"]) > 20:
            self.short["messages"] = self.short["messages"][-20:]
        self.save()
    
    def set_project(self, name):
        self.short["current_project"] = name
        self.save()
    
    def remember(self, key, value):
        self.long[key] = {"value": value}
        self.save()
    
    def recall(self, key):
        return self.long.get(key, {}).get("value")
    
    def get_context(self):
        msgs = []
        for m in self.short.get("messages", []):
            # Handle both "text" and "content" keys
            text = m.get("text") or m.get("content") or m.get("message", "")
            if text:
                msgs.append({"role": m.get("role", "user"), "text": text})
        
        recent = msgs[-10:] if len(msgs) > 10 else msgs
        return "\n".join([f"{m['role']}: {m['text'][:150]}" for m in recent])

memory = Memory()
print("[OK] Memory loaded")


# === AI CALLS ===
def ai(prompt, model="qwen2.5-coder:3b", timeout=120):
    """Make AI call"""
    print(f"[AI] Calling...")
    try:
        r = requests.post(OLLAMA_URL, json={"model": model, "prompt": prompt, "stream": False}, timeout=timeout)
        if r.status_code == 200:
            result = r.json().get("response", "").strip()
            print(f"[AI] Got {len(result)} chars")
            return result
    except Exception as e:
        print(f"[AI] Error: {e}")
    return None


# === FILE OPS ===
def save_file(path, content):
    """Save file"""
    try:
        full = os.path.join(WORKSPACE, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, "w", encoding="utf-8").write(content)
        print(f"[SAVE] {path}")
        return True
    except Exception as e:
        print(f"[SAVE ERROR] {e}")
        return False


def read_file(path):
    """Read file"""
    try:
        full = os.path.join(WORKSPACE, path)
        if os.path.exists(full):
            return open(full, "r", encoding="utf-8").read()
    except: pass
    return None


def list_files(path=""):
    """List files"""
    base = os.path.join(WORKSPACE, path)
    if not os.path.exists(base):
        return []
    return [f for f in os.listdir(base)]


def extract_code(text):
    """Extract code from markdown"""
    if "```" in text:
        m = re.findall(r'```(?:\w+)?\n(.*?)```', text, re.DOTALL)
        if m:
            return m[0].strip()
    
    if "<html" in text.lower():
        start = text.find("<!DOCTYPE") 
        if start == -1: start = text.find("<html")
        end = text.rfind("</html>") + 7
        if start >= 0 and end > 0:
            return text[start:end]
    
    return text


# === TRUE AI AGENT ===
def agent(user_msg, model):
    """True AI Agent - multi-step reasoning"""
    msg = user_msg.lower().strip()
    original = user_msg.strip()
    
    print(f"[AGENT] Input: {original[:50]}...")
    memory.add_msg("user", original)
    
    # === FILE COMMANDS ===
    if msg in ["list workspace", "ls", "files"]:
        files = list_files()
        memory.add_msg("assistant", f"Listed {len(files)} files")
        return f"📁 Files:\n" + "\n".join([f"  {f}" for f in files]) if files else "  (empty)"
    
    if msg.startswith("read "):
        path = original[5:].strip()
        content = read_file(path)
        if content:
            memory.add_msg("assistant", f"Read {path}")
            if len(content) > 2000:
                content = content[:2000] + "\n...(truncated)"
            return f"📄 {path}:\n\n{content}"
        return f"❌ Not found: {path}"
    
    if msg.startswith("delete "):
        path = original[7:].strip()
        full = os.path.join(WORKSPACE, path)
        try:
            if os.path.isdir(full):
                import shutil
                shutil.rmtree(full)
            elif os.path.exists(full):
                os.remove(full)
            memory.add_msg("assistant", f"Deleted {path}")
            return f"✅ Deleted: {path}"
        except:
            return f"❌ Cannot delete: {path}"
    
    # === IMPROVE EXISTING PROJECT ===
    if any(x in msg for x in ["improve", "update", "add more", "enhance", "more pages"]):
        current = memory.short.get("current_project")
        
        if not current:
            # Find most recent project
            files = list_files()
            for f in files:
                if os.path.isdir(os.path.join(WORKSPACE, f)):
                    current = f
                    break
        
        if not current:
            return "❌ No project to improve. Create one first."
        
        print(f"[AGENT] Improving: {current}")
        
        # STEP 1: Read all existing files
        print("[STEP 1] Reading existing files...")
        project_path = os.path.join(WORKSPACE, current)
        existing = {}
        
        for root, dirs, files in os.walk(project_path):
            for f in files:
                path = os.path.join(root, f)
                rel = os.path.relpath(path, WORKSPACE)
                try:
                    content = open(path, "r", encoding="utf-8").read()
                    existing[rel] = content[:2000]
                except: pass
        
        if not existing:
            return "❌ Cannot read project files."
        
        # Show what we have
        file_list = ", ".join(existing.keys())
        print(f"[AGENT] Found files: {file_list}")
        
        # STEP 2: Analyze with AI what to improve
        print("[STEP 2] AI analyzing...")
        
        analyze_prompt = f"""You are an expert web developer analyzing an existing project.

Project: {current}
Existing files: {file_list}

First file content:
{list(existing.values())[0][:1000]}

User wants: {original}

What improvements are needed? List 3-5 specific improvements as a numbered list."""
        
        improvements = ai(analyze_prompt, model, timeout=90)
        
        if not improvements:
            return "❌ Cannot analyze. Is Ollama running?"
        
        print(f"[AGENT] Improvements:\n{improvements[:200]}...")
        
        # STEP 3: Generate improved files one by one
        print("[STEP 3] Generating improved files...")
        
        for fname in existing:
            print(f"[AI] Improving {fname}...")
            
            improve_prompt = f"""You are improving an existing file: {fname}

Current content (first 1500 chars):
{existing[fname][:1500]}

User wants: {original}

Improvements to make:
{improvements}

Generate the IMPROVED full content for this file.
- Keep the same format (HTML, CSS, JS)
- Make it better - more content, better styling, more features
- Return ONLY the complete code, no explanation

File: {fname}"""
            
            new_content = ai(improve_prompt, model, timeout=180)
            
            if new_content:
                # Extract code
                code = extract_code(new_content)
                
                # Verify it's not empty
                if len(code) > 100:
                    if save_file(fname, code):
                        print(f"[OK] Updated {fname}")
                else:
                    print(f"[WARN] Content too short for {fname}")
        
        memory.add_msg("assistant", f"Improved {current}")
        memory.remember(f"project_{current}", "improved")
        
        return f"✅ Improved {current}!\n\nImprovements made:\n{improvements[:300]}...\n\n📂 {WORKSPACE}\\{current}\\"
    
    # === CREATE NEW PROJECT ===
    if any(x in msg for x in ["make", "create", "build", "generate", "write"]):
        print("[AGENT] Creating new project...")
        
        # Determine type
        ptype = "website"
        if "python" in msg or "script" in msg:
            ptype = "python"
        elif "discord" in msg:
            ptype = "discord"
        
        # Extract topic
        topic = original
        for prep in ["about ", "on ", "for ", "named "]:
            if prep in msg:
                topic = msg.split(prep)[1].strip("?.!").strip()
                break
        
        if "parks" in msg:
            topic = "Parks and Nature"
        
        # Project name
        pname = "".join(c for c in topic.lower().replace(" ", "_")[:20] if c.isalnum() or c == "_")
        memory.set_project(pname)
        
        print(f"[AGENT] Creating {ptype}: {pname} ({topic})")
        
        if ptype == "website":
            # STEP 1: Plan the website
            print("[STEP 1] Planning website structure...")
            
            plan_prompt = f"""Plan a complete website about {topic}.
Return a list of pages needed as:
PAGES: home.html,about.html,services.html,contact.html

Or for simple sites:
PAGES: index.html,style.css"""
            
            plan = ai(plan_prompt, model, timeout=60)
            
            pages = ["index.html"]
            if plan and "PAGES:" in plan:
                pages = [p.strip() for p in plan.split("PAGES:")[1].split(",")]
            
            print(f"[AGENT] Will create: {pages}")
            
            # STEP 2: Generate each file with AI
            for page in pages:
                print(f"[AI] Generating {page}...")
                
                page_prompt = f"""Create a complete, professional {page} for a website about {topic}.

Requirements:
- Professional HTML5 structure
- Real content about {topic} (NOT lorem ipsum)
- Internal CSS for styling
- Navigation to other pages
- Modern, clean design

Pages to link: {", ".join(pages)}

Return ONLY the complete HTML code."""
                
                content = ai(page_prompt, model, timeout=180)
                
                if content:
                    code = extract_code(content)
                    
                    if len(code) > 200:
                        save_file(f"{pname}/{page}", code)
                        print(f"[OK] Created {page}")
                    else:
                        # Fallback simple page
                        simple = f"""<!DOCTYPE html>
<html><head><title>{topic}</title></head>
<body><h1>{topic}</h1><p>Content about {topic}.</p></body></html>"""
                        save_file(f"{pname}/{page}", simple)
                        print(f"[OK] Created {page} (fallback)")
            
            # STEP 3: Generate CSS if needed
            if any(p.endswith(".html") for p in pages):
                print("[AI] Generating style.css...")
                
                css_prompt = f"""Create a complete CSS file for a {topic} website.

Return ONLY CSS code with:
- Modern responsive design
- Navigation styling
- Hero section
- Content sections
- Footer
- Hover effects
- Mobile-friendly

No explanations, just CSS."""
                
                css = ai(css_prompt, model, timeout=120)
                
                if css and "{" in css:
                    save_file(f"{pname}/style.css", css)
                    print("[OK] Created style.css")
            
            memory.add_msg("assistant", f"Created {pname}")
            memory.remember(f"project_{pname}", topic)
            
            return f"✅ Created {ptype}: {topic}\n📂 {WORKSPACE}\\{pname}\\"
        
        elif ptype == "python":
            code_prompt = f"""Write a complete, working Python script for: {topic}

Requirements:
- Proper imports
- Functions with docstrings
- Error handling
- Main execution
- Comments

Return ONLY Python code."""
            
            code = ai(code_prompt, model, timeout=180)
            
            if code:
                code = extract_code(code)
                save_file(f"{pname}/{pname}.py", code)
                memory.add_msg("assistant", f"Created {pname}")
                
                return f"✅ Created Python script: {topic}\n📂 {WORKSPACE}\\{pname}\\{pname}.py"
        
        return "❌ Creation failed. Try again."
    
    # === GENERAL CHAT ===
    print("[AGENT] Chat mode...")
    
    ctx = memory.get_context()
    prefs = {k: v["value"] for k, v in memory.long.items() if "value" in v}
    
    chat_prompt = f"""You are ARAS, an AI Agent by SS Corporations.

Conversation:
{ctx}

User: {original}

Remember: You are ARAS. If asked to create something, use the create command.
{json.dumps(prefs) if prefs else ""}

ARAS:"""
    
    response = ai(chat_prompt, model, timeout=90)
    
    if response:
        response = response.replace("Qwen", "ARAS").replace("Alibaba", "SS Corporations")
        memory.add_msg("assistant", response)
        return response
    
    return "Connection error. Try again."


def chat(msg, model):
    return agent(msg, model)
