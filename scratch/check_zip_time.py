import os
import time

def check_file_times():
    gd_path = "/home/kainanteh/game-dev-jam-2026/Main.gd"
    zip_path = "/home/kainanteh/game-dev-jam-2026/game-dev-jam-web.zip"
    
    if os.path.exists(gd_path):
        gd_mtime = os.path.getmtime(gd_path)
        print(f"Main.gd - Última modificación: {time.ctime(gd_mtime)}")
    else:
        print("Error: Main.gd no existe.")
        
    if os.path.exists(zip_path):
        zip_mtime = os.path.getmtime(zip_path)
        print(f"game-dev-jam-web.zip - Última modificación: {time.ctime(zip_mtime)}")
        
        # Comparación
        if gd_mtime > zip_mtime:
            print("\n¡ALERTA! El archivo de código Main.gd es MÁS NUEVO que el zip compilado.")
            print("Esto significa que el build web actual NO contiene tus últimos cambios de código y hay que compilarlo de nuevo.")
        else:
            print("\nEl zip compilado es más nuevo o igual que el código.")
    else:
        print("Error: game-dev-jam-web.zip no existe.")

if __name__ == "__main__":
    check_file_times()
