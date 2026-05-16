# Documento de Diseño de Juego (GDD): Camino Ancestral (Ancestral Path)

**Tema:** Connection (GameDev.tv Jam 2026)
**Género:** Puzzle de Lógica / Conexión (2D)
**Plataforma:** Web / PC (Godot Engine)

## 1. Visión General: El Ciclo de la Vida
El juego trata sobre la creación y expansión de un linaje a través de la conexión. Empezando con dos retratos (Hombre y Mujer), el jugador debe guiar sus raíces para que se encuentren y den vida a una nueva generación. El juego progresa verticalmente, donde el éxito de una generación se convierte en la base (y a veces el obstáculo) de la siguiente.

## 2. Mecánica Principal: El Desafío Lógico de la Raíz
El núcleo del juego es un puzzle de navegación, optimización de recursos y toma de decisiones en tiempo real.

### 2.1. Gestión de la Savia (Energía)
*   **Origen:** Cada pareja de retratos (Padre y Madre) comienza con una reserva base de Savia.
*   **Consumo:** Extender la raíz por el escenario consume Savia de forma constante. Cada centímetro cuenta.
*   **Recolección:** El jugador puede recargar Savia pasando por **Nodos de Nutrientes** (frutos/semillas) distribuidos por el mapa.
*   **Dilema Lógico:** El jugador debe decidir si tomar la ruta más corta o desviarse para recoger nutrientes que aseguren la longevidad del linaje.

### 2.2. Obstáculos y Peligros Dinámicos
El escenario no es estático; el jugador debe reaccionar a amenazas en tiempo real:
*   **La Plaga (Blight):** Nubes de esporas oscuras que se mueven por el mapa. Tocarlas drena la Savia rápidamente.
*   **Raíces Parásitas:** Amenazas que intentan interceptar la raíz del jugador, obligando a maniobras de evasión.
*   **Terreno Cambiante:** Rocas que se desplazan o grietas que se abren, alterando los caminos disponibles durante el trazado.

### 2.3. La Unión y el Legado
*   Cuando las dos raíces se encuentran, ocurre una fusión visual y nace un **nuevo retrato (hijo)** en el punto de encuentro exacto.

## 3. Dinámica de Múltiples Hijos y Generaciones
*   **Crecimiento Vertical:** A medida que nacen nuevos hijos, la cámara se desplaza, dejando a los padres arriba.
*   **Herencia Escénica:** Las raíces de las generaciones anteriores permanecen en el suelo, convirtiéndose en obstáculos físicos o guías estructurales para los nuevos puzzles.
*   **Gestión de Espacio:** En niveles con múltiples hijos, el jugador debe gestionar varias raíces simultáneamente, evitando que se crucen o bloqueen, creando una red compleja de conexiones familiares.
*   **Evolución de Rasgos:** Los nodos de nutrientes recogidos por los padres otorgan rasgos especiales a los hijos, permitiéndoles superar obstáculos específicos en niveles futuros (ej: raíces de fuego para quemar hielo).

## 4. Final y Ciclo de Juego: El Linaje Eterno
*   **Naturaleza:** El juego es de tipo **infinito (Arcade/Roguelike)**. No tiene un final definitivo, sino que el objetivo es ver cuántas generaciones puede sostener el jugador antes de que el linaje se extinga.
*   **Condición de Derrota:** El juego termina si el jugador se queda sin "Savia" para realizar una conexión o si los obstáculos ambientales impiden que los descendientes encuentren pareja.
*   **Renacimiento:** Al morir el árbol, las semillas se dispersan, permitiendo empezar un nuevo linaje (posiblemente con mejoras acumuladas).

## 5. Sistema de Puntuación y Ranking (Online)
*   **Puntuación:** Se basa principalmente en el **Número de Generaciones** alcanzadas.
*   **Multiplicadores:** Se obtienen puntos extra por la "Pureza" del linaje, el tiempo de resolución de cada puzzle y la cantidad de miembros de la familia despertados.
*   **Conectividad:** Gracias al uso de un VPS propio, el juego contará con una **Tabla de Clasificación (Leaderboard)** global donde los jugadores podrán comparar la longevidad de sus árboles genealógicos.

## 6. Estética y Estilo Visual: El "Brillo en la Oscuridad"
Inspirado directamente por la estética de **Nidhogg (2014)**, el juego adoptará un estilo **Lo-Fi / Minimalista** de alto impacto visual.

*   **Minimalismo Extremo (Pixel Art Lo-Fi):** Los personajes no tendrán rostros detallados ni texturas complejas. Serán siluetas vibrantes y minimalistas (estilo Atari 2600 moderno). Esto permite que el jugador se centre en la fluidez del movimiento y en la red de conexiones.
*   **Contraste y Color:**
    *   **Fondos:** Serán oscuros, profundos o con patrones psicodélicos muy sutiles para generar atmósfera.
    *   **Retratos:** Serán bloques de color sólido neón (ej: Hombre en azul eléctrico, Mujer en rosa vibrante).
    *   **Savia/Raíces:** Líneas de luz pura (dorado/amarillo neón) que contrastan fuertemente con el fondo.
