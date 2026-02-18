import os
import sys
import json
from unittest.mock import MagicMock, patch

# Add agent dir to path
sys.path.insert(0, os.path.join(os.getcwd(), 'agent'))

def test_enhanced_capabilities():
    print("Testing Enhanced ARAS Agent Capabilities (Mocked AI)...")
    
    with patch('requests.post') as mock_post:
        # Scenario 1: Complex coding task with shell execution
        mock_post.side_effect = [
            # Step 1: Write code
            MagicMock(status_code=200, json=lambda: {"response": 'Thought: I need to write a python script to calculate fibonacci.\nAction: {"tool": "file_op", "parameters": {"action": "write", "path": "fib.py", "content": "def fib(n): return n if n <= 1 else fib(n-1) + fib(n-2)\\nprint(fib(5))"}}'}),
            # Step 2: Run code
            MagicMock(status_code=200, json=lambda: {"response": 'Thought: Now I will run the script to verify it.\nAction: {"tool": "shell", "parameters": {"command": "python3 workspace/fib.py"}}'}),
            # Step 3: Final Answer
            MagicMock(status_code=200, json=lambda: {"response": 'Thought: The script worked and output 5.\nFinal Answer: I have created and verified the fibonacci script. The result for fib(5) is 5.'})
        ]
        
        from agent_core import chat
        
        print("\n--- Testing ReAct Loop with Shell & File Tools ---")
        response = chat("Create a fibonacci script and run it.", model="test-model")
        print(f"Agent Response: {response}")
        assert "fibonacci" in response.lower()
        assert "5" in response
        
        # Scenario 2: Tool Extension
        mock_post.side_effect = [
            # Step 1: Create tool
            MagicMock(status_code=200, json=lambda: {"response": 'Thought: I should create a tool to fetch weather.\nAction: {"tool": "create_tool", "parameters": {"name": "weather.py", "code": "class WeatherTool: pass"}}'}),
            # Step 2: Final Answer
            MagicMock(status_code=200, json=lambda: {"response": 'Final Answer: I have created the weather tool.'})
        ]
        
        print("\n--- Testing Tool Extension ---")
        response = chat("Create a weather tool.", model="test-model")
        print(f"Agent Response: {response}")
        assert "weather" in response.lower()
        
        print("\n✅ All enhanced capability tests passed!")

if __name__ == "__main__":
    try:
        test_enhanced_capabilities()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
