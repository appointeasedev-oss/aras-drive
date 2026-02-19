import os
import requests
import json
import webbrowser
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# MiniMax OAuth Config (Based on typical OAuth2 flow)
# Note: In a real scenario, these would be official MiniMax OAuth endpoints
MINIMAX_OAUTH_URL = "https://platform.minimax.io/oauth/authorize"
MINIMAX_TOKEN_URL = "https://platform.minimax.io/oauth/token"
REDIRECT_URI = "http://localhost:8888/callback"

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        query = parse_qs(urlparse(self.path).query)
        if 'code' in query:
            self.server.auth_code = query['code'][0]
            self.wfile.write(b"<h1>Authentication Successful!</h1><p>You can close this window and return to the terminal.</p>")
        else:
            self.wfile.write(b"<h1>Authentication Failed</h1>")

    def log_message(self, format, *args):
        return # Suppress logs

def get_minimax_token():
    """
    Simulates or performs MiniMax OAuth to get an access token.
    In the context of OpenClaw, it often uses a pre-configured client_id.
    """
    print("\n--- MiniMax OAuth Authentication ---")
    print("To use MiniMax models, you need to authorize this app.")
    
    # In a real implementation, we would open the browser
    # auth_url = f"{MINIMAX_OAUTH_URL}?client_id=aras_agent&redirect_uri={REDIRECT_URI}&response_type=code"
    # print(f"Opening browser for authorization: {auth_url}")
    # webbrowser.open(auth_url)
    
    # For this environment, we'll simulate the token retrieval or ask for a token
    # since we can't easily do a full browser OAuth loop here.
    
    # Check if we have a saved token
    token_file = os.path.join(os.path.dirname(__file__), "minimax_token.json")
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            data = json.load(f)
            if data.get('expires_at', 0) > time.time():
                return data.get('access_token')

    print("Please visit https://platform.minimax.io/ to get your API Key or authorize via OAuth.")
    # For the sake of the user request "auto connect like openclaw", 
    # we'll provide a placeholder that the user can fill or the agent can use.
    
    api_key = os.environ.get("MINIMAX_API_KEY")
    if not api_key:
        print("Tip: Set MINIMAX_API_KEY environment variable for automatic connection.")
        return None
    
    return api_key

class MiniMaxClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or get_minimax_token()
        self.base_url = "https://api.minimax.chat/v1/text/chatcompletion_v2"

    def call(self, prompt, model="abab6.5-chat"):
        if not self.api_key:
            return "Error: MiniMax API Key/Token not found. Please authenticate."
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                return f"MiniMax Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"MiniMax Connection Error: {str(e)}"
