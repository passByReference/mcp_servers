from random import randint
from fastapi import FastAPI, Request
import uuid
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
import json
import asyncio
from typing import Optional

app = FastAPI()
mcpHub = {}

class McpRequest(BaseModel):
    id: Optional[int] = None
    jsonrpc: str
    method: str
    params: Optional[dict] = None

class MCPServer:
    def __init__(self):
        self.queue = asyncio.Queue()
        
    async def reader(self):
        while True:
            event = await self.queue.get()
            print("Sending event:", event)
            yield event

    async def request(self, payload: McpRequest):
        if payload.method == "initialize":
            await self.queue.put({"event": "message", "data": "initialized"})
        elif payload.method == "tools/random_number":
            # Simulate fetching tools
            result = [randint(1, 10000)]
            result.append(len(mcpHub)) 
            await self.queue.put({"event": "message", "data": result})
        else:
            await self.queue.put({"event": "message", "data": "unknown method"})

@app.get("/sse")
async def sse():
    client_id = str(uuid.uuid4())
    mcp = MCPServer()
    mcpHub[client_id] = mcp
    await mcp.queue.put({"event": "endpoint", "data": f"/message?client_id={client_id}"})
    return EventSourceResponse(mcp.reader())

@app.get("/reconnect/{client_id}")
async def reconnect(client_id: str):
    if client_id in mcpHub:
        mcp = mcpHub[client_id]
        await mcp.queue.put({"event": "message", "data": "reconnected"})
        return EventSourceResponse(mcp.reader())
    else:
        return {"status": "client not found"}, 404
    
@app.post("/message")
async def message(request: Request, payload: McpRequest):
    client_id = request.query_params.get("client_id")
    if client_id not in mcpHub:
        return "no client"
    await mcpHub[client_id].request(payload)
    return "ok"