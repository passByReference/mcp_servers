# Alibaba MCP Server Implemetation

## Wiki
Implement the code example at this blog post: https://mp.weixin.qq.com/s/0YZNEJmKJJioyzARt1idTA?poc_token=HM0LCGijrv9U65m_C7RWba5Z78pXac0_XtW3enGT


## How to Run the Experiment
Start the server
`uvicorn mcp_server:app --reload`

Run the client
`python client.py`

## Expected Flow
1. Client connects to /sse endpoint

2. Server generates a client ID and returns the message endpoint via SSE

3. Client receives the endpoint URL and sends a message to /message

4. Server processes the message and sends responses back via SSE

5. Client receives the responses in real-time

## Architecture Overview


## Q & A
1. In the server, the message method does not explicitly return "data", then how is the data returned to the client?

Data is returned to the client asynchronously via Server-Sent Events (SSE), not through the HTTP response of the /message endpoint.

During the test, we have two terminals open. One is SSE connection through `curl -N http://localhost:8000/sse`. Another is where we send the POST request. 

The POST request will syncrhonously receive the response specified in the message method ("OK" in current implmentation). The "data" will be asynchronously dequeed via the "reader()" method which will be automatically called, and sent to the SSE connection.