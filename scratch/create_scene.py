import json
import subprocess
import os

def create_main_scene():
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
    
    # Create scene
    print("Creando escena principal...")
    send({
        "jsonrpc": "2.0", 
        "id": 2, 
        "method": "tools/call", 
        "params": {
            "name": "create_scene", 
            "arguments": {
                "projectPath": "/home/kainanteh/game-dev-jam-2026",
                "scenePath": "Main.tscn",
                "rootNodeType": "Node2D"
            }
        }
    })
    print(json.dumps(receive(2), indent=2))
            
    process.terminate()

if __name__ == "__main__":
    create_main_scene()
