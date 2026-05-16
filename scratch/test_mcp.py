import json
import subprocess
import os

def call_mcp_tool(tool_name, arguments={}):
    mcp_server_path = "/home/kainanteh/game-dev-jam-2026/Contexto/godot-mcp/build/index.js"
    godot_path = "/usr/bin/godot"
    
    env = os.environ.copy()
    env["GODOT_PATH"] = godot_path
    
    process = subprocess.Popen(
        ["node", mcp_server_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    
    # Initialize MCP session
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "Antigravity-Test", "version": "1.0.0"}
        }
    }
    
    process.stdin.write(json.dumps(init_request) + "\n")
    process.stdin.flush()
    
    # Read init response
    response = process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
    process.stdin.flush()
    
    # Call the tool
    call_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    process.stdin.write(json.dumps(call_request) + "\n")
    process.stdin.flush()
    
    # Read responses until we get the one for id 2
    while True:
        line = process.stdout.readline()
        if not line:
            break
        try:
            resp = json.loads(line)
            if resp.get("id") == 2:
                print(json.dumps(resp, indent=2))
                break
        except:
            continue
            
    process.terminate()

if __name__ == "__main__":
    call_mcp_tool("get_debug_output")
