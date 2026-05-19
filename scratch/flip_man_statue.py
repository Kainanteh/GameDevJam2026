from PIL import Image

def flip_image(path):
    im = Image.open(path)
    flipped = im.transpose(Image.FLIP_LEFT_RIGHT)
    flipped.save(path)
    print(f"Flipped {path} horizontally.")

flip_image("assets/estatuaHombre.png")
