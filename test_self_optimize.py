import os
import sys
from unittest.mock import MagicMock, patch

# Add agent dir to path
sys.path.insert(0, os.path.join(os.getcwd(), 'agent'))

def test_self_optimization():
    print("Testing ARAS Self-Optimization Capability (Mocked AI)...")
    
    with patch('requests.post') as mock_post:
        # Step 1: Agent decides to optimize its prompt
        mock_post.side_effect = [
            MagicMock(status_code=200, json=lambda: {"response": 'Thought: My prompt is too long. I will optimize it.\nAction: {"tool": "self_optimize", "parameters": {"target": "system_prompt", "new_content": "You are a very smart and fast AI agent."}}'}),
            MagicMock(status_code=200, json=lambda: {"response": 'Thought: I have optimized my prompt.\nFinal Answer: I have successfully optimized my internal system prompt for better performance.'})
        ]
        
        from agent_core import chat, SYSTEM_PROMPT
        
        print(f"Original Prompt snippet: {SYSTEM_PROMPT[:50]}...")
        
        response = chat("Improve your own performance.", model="test-model")
        print(f"Agent Response: {response}")
        
        # Re-import to check the change (or check the file)
        with open('agent/agent_core.py', 'r') as f:
            content = f.read()
            assert "You are a very smart and fast AI agent." in content
        
        print("✅ Self-optimization test passed!")

if __name__ == "__main__":
    try:
        test_self_optimization()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
