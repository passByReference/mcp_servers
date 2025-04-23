import requests
import json
import asyncio
import aiohttp



class MCPClient:
    def __init__(self):
        self.client_id = None
        self.session = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 3

    async def connect(self):
        self.session = aiohttp.ClientSession()
         # Connect to SSE endpoint
        async with self.session.get('http://localhost:8000/sse') as resp:
            print("Connected to SSE stream")
            print(resp.content)
            async for line in resp.content:
                print("Received line:", line)
                if line.startswith(b'data:'):
                    try:
                        # Try parsing as JSON first
                        data = json.loads(line[5:].strip())
                    except json.JSONDecodeError:
                        # Fall back to raw string if not JSON
                        data = line[5:].strip().decode('utf-8')
                    print("Received:", data)
                    
                    if isinstance(data, dict) and data.get('event') == 'endpoint':
                        message_url = 'http://localhost:8000' + data['data']
                    elif isinstance(data, str) and data.startswith('/message?'):
                        message_url = 'http://localhost:8000' + data
                    
                    print(f"Message endpoint: {message_url}")
                        
                    # Send a sample message
                    payload = {
                        "jsonrpc": "2.0",
                        "method": "initialize",
                        "params": {}
                    }
                    post_resp = requests.post(message_url, json=payload)
                    print("POST response:", post_resp.text)
        
    async def reconnect(self):
        if not self.client_id:
            print("No client ID found, cannot reconnect.")
            return
        while self.reconnect_attempts < self.max_reconnect_attempts:
            try:
                async with self.session.get(f'http://localhost:8000/reconnect/{self.client_id}') as resp:
                    print(f"Reconnected to SSE stream for client ID: {self.client_id}")
                    self.reconnect_attempts = 0
                    return True
            except Exception as e:
                self.reconnect_attempts += 1
                print(f"Reconnect attempt {self.reconnect_attempts} failed: {e}")
                await asyncio.sleep(2 ** self.reconnect_attempts)
        print("Max reconnect attempts reached, giving up.")
        return False
    
    async def close(self):
        if self.session:
            await self.session.close()
            print("Session closed")

                    
                              

asyncio.run(sse_client())