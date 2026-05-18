# Documento de Diseño de Juego (GDD): Camino Ancestral (Ancestral Path)

**Última Actualización:** Mayo 2026 (Versión Final de Compilación de la Jam)
**Tema:** Connection (GameDev.tv Jam 2026)
**Género:** Puzzle de Lógica / Conexión Rítmica (2D)
**Plataforma:** Web (HTML5) / PC (Godot Engine 4.6)

---

## 1. Visión General: El Ciclo del Legado
**Camino Ancestral** es un juego arcade/roguelike de conexión infinita y gestión de recursos donde el jugador guía la propagación de un árbol familiar generación tras generación.

Empezando con un retrato azul (Hombre) y un retrato rosa (Mujer), el jugador traza caminos de luz (raíces) sobre una cuadrícula bidimensional para que se conecten. Al unirse, la cámara se desplaza verticalmente, el linaje avanza y nace la siguiente generación, la cual debe usar los cimientos (e interceptar los peligros) de sus predecesores.

---

## 2. Mecánicas de Juego Reales (Fieles al Código)

### 2.1. Trazado y Gestión de Raíces
*   **Dibujar (Clic Izquierdo + Arrastrar):** El jugador extiende la raíz de luz de forma fluida por las celdas de la cuadrícula. Cada segmento de raíz trazado consume **Savia (Energía)**.
*   **Borrar/Retraer (Clic Derecho):** Hacer clic derecho sobre la punta activa de la raíz deshace el camino de forma proporcional, devolviendo la savia consumida para permitir rectificar rutas.
*   **Punta Dinámica de Búsqueda:** Cuando el jugador no está trazando activamente (`is_drawing == false`), la punta final de la raíz se orienta de forma orgánica y dinámica apuntando directamente hacia el cursor del ratón, imitando la búsqueda física de nutrientes.

### 2.2. Gestión de la Savia (Recursos)
*   **Consumo:** Cada paso por la cuadrícula cuesta savia. Si la savia se agota a 0 antes de realizar la unión, el juego termina.
*   **💚 Corazón Verde (+1):** Recarga básica de `+1` de savia al pasar la raíz sobre él.
*   **❤️ Corazón Rojo (+5):** Recargador premium de `+5` de savia. Al recogerlo, lanza una animación flotante y un pulso de escala neón gigante en el marcador de puntuación principal.

### 2.3. Control de Tiempo: El Reloj de Arena (⏳)
*   **Reloj de Arena (+⏳ SLOW!):** Recoger un reloj de arena ralentiza significativamente el desplazamiento automático de la cámara y del escenario.
*   **Sistema de Pilas (Stack x3):** Recoger múltiples relojes de forma consecutiva acumula pilas de tiempo de ralentización (hasta x3), extendiendo proporcionalmente la duración del efecto (6s para x1, 12s para x2, 18s para x3).
*   **Interfaz de Progreso Neon:** El estado se muestra mediante un indicador circular premium en la esquina superior izquierda que dibuja un arco de progreso neon de color violeta que se vacía en tiempo real y muestra el multiplicador activo (ej: `x2` o `x3`).

### 2.4. Obstáculos y Colisiones
*   **Bloques Grises del Escenario:** Celdas rocosas que bloquean físicamente el paso de las raíces, obligando a trazar rutas de evasión.
*   **Colisión de Caminos Ancestrales ($O(1)$ Hash Map):** Las raíces trazadas por las generaciones anteriores permanecen en el terreno como obstáculos infranqueables. Para garantizar un rendimiento óptimo de 60 FPS estables sin tirones, el juego utiliza una tabla hash (`_occupied_previous_points`) que comprueba la colisión de la nueva raíz contra miles de segmentos de generaciones previas en tiempo constante $O(1)$.

---

## 3. Dinámica Generacional y Progresión Infinita
*   **Crecimiento Vertical Infinito:** Cada unión exitosa desplaza la cámara y genera la nueva pareja en la parte inferior, haciendo del linaje una progresión infinita.
*   **Envejecimiento Dinámico a Calavera (Morphing):** A medida que la cámara avanza, los retratos de las parejas de generaciones previas pasan a ser "Ancestros inactivos". Para representarlo:
	*   El color de sus marcos neón se desvanece suavemente a un gris pétreo en 1.0 segundos.
	*   Al volverse grises, se inicia una transición continua de *morphing* por desintegración de bloques digitales retro (mediante un Shader dedicado de canvas) que transforma de forma orgánica los retratos humanos en calaveras (`res://assets/calavera.png`).
*   **Combo Arcade de Uniones:** Conectar generaciones de forma rápida y fluida incrementa un multiplicador neón arcade visible en la interfaz para potenciar la puntuación del jugador.

---

## 4. Estética y Estilo Visual: Neón en la Oscuridad
El juego adopta un diseño minimalista premium inspirado en el minimalismo de *Nidhogg*:

*   **Alto Contraste:** Fondos oscuros abisales (`#07060a`) que contrastan con los colores neón puro del juego: Hombre en azul eléctrico (`#00d2ff`), Mujer en rosa/fucsia vibrante (`#ff007f`) y raíces de savia en destellos dorados.
*   **Interfaz de Emojis Reemplazada por PNGs:** Toda la UI del juego prescinde de emojis de texto que puedan romperse en navegadores web. En su lugar, se cargan directamente los assets oficiales Twemoji de alta resolución en componentes `TextureRect` y `HBoxContainer`:
	*   `res://assets/icon_hourglass.png` (Relojes de arena e interfaz flotante `SLOW!`).
	*   `res://assets/icon_heart_red.png` (Notificación flotante `+5` de savia).
	*   `res://assets/icon_heart_green.png` (Notificación flotante `+1` de savia).
	*   `res://assets/flag_es.png` y `res://assets/flag_uk.png` (Banderas físicas de selección de idioma).

---

## 5. Banda Sonora y Sincronización Rítmica (Phonk)
La música y el sonido actúan como un elemento de juego interactivo en Camino Ancestral:

*   **Dark Gregorian Phonk:** Banda sonora mística de trap y cantos gregorianos (`res://assets/music.ogg`) transcodificada a formato nativo OGG Vorbis para garantizar reproducción y decodificación fluida en navegadores HTML5.
*   **Analizador de Espectro en Tiempo Real:** El juego cuenta con un bus de audio aislado (`"Music"`) que ejecuta un analizador de espectro dinámico (`AudioEffectSpectrumAnalyzer`). 
*   **Latidos Sincronizados:** En cada golpe de bajo (beat) de la música, el analizador de espectro de audio hace latir físicamente la escala de los retratos activos de los padres, los nutrientes del mapa y la cuadrícula en tiempo de ejecución, sumergiendo al jugador en un trance rítmico total.
*   **Desbloqueo de Audio Defensivo:** Para saltarse las políticas restrictivas de *Autoplay* de los navegadores web modernos (Chrome, Safari, Firefox), el juego desmutea y activa explícitamente los buses de sonido al primer clic de idioma del jugador.

---

## 6. Conectividad y Tablas de Clasificación Online
*   **Leaderboard Online:** El juego integra un sistema de comunicación HTTP con un VPS propio del desarrollador, permitiendo registrar la puntuación y el linaje de los jugadores y mostrar en pantalla una tabla de clasificación global en tiempo real competitiva.
