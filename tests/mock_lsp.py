"""A very simple mock LSP server for testing."""

import json
import sys


def main() -> None:
    while True:
        header = b""
        while True:
            line = sys.stdin.buffer.readline()
            if not line:
                return
            header += line
            if line == b"\r\n":
                break

        content_length = 0
        for h_line in header.decode("utf-8").split("\r\n"):
            if h_line.lower().startswith("content-length:"):
                content_length = int(h_line.split(":")[1].strip())

        body = sys.stdin.buffer.read(content_length).decode("utf-8")
        msg = json.loads(body)
        method = msg.get("method")

        # Respond to initialize
        if method == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": msg["id"],
                "result": {
                    "capabilities": {
                        "textDocumentSync": 1,
                        "definitionProvider": True,
                        "completionProvider": {},
                        "hoverProvider": True,
                    },
                },
            }
            _send(response)
        elif method == "textDocument/definition":
            response = {
                "jsonrpc": "2.0",
                "id": msg["id"],
                "result": {
                    "uri": msg["params"]["textDocument"]["uri"],
                    "range": {
                        "start": {"line": 0, "character": 0},
                        "end": {"line": 0, "character": 10},
                    },
                },
            }
            _send(response)
        elif method == "textDocument/completion":
            response = {
                "jsonrpc": "2.0",
                "id": msg["id"],
                "result": {
                    "isIncomplete": False,
                    "items": [
                        {"label": "print", "kind": 3},
                        {"label": "def", "kind": 2},
                    ],
                },
            }
            _send(response)
        elif "id" in msg:
            response = {
                "jsonrpc": "2.0",
                "id": msg["id"],
                "result": {},
            }
            _send(response)


def _send(msg: dict) -> None:
    body = json.dumps(msg)
    header = f"Content-Length: {len(body)}\r\n\r\n"
    sys.stdout.buffer.write((header + body).encode("utf-8"))
    sys.stdout.buffer.flush()


if __name__ == "__main__":
    main()
