import os
import sys
import requests
from unittest.mock import MagicMock, patch

# Add agent dir to path
sys.path.insert(0, os.path.join(os.getcwd(), 'agent'))

def test_ai_call_retries():
    print("Testing ARAS AI Call Retry Logic...")
    
    with patch('requests.post') as mock_post:
        # Simulate two timeouts followed by a success
        mock_post.side_effect = [
            requests.exceptions.Timeout("Read timeout"),
            requests.exceptions.Timeout("Read timeout"),
            MagicMock(status_code=200, json=lambda: {"response": "Success after retries!"})
        ]
        
        from agent_core import ai_call
        
        print("Calling ai_call (should retry twice and then succeed)...")
        # Use small timeout for test speed
        response = ai_call("test prompt", model="test-model", timeout=1, retries=3)
        
        print(f"Final Response: {response}")
        assert response == "Success after retries!"
        assert mock_post.call_count == 3
        print("✅ Retry logic test passed!")

if __name__ == "__main__":
    try:
        test_ai_call_retries()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
