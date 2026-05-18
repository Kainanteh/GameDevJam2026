import urllib.request
import os

emojis = {
    "icon_mouse.png": "https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/1f5b1.png",
    "icon_heart_green.png": "https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/1f49a.png",
    "icon_heart_red.png": "https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/2764.png",
    "icon_hourglass.png": "https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/23f3.png",
    "icon_arrow_yellow.png": "https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/1f449.png"
}

headers = {'User-Agent': 'Mozilla/5.0'}

for filename, url in emojis.items():
    dest = os.path.join("assets", filename)
    print(f"Downloading {url} to {dest}...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            with open(dest, 'wb') as out_file:
                out_file.write(response.read())
        print(f"Successfully downloaded {filename}")
    except Exception as e:
        print(f"Failed to download {filename}: {e}")
