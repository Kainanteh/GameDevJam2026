import json
import subprocess
import os
import time

def run_and_debug():
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
    
    def send(msg):
        process.stdin.write(json.dumps(msg) + "\n")
        process.stdin.flush()

    def receive(target_id):
        while True:
            line = process.stdout.readline()
            if not line: return None
            try:
                resp = json.loads(line)
                if resp.get("id") == target_id: return resp
            except: continue

    # Initialize
    send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "Test", "version": "1"}}})
    receive(1)
    send({"jsonrpc": "2.0", "method": "notifications/initialized"})
    
    # Run project
    print("Iniciando proyecto...")
    send({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "run_project", "arguments": {"projectPath": "/home/kainanteh/game-dev-jam-2026"}}})
    print(json.dumps(receive(2), indent=2))
    
    # Wait and get output
    for i in range(3):
        time.sleep(2)
        print(f"\nObteniendo salida de depuración ({i+1})...")
        send({"jsonrpc": "2.0", "id": 10+i, "method": "tools/call", "params": {"name": "get_debug_output", "arguments": {}}})
        print(json.dumps(receive(10+i), indent=2))
            
    process.terminate()

if __name__ == "__main__":
    run_and_debug()
