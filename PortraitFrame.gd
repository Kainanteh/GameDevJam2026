extends Control

# Cargar las siluetas de forma dinámica en ejecución
const HOMBRE_TEX = "res://assets/hombre.png"
const MUJER_TEX = "res://assets/mujer.png"

# Propiedad de color expuesta para compatibilidad total con Main.gd y Tweens
@export var color: Color = Color.WHITE:
	set(val):
		color = val
		if _character_mat:
			_character_mat.set_shader_parameter("tint_color", color)
		if _border_node:
			_border_node.queue_redraw()

@export var border_width: float = 4.0

# Escala de la silueta dentro del marco (puedes aumentarla o reducirla desde el Inspector)
@export var sprite_scale: float = 1.3

# Desplazamiento vertical del sprite (positivo para bajarlo, negativo para subirlo)
@export var sprite_y_offset: float = 12.0

# Configuración de los compases de la música (BPM) para el cabeceo sincronizado
@export var bpm: float = 120.0

# Define si este retrato está activo o "apagado" (los apagados no respiran ni cabecean)
@export var active: bool = true:
	set(val):
		active = val
		# Transición suave a gris al desactivarse para denotar inactividad histórica
		if not active:
			if is_inside_tree():
				var tween = create_tween()
				tween.tween_property(self, "color", Color(0.3, 0.3, 0.3, 1.0), 1.2).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
			else:
				color = Color(0.3, 0.3, 0.3, 1.0)

# Nodos hijos internos
var _bg_rect: ColorRect
var _character_sprite: TextureRect
var _character_mat: ShaderMaterial
var _border_node: Control

# Variables de control para las animaciones
var breathing_time: float = 0.0
var bob_offset: float = 0.0
var last_beat_index: int = 0
var beat_scale: float = 1.0

func _ready() -> void:
	# Desfasar el tiempo de respiración inicial para evitar bloques robóticos
	breathing_time = randf() * 10.0
	
	# Si predomina el azul (hombre), compensamos que su silueta sea de menor tamaño relativo
	# y tenga más aire abajo, aumentando su escala a 1.55 y su offset vertical a 26.0
	if color.b > color.r and sprite_scale == 1.3:
		sprite_scale = 1.55
		sprite_y_offset = 26.0
	
	# 1. Instanciar Fondo Rectangular Sólido (Capa inferior)
	# Oculta todas las raíces que pasan por detrás del retrato
	_bg_rect = ColorRect.new()
	_bg_rect.name = "BackgroundMask"
	_bg_rect.color = Color(0.05, 0.05, 0.05, 1) # Color exacto del fondo del canvas
	_bg_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_bg_rect.pivot_offset = size / 2.0 # Pivot centrado para que escale al unísono con el marco
	add_child(_bg_rect)
	
	# 2. Instanciar Sprite del Personaje (Capa intermedia)
	_character_sprite = TextureRect.new()
	_character_sprite.name = "CharacterSprite"
	_character_sprite.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_character_sprite.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	
	# SHADER: Reemplaza cualquier color del archivo por el color puro de modulación
	# Esto permite pintar una silueta rosa de color azul brillante sin mezclar colores oscuros!
	var shader = Shader.new()
	shader.code = """
	shader_type canvas_item;
	uniform vec4 tint_color : source_color;
	void fragment() {
		vec4 tex_color = texture(TEXTURE, UV);
		COLOR = vec4(tint_color.rgb, tex_color.a * tint_color.a);
	}
	"""
	_character_mat = ShaderMaterial.new()
	_character_mat.shader = shader
	_character_mat.set_shader_parameter("tint_color", color)
	_character_sprite.material = _character_mat
	add_child(_character_sprite)
	
	# 3. Instanciar Control del Borde (Capa superior)
	# Dibuja los bordes neón por encima del personaje para dar efecto de marco profundo
	_border_node = Control.new()
	_border_node.name = "BorderOverlay"
	_border_node.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_border_node.draw.connect(_draw_borders)
	_border_node.pivot_offset = size / 2.0 # Pivot centrado para que escale desde el medio
	add_child(_border_node)
	
	_update_texture()

