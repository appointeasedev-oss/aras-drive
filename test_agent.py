import os
import sys
from unittest.mock import MagicMock, patch

# Add agent dir to path
sys.path.insert(0, os.path.join(os.getcwd(), 'agent'))

def test_mock_agent():
    print("Testing ARAS Agent Refactor (Mocked AI)...")
    
    # Mocking requests.post to simulate Ollama response
    with patch('requests.post') as mock_post:
        # Step 1: Agent wants to list files
        # Step 2: Agent gives final answer
        mock_post.side_effect = [
            MagicMock(status_code=200, json=lambda: {"response": 'Thought: I should check the files first.\nAction: {"tool": "file_op", "parameters": {"action": "list", "path": ""}}'}),
            MagicMock(status_code=200, json=lambda: {"response": 'Thought: I see the files. I will tell the user.\nFinal Answer: The workspace has some files.'})
        ]
        
        from agent_core import chat
        
        print("Sending message to agent...")
        response = chat("What's in my workspace?", model="test-model")
        print(f"Agent Response: {response}")
        
        assert "workspace" in response.lower()
        print("✅ ReAct loop test passed!")

if __name__ == "__main__":
    try:
        test_mock_agent()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
