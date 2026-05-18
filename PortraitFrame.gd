extends Control

# Cargar las siluetas de forma dinámica en ejecución
const HOMBRE_TEX = "res://assets/hombre.png"
const MUJER_TEX = "res://assets/mujer.png"

# Propiedad de color expuesta para compatibilidad total con Main.gd y Tweens
@export var color: Color = Color.WHITE:
	set(val):
		color = val
		
		# Ajustar dinámicamente la escala y offset de la silueta según el color (género)
		if color.b > color.r:
			sprite_scale = 1.55
			sprite_y_offset = 26.0
		else:
			sprite_scale = 1.3
			sprite_y_offset = 12.0
			
		if _character_mat:
			_character_mat.set_shader_parameter("tint_color", color)
		if _border_node:
			_border_node.queue_redraw()
		_update_texture()

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
		var was_active = active
		active = val
		if not active:
			if was_active and is_inside_tree():
				_transition_to_skull()
			else:
				color = Color(0.3, 0.3, 0.3, 1.0)
				_is_skull = true
				_is_skull_and_bobs = true
				_anim_sprite_scale = 1.0
				_anim_sprite_scale_x = 1.0
				_morph_scale = 1.0
				_morph_offset = 1.0
				_update_texture()
				if _character_mat:
					_character_mat.set_shader_parameter("tint_color", Color(0.3, 0.3, 0.3, 1.0))
					_character_mat.set_shader_parameter("morph_weight", 1.0)
		else:
			# Si se vuelve a activar (por ejemplo al reiniciar o regenerar)
			_is_skull = false
			_is_skull_and_bobs = false
			_anim_sprite_scale = 1.0
			_anim_sprite_scale_x = 1.0
			_morph_scale = 0.0
			_morph_offset = 0.0
			_update_texture()
			if _character_mat:
				_character_mat.set_shader_parameter("tint_color", color)
				_character_mat.set_shader_parameter("morph_weight", 0.0)

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

# ✅ NUEVO: Controladores de la animación de conversión a calavera
var _is_skull: bool = false
var _is_skull_and_bobs: bool = false
var _anim_sprite_scale: float = 1.0
var _anim_sprite_scale_x: float = 1.0
var _morph_scale: float = 0.0
var _morph_offset: float = 0.0

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
	
	# SHADER: Realiza una transformación física por desintegración de bloques retro 48x48
	# y distorsión de glitch horizontal electromagnética en lugar de un fundido simple.
	var shader = Shader.new()
	shader.code = """
	shader_type canvas_item;
	uniform vec4 tint_color : source_color;
	uniform sampler2D skull_texture : filter_nearest;
	uniform float morph_weight : hint_range(0.0, 1.0) = 0.0;
	
	float hash(vec2 p) {
		p = fract(p * vec2(123.34, 456.21));
		p += dot(p, p + 45.32);
		return fract(p.x * p.y);
	}
	
	void fragment() {
		// 1. Interferencia/Glitch horizontal en el punto medio del morph
		float glitch_factor = sin(morph_weight * 3.14159);
		float glitch_noise = hash(vec2(floor(UV.y * 32.0), morph_weight));
		float horizontal_offset = 0.0;
		if (glitch_noise < glitch_factor * 0.35) {
			horizontal_offset = (hash(vec2(morph_weight, UV.y)) - 0.5) * 0.06 * glitch_factor;
		}
		
		vec2 glitched_uv = vec2(UV.x + horizontal_offset, UV.y);
		
		// 2. Leer las dos siluetas con el glitch aplicado
		vec4 base_color = texture(TEXTURE, glitched_uv);
		vec4 target_color = texture(skull_texture, glitched_uv);
		
		// 3. Desintegración digital por bloques retro de 48x48
		float block_noise = hash(floor(glitched_uv * 48.0));
		
		// El bloque se transforma al instante (cero difuminado) de humano a calavera según el umbral
		vec4 final_tex_color = base_color;
		if (block_noise < morph_weight) {
			final_tex_color = target_color;
		}
		
		COLOR = vec4(tint_color.rgb, final_tex_color.a * tint_color.a);
	}
	"""
	_character_mat = ShaderMaterial.new()
	_character_mat.shader = shader
	_character_mat.set_shader_parameter("tint_color", color)
	_character_mat.set_shader_parameter("morph_weight", 0.0)
	
	# Cargar la textura de la calavera de forma estática en el shader
	var skull_tex = load("res://assets/calavera.png") as Texture2D
	_character_mat.set_shader_parameter("skull_texture", skull_tex)
	
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
			
		# ✅ Interpolar suavemente de forma continua el tamaño y offset del personaje al estándar de la calavera
		var target_scale = 1.3
		var target_offset = 12.0
		
		var active_scale = lerp(sprite_scale, target_scale, _morph_scale)
		var active_y_offset = lerp(sprite_y_offset, target_offset, _morph_offset)

		# Aplicar la escala de la silueta y multiplicador general
		char_width *= active_scale * _anim_sprite_scale
		char_height *= active_scale * _anim_sprite_scale
			
		# Animación de respiración muy sutil y lenta (solo si está activo)
		var b_scale = 1.0
		if active:
			b_scale = 1.0 + sin(breathing_time * 1.5) * 0.008
		char_height *= b_scale
		
		# Centrado horizontal y anclaje al suelo con el cabeceo vertical y el desplazamiento aplicados
		var char_x = margin + (orig_width - char_width) / 2.0
		var char_y = margin + (orig_height - char_height) + bob_offset + active_y_offset
		
		_character_sprite.position = Vector2(char_x, char_y)
		_character_sprite.size = Vector2(char_width, char_height)
		
	# Aplicar el pulso de compás de escala al marco neón exterior y a su máscara de fondo negro
	if _border_node:
		_border_node.scale = Vector2.ONE * beat_scale
	if _bg_rect:
		_bg_rect.scale = Vector2.ONE * beat_scale

