import os
import sys
import json
from unittest.mock import MagicMock, patch

# Add agent dir to path
sys.path.insert(0, os.path.join(os.getcwd(), 'agent'))

def test_orchestration():
    print("Testing ARAS Multi-Agent Orchestration (Mocked AI)...")
    
    with patch('requests.post') as mock_post:
        # Mock responses: 1. Orchestrator Plan, 2. Explorer Step, 3. Coder Step, 4. Reviewer Step
        mock_post.side_effect = [
            # Orchestrator Plan
            MagicMock(status_code=200, json=lambda: {"response": '[{"step": 1, "task": "Search for API keys", "agent": "explorer"}, {"step": 2, "task": "Fix the bug", "agent": "coder"}]'}),
            
            # Step 1: Explorer (using codebase_manage)
            MagicMock(status_code=200, json=lambda: {"response": 'Thought: I will search for keys.\nAction: {"tool": "codebase_manage", "parameters": {"action": "search", "query": "API_KEY"}}\nObservation: Found in config.py'}),
            MagicMock(status_code=200, json=lambda: {"response": 'Final Answer: Found API keys in config.py.'}),
            
            # Step 2: Coder
            MagicMock(status_code=200, json=lambda: {"response": 'Thought: I will fix the bug.\nAction: {"tool": "file_op", "parameters": {"action": "write", "path": "fix.py", "content": "print(\'fixed\')"}}'}),
            MagicMock(status_code=200, json=lambda: {"response": 'Final Answer: Bug fixed in fix.py.'})
        ]
        
        from agent_core import chat
        
        print("\n--- Testing Multi-Agent Workflow ---")
        response = chat("Search for keys and fix the bug.", model="test-model")
        print(f"Agent Response:\n{response}")
        
        assert "config.py" in response
        assert "fix.py" in response
        print("\n✅ Orchestration test passed!")

if __name__ == "__main__":
    try:
        test_orchestration()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
