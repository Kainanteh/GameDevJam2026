# Cómo conectar tu IA al Servidor MCP de Godot

He instalado un servidor MCP en tu proyecto. Esto permite que asistentes como **Claude Desktop**, **Cursor** o **Cline** interactúen directamente con Godot.

## Configuración para Claude Desktop

Añade lo siguiente a tu archivo `claude_desktop_config.json` (normalmente en `~/.config/Claude/claude_desktop_config.json` en Linux):

```json
{
  "mcpServers": {
    "godot": {
      "command": "node",
      "args": ["/home/kainanteh/game-dev-jam-2026/Contexto/godot-mcp/build/index.js"],
      "env": {
        "GODOT_PATH": "/usr/bin/godot",
        "DEBUG": "false",
        "READ_ONLY": "false"
      }
    }
  }
}
```

## Configuración para Cursor

1. Ve a **Settings** -> **Features** -> **MCP**.
2. Haz clic en **+ Add New MCP Server**.
3. Configura:
   - **Name**: `godot`
   - **Type**: `command`
   - **Command**: `node /home/kainanteh/game-dev-jam-2026/Contexto/godot-mcp/build/index.js`
4. En las variables de entorno (si Cursor lo permite en tu versión) o editando el `.cursor/mcp.json` del proyecto:
   ```json
   {
     "mcpServers": {
       "godot": {
         "command": "node",
         "args": ["/home/kainanteh/game-dev-jam-2026/Contexto/godot-mcp/build/index.js"],
         "env": {
           "GODOT_PATH": "/usr/bin/godot"
         }
       }
     }
   }
   ```

## Herramientas Disponibles

Una vez conectado, podrás usar comandos como:
- `run_project`: Ejecuta el juego.
- `get_debug_output`: Ver los logs de la consola.
- `get_project_info`: Ver la estructura del proyecto.
- `add_node` / `edit_node`: Manipular la escena directamente.

---
*Nota: Antigravity ya está "conectado" internamente y puede usar estas herramientas mediante scripts de ayuda.*