# Carga la textura correspondiente de forma segura (soporta la calavera de desactivación)
func _update_texture() -> void:
	if not _character_sprite:
		return
		
	var path = "res://assets/calavera.png" if _is_skull else (MUJER_TEX if color.r > color.b else HOMBRE_TEX)
	var tex = load(path) as Texture2D
	if tex != null:
		if _character_sprite.texture != tex:
			_character_sprite.texture = tex

# Disparador del cabeceo (golpe de ritmo)
func trigger_beat_bob() -> void:
	beat_scale = 1.08 # Crece un 8% (todos los marcos pulsan en unísono)
	
	# El cabeceo vertical interno ocurre si está activo o si ya es calavera animada (beat continuado)
	if active or _is_skull_and_bobs:
		bob_offset = 12.0 # Desplazamiento hacia abajo
	else:
		bob_offset = 0.0
	
	var tween = create_tween()
	tween.set_parallel(true)
	tween.tween_property(self, "beat_scale", 1.0, 0.25).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	if active or _is_skull_and_bobs:
		tween.tween_property(self, "bob_offset", 0.0, 0.25).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)

# ✅ NUEVO: Animación premium de Morphing y Cross-Dissolve directo
func _transition_to_skull() -> void:
	# 1. Transición suave del color general del marco a gris (1.0 segundos)
	var color_tween = create_tween()
	color_tween.tween_property(self, "color", Color(0.3, 0.3, 0.3, 1.0), 1.0).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	
	# 2. Al terminar la transición a gris, hacemos el morphing directo (cross-dissolve)
	color_tween.tween_callback(func():
		var morph_tween = create_tween()
		morph_tween.set_parallel(true)
		
		# Mezclar las dos texturas de forma continua y directa (morph_weight en shader: de 0.0 a 1.0)
		morph_tween.tween_method(func(val: float):
			if _character_mat:
				_character_mat.set_shader_parameter("morph_weight", val)
		, 0.0, 1.0, 0.75).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		
		# Interpolar el tamaño suavemente al estándar de la calavera en paralelo
		morph_tween.tween_property(self, "_morph_scale", 1.0, 0.75).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		
		# Interpolar el offset vertical suavemente en paralelo
		morph_tween.tween_property(self, "_morph_offset", 1.0, 0.75).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		
		# Al completarse el morph por completo, activamos el cabeceo al ritmo (beat bobbing)
		morph_tween.chain().tween_callback(func():
			_is_skull = true
			_is_skull_and_bobs = true
		)
	)

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
