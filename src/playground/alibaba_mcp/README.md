# Alibaba MCP Server Implemetation

## Wiki
Implement the code example at this blog post: https://mp.weixin.qq.com/s/0YZNEJmKJJioyzARt1idTA?poc_token=HM0LCGijrv9U65m_C7RWba5Z78pXac0_XtW3enGT


## How to Run the Experiment
Start the server
`uvicorn mcp_server:app --reload`

Run the client
`python client.py`

## Architecture Overview
1. Components
* Server: FastAPI application with two endpoints:
  * `GET /sse`: Establishes an SSE connection
  * `POST /message`: Receives client messages
* Client: Connects to `/sse` and **listens** for real-time events while sending messages via `/message`.

2. Communication Flow
   1. Client connects to /sse
      * The server generates a unique client_id using uuid.
      * Creates an MCPServer instance and stores it in mcpHub (a dictionary).
      * Sends back an SSE stream containing the client’s dedicated /message endpoint.
   2. Client receives SSE events
      * The client listens for messages like:
        ```
            event: endpoint
            data: /message?client_id=1234-5678-90ab
        ```
      * It extracts the `client_id` and uses it to send messages.

   3. Client sends messages via `/message`
       * The client POSTs JSON-RPC-like requests:
       ```
           {
           "jsonrpc": "2.0",
           "method": "initialize",
           "params": {}
           }
       ```
       * The server processes the method (e.g., initialize, tools/list) and responds via SSE.

   4. Server pushes responses via SSE
       * The MCPServer class uses an `asyncio.Queue` to manage messages.

       * When the client sends a request, the server enqueues a response, which is streamed back in real time.

## Strengths of This Architecture
✅ 1. Real-Time Updates (SSE)

    Unlike HTTP polling, SSE allows the server to push updates instantly.

    Works well for notifications, live logs, or progress tracking.

✅ 2. Lightweight & HTTP-Based

    Uses standard HTTP/HTTPS (no WebSocket complexity).

    Works behind proxies and firewalls (unlike WebSockets).

✅ 3. Scalable Client Handling

    Each client gets a unique client_id and MCPServer instance.

    The mcpHub dictionary allows tracking multiple clients.

✅ 4. Asynchronous (FastAPI + asyncio)

    Efficiently handles many concurrent connections.

    Uses Python’s native async I/O for high performance.

✅ 5. JSON-RPC-Like Structure

    The method and params system makes it easy to extend functionality.

    Works well for RPC (Remote Procedure Call) patterns.

## Weaknesses & Limitations
❌ 1. SSE Limitations

    Unidirectional: Only server → client (client must use separate HTTP requests to send data).

    No built-in reconnection: If the connection drops, the client must manually reconnect.

    Browser limits: Some browsers restrict the number of SSE connections.

❌ 2. No Persistence

    If the server restarts, all client_ids and queues are lost.

    No message history—clients must reinitialize.

❌ 3. Scalability Bottlenecks

    asyncio.Queue is in-memory → Not distributed.

    If scaled horizontally (multiple servers), clients must reconnect to the right instance.

❌ 4. No Authentication

    Anyone with the client_id can send messages (no security checks).

    No rate limiting or DDoS protection.

❌ 5. Debugging Complexity

    SSE streams can be hard to inspect (unlike REST APIs).

    Errors in MCPServer.request() could silently fail.


## Q & A
1. In the server, the message method does not explicitly return "data", then how is the data returned to the client?

Data is returned to the client asynchronously via Server-Sent Events (SSE), not through the HTTP response of the /message endpoint.

During the test, we have two terminals open. One is SSE connection through `curl -N http://localhost:8000/sse`. Another is where we send the POST request. 

The POST request will syncrhonously receive the response specified in the message method ("OK" in current implmentation). The "data" will be asynchronously dequeed via the "reader()" method which will be automatically called, and sent to the SSE connection.