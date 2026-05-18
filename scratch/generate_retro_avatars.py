import os
from PIL import Image

def create_knight():
    # 16x16 Knight head sprite
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    pixels = img.load()
    
    # Colors
    O = (0, 0, 0, 255)       # Outline
    S = (100, 110, 120, 255) # Steel
    L = (140, 150, 160, 255) # Light Steel
    G = (229, 178, 37, 255)  # Gold trim
    E = (0, 220, 255, 255)   # Cyan eye glow
    
    sprite = [
        "....OOOOOO......",
        "...OSSSSSSO.....",
        "..OSSSLLSSSO....",
        ".OSSSLLLLSSSO...",
        "OSSSLLLLLLSSSO..",
        "OGGGGGGGGGGGGO..",
        "OGOOOOOOOOOOGO..",
        "OGOEEOOOOEEOOGO.",
        "OSOOOOOOOOOOSO.",
        "OSSSOOOOOOOSSSO.",
        ".OSSSSSSSSSSSO..",
        "..OSSSSSSSSSO...",
        "...OSSSSSSSO....",
        "....OOOOOOO.....",
        "................",
        "................"
    ]
    
    for y, row in enumerate(sprite):
        for x, char in enumerate(row):
            if char == 'O': pixels[x, y] = O
            elif char == 'S': pixels[x, y] = S
            elif char == 'L': pixels[x, y] = L
            elif char == 'G': pixels[x, y] = G
            elif char == 'E': pixels[x, y] = E
            
    return img

def create_mage():
    # 16x16 Mage head sprite
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    pixels = img.load()
    
    # Colors
    O = (0, 0, 0, 255)       # Outline
    P = (90, 40, 130, 255)   # Purple robe/hat
    L = (130, 70, 180, 255)  # Light Purple
    G = (229, 178, 37, 255)  # Gold gem/trim
    E = (255, 0, 128, 255)   # Glowing pink eyes
    S = (20, 20, 20, 255)    # Shadowed face
    
    sprite = [
        "......OO........",
        ".....OPO........",
        "....OPPPO.......",
        "...OPLLPO.......",
        "...OPLLPO.......",
        "..OPLLLLPO......",
        ".OPPLLLLPPO.....",
        "OPPGGGGGPPO.....",
        "OPOSSSSSSOPO....",
        "OOSSEESSEESOO...",
        ".OSSSSSSSSO.....",
        ".OPSSSSSSPO.....",
        "..OPPPPPO.......",
        "...OOOOO........",
        "................",
        "................"
    ]
    
    for y, row in enumerate(sprite):
        for x, char in enumerate(row):
            if char == 'O': pixels[x, y] = O
            elif char == 'P': pixels[x, y] = P
            elif char == 'L': pixels[x, y] = L
            elif char == 'G': pixels[x, y] = G
            elif char == 'E': pixels[x, y] = E
            elif char == 'S': pixels[x, y] = S
            
    return img

def create_rogue():
    # 16x16 Rogue head sprite
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    pixels = img.load()
    
    # Colors
    O = (0, 0, 0, 255)       # Outline
    H = (30, 85, 45, 255)    # Hood Green
    L = (50, 120, 70, 255)   # Light Green
    M = (70, 60, 50, 255)    # Leather Mask
    E = (229, 178, 37, 255)  # Gold/amber eyes
    
    sprite = [
        "....OOOOOO......",
        "...OHHHHHHO.....",
        "..OHHLLLLHHO....",
        ".OHLLLLLLLLHO...",
        "OHLLLLLLLLLLHO..",
        "OHLLOOOOOOLLHO..",
        "OHLOOEEEEOOLHO..",
        "OHLOMMMMMMOLHO..",
        "OHOMMMMMMMMOHO..",
        ".OMMMMMMMMMMO...",
        ".OMMMMMMMMMMO...",
        "..OMMMMMMMMO....",
        "...OHHHHHHO.....",
        "....OOOOOO......",
        "................",
        "................"
    ]
    
    for y, row in enumerate(sprite):
        for x, char in enumerate(row):
            if char == 'O': pixels[x, y] = O
            elif char == 'H': pixels[x, y] = H
            elif char == 'L': pixels[x, y] = L
            elif char == 'M': pixels[x, y] = M
            elif char == 'E': pixels[x, y] = E
            
    return img

def create_king():
    # 16x16 King head sprite
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    pixels = img.load()
    
    # Colors
    O = (0, 0, 0, 255)       # Outline
    G = (229, 178, 37, 255)  # Gold Crown
    R = (220, 30, 30, 255)   # Ruby Gem
    B = (220, 220, 220, 255) # Silver hair/beard
    F = (235, 175, 135, 255) # Face skin
    S = (40, 40, 40, 255)    # Shadow/Eyes
    
    sprite = [
        "...O.O.O.O......",
        "..OGOGOGOGO.....",
        ".OGOROGOROGO....",
        "OGGGGGGGGGGGO...",
        "OGGGGGGGGGGGO...",
        ".OSFSSFSSSO.....",
        "OSFFFFFFFFSO....",
        "OSFFFFFFFFSO....",
        "OSBBBBBBBBBS....",
        ".OBBBBBBBBBO....",
        "..OBBBBBBBO.....",
        "...OBBBBBO......",
        "....OOOOO.......",
        "................",
        "................",
        "................"
    ]
    
    for y, row in enumerate(sprite):
        for x, char in enumerate(row):
            if char == 'O': pixels[x, y] = O
            elif char == 'G': pixels[x, y] = G
            elif char == 'R': pixels[x, y] = R
            elif char == 'B': pixels[x, y] = B
            elif char == 'F': pixels[x, y] = F
            elif char == 'S': pixels[x, y] = S
            
    return img

def create_skeleton():
    # 16x16 Skeleton skull sprite
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    pixels = img.load()
    
    # Colors
    O = (0, 0, 0, 255)       # Outline
    W = (235, 230, 215, 255) # Bone White
    S = (180, 170, 155, 255) # Shaded Bone
    E = (220, 30, 30, 255)   # Red pinprick eye glow
    
    sprite = [
        "....OOOOOO......",
        "...OWWWWWWO.....",
        "..OWWWWWWWWO....",
        ".OWWWOOOWWWOO...",
        "OWWWOEOOOWEOOW..",
        "OWWWWWWWWWWWOW..",
        "OSSSWWWWWWSSSW..",
        ".OSSSSWWSSSSW...",
        "..OSSOOOSSOO....",
        "...OSSSSSSO.....",
        "....OOOOOO......",
        "................",
        "................",
        "................",
        "................",
        "................"
    ]
    
    for y, row in enumerate(sprite):
        for x, char in enumerate(row):
            if char == 'O': pixels[x, y] = O
            elif char == 'W': pixels[x, y] = W
            elif char == 'S': pixels[x, y] = S
            elif char == 'E': pixels[x, y] = E
            
    return img

def save_upscaled(img, filepath, size=64):
    # Upscale using Nearest Neighbor to keep retro grid crisp
    upscaled = img.resize((size, size), Image.NEAREST)
    upscaled.save(filepath)
    print(f"Generated {filepath} successfully.")

os.makedirs("assets", exist_ok=True)
save_upscaled(create_knight(), "assets/avatar_knight.png")
save_upscaled(create_mage(), "assets/avatar_mage.png")
save_upscaled(create_rogue(), "assets/avatar_rogue.png")
save_upscaled(create_king(), "assets/avatar_king.png")
save_upscaled(create_skeleton(), "assets/avatar_skeleton.png")
