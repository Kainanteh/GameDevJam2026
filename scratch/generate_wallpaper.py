import os
import random
from PIL import Image, ImageDraw

def generate_panoramic_wallpaper():
    logo_path = "/home/kainanteh/game-dev-jam-2026/Contexto/GameDevTV20206.png"
    out_dir = "/home/kainanteh/game-dev-jam-2026"
    
    # 1. CREAR EL LIENZO PANORÁMICO DE 1920x1080
    # Usamos el color de fondo abisal puro #07060a
    wallpaper = Image.new("RGBA", (1920, 1080), (7, 6, 10, 255))
    draw = ImageDraw.Draw(wallpaper)
    
    # 2. DIBUJAR ESTRELLAS COHERENTES Y ORGÁNICAS (SOLO EN LATERALES)
    # Lateral Izquierdo: x de 20 a 380
    # Lateral Derecho: x de 1540 a 1900
    
    # Paleta de colores exacta del logotipo
    neon_blue = (0, 210, 255, 255)
    neon_pink = (255, 0, 127, 255)
    star_white = (255, 255, 255, 220)
    
    def draw_star(draw_obj, cx, cy, color, size):
        if size == 1:
            draw_obj.point((cx, cy), fill=color)
        elif size == 2:
            # Estrella mediana de 2 píxeles
            draw_obj.point((cx, cy), fill=color)
            draw_obj.point((cx+1, cy), fill=color)
        elif size == 3:
            # Estrella pixel-art en cruz con brillo suave (Bloom)
            draw_obj.point((cx, cy), fill=color)
            draw_obj.point((cx-1, cy), fill=(color[0], color[1], color[2], 120))
            draw_obj.point((cx+1, cy), fill=(color[0], color[1], color[2], 120))
            draw_obj.point((cx, cy-1), fill=(color[0], color[1], color[2], 120))
            draw_obj.point((cx, cy+1), fill=(color[0], color[1], color[2], 120))
        elif size == 4:
            # Gran estrella Memento Mori resplandeciente
            draw_obj.point((cx, cy), fill=star_white)
            draw_obj.point((cx-1, cy), fill=color)
            draw_obj.point((cx+1, cy), fill=color)
            draw_obj.point((cx, cy-1), fill=color)
            draw_obj.point((cx, cy+1), fill=color)
            # Brillo lejano
            draw_obj.point((cx-2, cy), fill=(color[0], color[1], color[2], 60))
            draw_obj.point((cx+2, cy), fill=(color[0], color[1], color[2], 60))
            draw_obj.point((cx, cy-2), fill=(color[0], color[1], color[2], 60))
            draw_obj.point((cx, cy+2), fill=(color[0], color[1], color[2], 60))

    # Sembrar estrellas fijas hermosas en el Lateral Izquierdo
    left_stars = [
        (80, 150, neon_blue, 4),
        (220, 280, neon_pink, 3),
        (120, 420, star_white, 1),
        (310, 110, neon_pink, 2),
        (60, 580, neon_blue, 3),
        (280, 690, star_white, 1),
        (190, 850, neon_pink, 4),
        (90, 930, neon_blue, 2),
        (340, 480, star_white, 1),
        (150, 720, neon_blue, 3)
    ]
    
    # Sembrar estrellas fijas hermosas en el Lateral Derecho
    right_stars = [
        (1820, 120, neon_pink, 4),
        (1650, 220, neon_blue, 3),
        (1780, 450, star_white, 1),
        (1580, 150, neon_pink, 2),
        (1850, 550, neon_blue, 3),
        (1620, 680, star_white, 1),
        (1730, 820, neon_pink, 4),
        (1800, 950, neon_blue, 2),
        (1560, 900, star_white, 1)
    ]
    
    for x, y, col, sz in left_stars:
        draw_star(draw, x, y, col, sz)
        
    for x, y, col, sz in right_stars:
        draw_star(draw, x, y, col, sz)

    # 3. MENTAR E INTEGRAR EL LOGO DE LA JAM EN EL LATERAL DERECHO
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        
        # Redimensionar el logo a 260px de ancho (escala perfecta e idéntica a Flammension)
        w_target = 260
        w_percent = (w_target / float(logo.size[0]))
        h_target = int((float(logo.size[1]) * float(w_percent)))
        logo_resized = logo.resize((w_target, h_target), Image.Resampling.LANCZOS)
        
        # Posicionar el logo flotando en el espacio a la derecha (x=1600, y=360)
        # Esto queda visible a la derecha de la columna del juego
        wallpaper.paste(logo_resized, (1600, 360), logo_resized)
        print("¡Logo de la Jam fusionado con éxito en el lateral derecho!")
    else:
        print("Error: Logo de la Jam no encontrado.")

    # 4. GUARDAR WALLPAPER PANORÁMICO
    bg_out = os.path.join(out_dir, "tile_background.png")
    bg_brain = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/tile_background.png"
    
    wallpaper.save(bg_out, "PNG")
    wallpaper.save(bg_brain, "PNG")
    print("Wallpaper panorámico guardado en:", bg_out)
    
    # 5. GENERAR EMBED BG PLANO SIN LÍNEAS
    # Para que se funda de forma invisible con el fondo, un bloque liso de #07060a
    embed_tile = Image.new("RGBA", (64, 64), (7, 6, 10, 255))
    embed_out = os.path.join(out_dir, "tile_embed.png")
    embed_brain = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/tile_embed.png"
    
    embed_tile.save(embed_out, "PNG")
    embed_tile.save(embed_brain, "PNG")
    print("Embed BG liso guardado en:", embed_out)

if __name__ == "__main__":
    generate_panoramic_wallpaper()
