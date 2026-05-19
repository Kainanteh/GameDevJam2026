import os

def main():
    src_file = "/home/kainanteh/game-dev-jam-2026/Contexto/webrelativa.txt"
    dest_file = "/home/kainanteh/game-dev-jam-2026/preview_itch.html"
    
    if not os.path.exists(src_file):
        print(f"Error: {src_file} no encontrado.")
        return
        
    with open(src_file, "r", encoding="utf-8") as f:
        html = f.read()
        
    # Reemplazar la imagen de fondo de la página por la local
    html = html.replace(
        "https://img.itch.zone/aW1nLzI3MzQxMTYwLnBuZw==/original/7dJDfk.png",
        "tile_background.png"
    )
    
    # Reemplazar la imagen de fondo del reproductor (embed) por la local
    html = html.replace(
        "https://img.itch.zone/aW1nLzI3MzQxMTY4LnBuZw==/original/JAo26V.png",
        "tile_embed.png"
    )
    
    # Reemplazar la imagen de cabecera (banner) por el logotipo transparente local
    html = html.replace(
        "https://img.itch.zone/aW1nLzI3MzQxMjczLnBuZw==/original/zhYJQY.png",
        "logo_titulo_transparent.png"
    )
    
    # Reemplazar el origen del iframe del juego para cargar la build local de Godot
    # Esto te permitirá jugar localmente directamente en la plantilla de itch.io
    html = html.replace(
        "https://html-classic.itch.zone/html/17590695/index.html?v=1779132477",
        "build/index.html"
    )
    
    with open(dest_file, "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"¡Creado con éxito el archivo de preview local en: {dest_file}!")

if __name__ == "__main__":
    main()