*   **El "Rastro del Linaje":** Al igual que la sangre en Nidhogg, las raíces que el jugador extienda dejarán una **mancha de luz persistente**. Al final de muchas generaciones, el fondo oscuro estará "pintado" por los caminos que tomaron los ancestros, creando una obra de arte generativa única en cada partida.
*   **Animación Fluida:** A pesar de la baja resolución de los sprites, las animaciones de las raíces al crecer y de los retratos al "fusionarse" serán extremadamente fluidas, dando una sensación orgánica y viva.
*   **Envejecimiento Dinámico:** A medida que el linaje avanza y los retratos quedan en la parte superior de la pantalla (pasando a ser ancestros), estos deben "envejecer" visualmente.
    *   **Efecto:** Se simulará el paso del tiempo mediante la aparición de líneas sutiles (oscuras o claras según el color base) que cruzan los rostros, representando arrugas o las vetas de la madera vieja. Esto refuerza la idea de que los cimientos del árbol son antiguos y sabios.
*   **Monumentos de la Historia:** A medida que la cámara se desplaza hacia abajo con las nuevas generaciones, aparecerán en los márgenes laterales (izquierda y derecha) **estatuas de estilo griego y romano** (hombres y mujeres de piedra).
    *   **Propósito:** Estos monumentos llevarán grabados **mensajes narrativos o de ánimo** que invitan al jugador a seguir profundizando en el linaje. Representan la "memoria de piedra" de la humanidad, dando una sensación de escala épica y trascendencia al progreso del jugador.
*   **Ventaja de Producción:** Este estilo permite generar assets rápidamente durante la Jam, priorizando el "feeling" y la jugabilidad sobre el pulido gráfico tradicional.

## 7. Audio y Música: Atmósfera "Dark Gregorian Phonk"
Inspirada en el estilo **Dark Gregorian Phonk** (ej: *Ave Maria | Dark Gregorian Phonk*), la banda sonora será una pieza fundamental para sumergir al jugador en el trance y la tensión de mantener vivo el árbol genealógico.

*   **Estilo:** **Dark Gregorian Phonk**. Una poderosa fusión de música coral sacra o cantos gregorianos con una agresiva producción moderna de phonk/trap. Bajos muy pesados (808s saturados), percusión trap contundente, sintetizadores oscuros y efectos de glitch.
*   **Atmósfera:** Oscura, mística, épica y profundamente dramática. Debe sentirse como un ritual sagrado antiguo colisionando con un ritmo frenético y pesado. La solemnidad melancólica de las voces corales contrasta perfectamente con la velocidad y urgencia puramente "Arcade" de conectar las raíces a tiempo.
*   **Efectos de Sonido (SFX):** 
    *   Percusiones secas y contundentes (estilo phonk cowbells o claps pesados) para marcar los ritmos de cada clic y confirmación de unión.
    *   Ecos de cánticos corales o voces sagradas distorsionadas que resuenan cuando la cámara desciende y nace una nueva generación.
    *   Sonidos de madera antigua crujiendo violentamente, acompañados de subgraves profundos, para la tensión de expandir o retraer rápidamente la raíz.

## 8. Lista de Assets (Tareas Pendientes)

### Visuales (Imágenes)
*   **Retratos Base:** Siluetas minimalistas en colores neón (Hombre, Mujer, Niño/Semilla).
*   **Segmentos de Raíz:** Diferentes formas (Recta, en L, en T, Cruce) con versión apagada y versión brillante.
*   **Nodos de Entorno:** Iconos para nutrientes (Fuerza, Sabiduría, etc.) y obstáculos (Rocas, Corrupción).
*   **Fondos:** Capas de fondos oscuros con grano o ruido para profundidad.
*   **Partículas:** Brillos para la "fusión" y el rastro de luz de las raíces.
*   **Monumentos:** Estatuas pixeladas de estilo griego/romano para los laterales.
*   **Interfaz (UI):** Contador de generaciones, barra de Savia (Energía) y botones de estilo retro.

### Audio (Sonidos)
*   **Música:** Bucle de atmósfera Witch House (Crystal Castles Style).
*   **SFX Rotación:** Crujido de madera seca.
*   **SFX Crecimiento:** Sonido de "siseo" o estática eléctrica al extender la raíz.
*   **SFX Conexión:** Acorde sintético triunfal y armónico al unir dos raíces.
*   **SFX Despertar:** Sonido de inhalación o latido cuando un retrato cobra vida.
*   **SFX Fallo/Muerte:** Distorsión súbita (Glitch) y silencio.