func _process(delta: float) -> void:
	if active:
		breathing_time += delta
		
	# Actualizar animaciones y proporciones sobre el nodo de textura
	var tex = _character_sprite.texture
	if not tex:
		_update_texture()
		tex = _character_sprite.texture
		
	if tex:
		# Margen de 2 píxeles para encajar perfectamente con el borde interior (borde de 4px)
		var margin = 2.0
		var orig_width = size.x - margin * 2.0
		var orig_height = size.y - margin * 2.0
		
		# Proporción original de aspecto para que no se estire
		var tex_size = tex.get_size()
		var aspect = tex_size.x / tex_size.y
		
		var char_width = orig_width
		var char_height = orig_height
		
		if aspect > 1.0:
			char_height = orig_width / aspect
		else:
			char_width = orig_height * aspect
			
		# Aplicar la escala personalizada del sprite para hacerlo más grande
		char_width *= sprite_scale
		char_height *= sprite_scale
			
		# Animación de respiración muy sutil y lenta (solo si está activo)
		var b_scale = 1.0
		if active:
			b_scale = 1.0 + sin(breathing_time * 1.5) * 0.008
		char_height *= b_scale
		
		# Centrado horizontal y anclaje al suelo con el cabeceo vertical y el desplazamiento aplicados
		var char_x = margin + (orig_width - char_width) / 2.0
		var char_y = margin + (orig_height - char_height) + bob_offset + sprite_y_offset
		
		_character_sprite.position = Vector2(char_x, char_y)
		_character_sprite.size = Vector2(char_width, char_height)
		
	# Aplicar el pulso de compás de escala al marco neón exterior y a su máscara de fondo negro
	if _border_node:
		_border_node.scale = Vector2.ONE * beat_scale
	if _bg_rect:
		_bg_rect.scale = Vector2.ONE * beat_scale

# Carga la textura correspondiente de forma segura
func _update_texture() -> void:
	if not _character_sprite:
		return
		
	var path = MUJER_TEX if color.r > color.b else HOMBRE_TEX
	if ResourceLoader.exists(path):
		var tex = load(path) as Texture2D
		if _character_sprite.texture != tex:
			_character_sprite.texture = tex

# Disparador del cabeceo (golpe de ritmo)
func trigger_beat_bob() -> void:
	beat_scale = 1.08 # Crece un 8% (todos los marcos pulsan en unísono)
	
	# Pero el cabeceo vertical interno de la silueta solo ocurre si está activo (los ancestros quedan congelados)
	if active:
		bob_offset = 12.0 # Desplazamiento hacia abajo (exagerado)
	else:
		bob_offset = 0.0
	
	var tween = create_tween()
	tween.set_parallel(true)
	tween.tween_property(self, "beat_scale", 1.0, 0.25).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	if active:
		tween.tween_property(self, "bob_offset", 0.0, 0.25).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)

# Función de dibujo para la capa superior (bordes y esquinas arcade)
func _draw_borders() -> void:
	var rect = Rect2(Vector2.ZERO, size)
	
	# Borde del contorno
	_border_node.draw_rect(rect, color, false, border_width)
	
	# Esquinas arcade retro neón
	var corner_len = 12.0
	var accent_color = color.lightened(0.2)
	
	# Esquina Superior Izquierda
	_border_node.draw_line(Vector2(0, 0), Vector2(corner_len, 0), accent_color, border_width)
	_border_node.draw_line(Vector2(0, 0), Vector2(0, corner_len), accent_color, border_width)
	
	# Esquina Superior Derecha
	_border_node.draw_line(Vector2(size.x, 0), Vector2(size.x - corner_len, 0), accent_color, border_width)
	_border_node.draw_line(Vector2(size.x, 0), Vector2(size.x, corner_len), accent_color, border_width)
	
	# Esquina Inferior Izquierda
	_border_node.draw_line(Vector2(0, size.y), Vector2(corner_len, size.y), accent_color, border_width)
	_border_node.draw_line(Vector2(0, size.y), Vector2(0, size.y - corner_len), accent_color, border_width)
	
	# Esquina Inferior Derecha
	_border_node.draw_line(Vector2(size.x, size.y), Vector2(size.x - corner_len, size.y), accent_color, border_width)
	_border_node.draw_line(Vector2(size.x, size.y), Vector2(size.x, size.y - corner_len), accent_color, border_width)
