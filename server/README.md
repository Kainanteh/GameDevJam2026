# Servidor de Clasificaciones Globales (PHP) 🌐

Este directorio contiene el backend listo para desplegar en tu VPS y alojar la tabla de clasificaciones globales del juego de forma compartida.

---

## 🚀 Despliegue en 2 Pasos (Súper Sencillo)

Como hemos escrito el backend en **PHP**, el despliegue en tu VPS es instantáneo. No necesitas configurar demonios (`pm2`), instalar paquetes Node (`npm`) ni abrir puertos personalizados. Tu servidor Apache o Nginx existente se encargará de todo.

### Paso 1: Sube el archivo a tu VPS
Copia el archivo `leaderboard.php` a la carpeta pública de tu servidor web en tu VPS.
*   **Apache/Nginx Común:** `/var/www/html/`
*   Puedes subirlo usando **SFTP, SCP o rsync**. Por ejemplo, desde tu terminal local:
    ```bash
    scp server/leaderboard.php usuario@tu_vps_ip:/var/www/html/
    ```

### Paso 2: Configura los permisos de escritura
Para que el script pueda guardar las puntuaciones en el archivo `scores.json` de forma segura, el servidor web necesita permisos de escritura en ese directorio. Ejecuta esto en la terminal de tu VPS:
```bash
# Otorgar al usuario del servidor web (generalmente www-data o nginx) la propiedad del directorio
sudo chown -R www-data:www-data /var/www/html/

# Asegurar que el servidor pueda escribir en esa carpeta
sudo chmod 775 /var/www/html/
```

---

## 🔒 Seguridad e Integridad

*   **Filtro Anti-Spam (`X-Game-Key`):** El backend exige que cada petición `POST` de registro incluya la cabecera HTTP `X-Game-Key: crux-noctis-2026-key` enviada de forma nativa por el juego. Si no coincide, devuelve un error `403 Forbidden`, evitando registros automatizados de bots.
*   **Sanitización de Datos:** Los nombres se limpian de etiquetas HTML y se recortan automáticamente a un máximo de **12 caracteres** en el servidor para evitar deformaciones visuales de la interfaz en los clientes.
*   **Persistencia Segura:** Las puntuaciones se guardan ordenadas en un archivo `scores.json` en el mismo directorio. Puedes hacer una copia de seguridad descargando este archivo en cualquier momento.

---

## 🧹 Cómo Limpiar/Reiniciar la Tabla de Clasificaciones

Cuando vayas a publicar el juego oficialmente para el Game Jam, querrás borrar los registros de prueba. Tienes dos maneras muy sencillas de hacerlo:

### Método 1: Desde tu Navegador Web (Recomendado y Seguro)
Simplemente visita esta URL secreta en tu navegador web. El script verificará la clave secreta del juego y borrará todas las puntuaciones de forma instantánea:
```text
https://kainanteh.es/gamedevjam2026/leaderboard.php?clear=true&key=crux-noctis-2026-key
```

### Método 2: Desde la Terminal de tu VPS
Si prefieres hacerlo por consola, simplemente conéctate a tu VPS por SSH y elimina el archivo `scores.json` que contiene los datos:
```bash
rm /var/www/html/gamedevjam2026/scores.json
```
*(El backend de PHP volverá a crear la base de datos vacía automáticamente en cuanto se registre la primera nueva puntuación).*
