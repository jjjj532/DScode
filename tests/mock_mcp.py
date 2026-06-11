"""A minimal mock MCP server for testing."""

import json
import sys


def _send(msg: dict) -> None:
    body = json.dumps(msg)
    header = f"Content-Length: {len(body)}\r\n\r\n"
    sys.stdout.buffer.write((header + body).encode("utf-8"))
    sys.stdout.buffer.flush()


def _recv() -> dict | None:
    header = b""
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        header += line
        if line == b"\r\n":
            break

    content_length = 0
    for h_line in header.decode("utf-8").split("\r\n"):
        if h_line.lower().startswith("content-length:"):
            content_length = int(h_line.split(":")[1].strip())

    body = sys.stdin.buffer.read(content_length).decode("utf-8")
    return json.loads(body)


AVAILABLE_TOOLS = [
    {
        "name": "read_file",
        "description": "Read a file",
        "inputSchema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
        },
    },
    {
        "name": "echo",
        "description": "Echo text back",
        "inputSchema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
        },
    },
]


def main() -> None:
    while True:
        msg = _recv()
        if msg is None:
            break

        method = msg.get("method", "")
        msg_id = msg.get("id")

        if method == "initialize":
            _send({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2025-03-26",
                    "serverInfo": {"name": "mock-mcp", "version": "1.0"},
                    "capabilities": {"tools": {}},
                },
            })
        elif method == "notifications/initialized":
            pass
        elif method == "tools/list":
            _send({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": AVAILABLE_TOOLS},
            })
        elif method == "tools/call":
            params = msg.get("params", {})
            tool_name = params.get("name", "")
            if tool_name == "echo":
                _send({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": params.get("arguments", {}).get("text", "")}
                        ],
                    },
                })
            elif tool_name == "read_file":
                _send({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": "file content"}],
                    },
                })
            else:
                _send({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"},
                })
        elif method == "shutdown":
            _send({"jsonrpc": "2.0", "id": msg_id, "result": None})
            break


if __name__ == "__main__":
    main()
