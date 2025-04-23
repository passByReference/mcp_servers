
import asyncio
from client import MCPClient


async def main():
    client = MCPClient()
    
    # Initial connection
    await client.connect()
    
    # Simulate connection loss and reconnect
    await asyncio.sleep(5)
    await client.reconnect()
    
    # Clean up
    await client.close()

asyncio.run(main())