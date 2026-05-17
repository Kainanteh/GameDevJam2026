extends Node2D


const PortraitFrame = preload("res://PortraitFrame.gd")

const GRID_SIZE = 32
const MAX_SAP = 150
const SAP_COST_PER_SEGMENT = 3

var sap = MAX_SAP
var current_path: PackedVector2Array = []
var is_drawing = false
var game_over = false
var generation = 1
var waiting_for_next = false
var camera_speed = 15.0 # Píxeles por segundo inicial
var all_previous_paths: Array[Vector2] = [] # Almacenar raíces antiguas para colisiones
var is_retracting = false # Flag para la marcha atrás
var last_beat_index = -1 # Índice para compás rítmico global

# Configuración del compás de música (Rhythm Engine)
@export var music_bpm: float = 120.0

# Variables para la sincronización híbrida por espectro de audio aislado
var _analyzer: AudioEffectSpectrumAnalyzerInstance
var _beat_cooldown: float = 0.0
var _last_magnitude: float = 0.0

@onready var root_line = $Roots/RootLine
@onready var sap_label = $UI/SapLabel
@onready var gen_label = $UI/GenerationLabel
@onready var message_label = $UI/MessageLabel
@onready var ancestor = $Ancestor
@onready var descendant = $Descendant
@onready var obstacles = $Obstacles
@onready var camera = $MainCamera
@onready var roots_container = $Roots

var rewards_container: Node
var _music_player: AudioStreamPlayer
var _generation_combo: Label
var _green_score_label: Label
var green_squares_collected: int = 0

var first_union_made = false
var _tutorial_timer = 0.0
var _tutorial_line: Line2D
var _tutorial_cursor: Label

var in_menu = true
var _menu_node: Control

# Configuración de la Tabla de Clasificaciones Global en tu VPS
const LEADERBOARD_API_URL = "https://kainanteh.es/gamedevjam2026/leaderboard.php"
const LEADERBOARD_API_KEY = "crux-noctis-2026-key"

var _leaderboard_panel: PanelContainer
var _leaderboard_back_btn: Button
var _classification_area: Control
var current_game_y_offset: float = 0.0
var leaderboard_entries: Array = []
var record_generation = 0
var current_language: String = "en"
var _lang_selector: HBoxContainer
var _es_flag_btn: Button
var _en_flag_btn: Button
var _menu_last_magnitude: float = 0.0
var _menu_beat_cooldown: float = 0.0
var _title_beat_pulse: float = 0.0
var _menu_average_delta: float = 0.0
var _title_font: SystemFont
var _battery_bar: Control
var _displayed_sap: float = 150.0
var _battery_beat_pulse: float = 0.0

func _ready():
	randomize()
	
	# Inicializar el indicador de combo de generación neón en la esquina superior derecha
	_setup_combo_ui()
	
	rewards_container = Node.new()
	rewards_container.name = "Rewards"
	add_child(rewards_container)
	
	# Redimensionar elementos iniciales para 3x3 celdas (retratos grandes)
	ancestor.size = Vector2(GRID_SIZE * 3, GRID_SIZE * 3)
	descendant.size = Vector2(GRID_SIZE * 3, GRID_SIZE * 3)
	
	# Asegurar que los retratos siempre se dibujen por encima de las raíces y estén ocultos en el menú
	ancestor.z_index = 10
	descendant.z_index = 10
	ancestor.hide()
	descendant.hide()
	
	# Forzar que el contenedor de raíces (roots_container) se dibuje al principio
	# de la jerarquía de Main (índice 2), quedando DETRÁS de todos los retratos y obstáculos
	move_child(roots_container, 2)
	
	# Inicializar elementos del tutorial visual si no se ha completado la primera unión
	_tutorial_line = Line2D.new()
	_tutorial_line.name = "TutorialLine"
	_tutorial_line.width = 6.0
	_tutorial_line.default_color = Color(1, 0.9, 0, 0.4) # Amarillo semi-transparente
	_tutorial_line.joint_mode = Line2D.LINE_JOINT_ROUND
	_tutorial_line.begin_cap_mode = Line2D.LINE_CAP_ROUND
	_tutorial_line.end_cap_mode = Line2D.LINE_CAP_ROUND
	add_child(_tutorial_line)
	
	_tutorial_cursor = Label.new()
	_tutorial_cursor.name = "TutorialCursor"
	_tutorial_cursor.text = "👉"
	_tutorial_cursor.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_tutorial_cursor.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_tutorial_cursor.add_theme_font_size_override("font_size", 48)
	_tutorial_cursor.pivot_offset = Vector2(24, 24)
	add_child(_tutorial_cursor)
	
	# Centrar los recuadros originales para que no se desplacen raro al crecer
	ancestor.position -= Vector2(GRID_SIZE, GRID_SIZE)
	descendant.position -= Vector2(GRID_SIZE, GRID_SIZE)
	_tutorial_cursor.position = (ancestor.position + ancestor.size / 2.0) - Vector2(24, 24)
	
	root_line.width = GRID_SIZE * 0.4
	
	var center_pos = ancestor.position + ancestor.size / 2.0
	var start_pos = get_grid_pos(center_pos)
	current_path.append(start_pos)
	root_line.points = current_path
	update_ui()
	_setup_battery_ui()
	_load_leaderboard_entries()
	_setup_classification_area()
	
	# Instanciar el reproductor de música de fondo
	_music_player = AudioStreamPlayer.new()
	_music_player.name = "BackgroundMusic"
	_music_player.bus = "Master"
	add_child(_music_player)
	_play_music()
	
	# Posicionar la cámara en el menú inicial
	camera.position = Vector2(0, -648)
	
	# Configurar y levantar el menú principal
	_setup_main_menu()
	
	# Establecer el idioma inglés por defecto al inicio
	_set_language("en")
	
	# Ocultar el tutorial de inicio mientras estamos en el menú
	if _tutorial_line:
		_tutorial_line.hide()
	if _tutorial_cursor:
		_tutorial_cursor.hide()

func _process(delta):
	# Animación de Pulso Rítmico Sincronizado para el Título del Menú Principal
	if _menu_node:
		var title_lbl = _menu_node.find_child("MenuTitle", true, false)
		var title_shadow = _menu_node.find_child("MenuTitleShadow", true, false)
		if title_lbl and title_shadow:
			# Decaer sutilmente el pulso del latido hacia 0 en cada fotograma
			_title_beat_pulse = lerp(_title_beat_pulse, 0.0, 1.0 - exp(-10.0 * delta))
			if _title_beat_pulse < 0.005:
				_title_beat_pulse = 0.0
				
			# El título de delante permanece perfectamente estático, elegante y quieto
			title_lbl.position = Vector2(0, 90)
			title_lbl.rotation = 0.0
			title_lbl.scale = Vector2.ONE
			
			# La sombra proyectada detrás es la que late al compás de la música (efecto aura/proyección rítmica por letra)
			title_shadow.position = Vector2(0, 90)
			title_shadow.rotation = 0.0
			title_shadow.scale = Vector2.ONE
			
			var shadow_scale = 1.05 + _title_beat_pulse * 1.2
			var shadow_vbox = title_shadow.find_child("VBox", true, false)
			if shadow_vbox:
				for line_node in shadow_vbox.get_children():
					if line_node is HBoxContainer:
						for char_node in line_node.get_children():
							if char_node is Label:
								char_node.scale = Vector2(shadow_scale, shadow_scale)
			
			# Detección adaptativa de ritmo ultra-sensible para la intro suave (primeros 8 segundos)
			# Nota: Analizamos la frecuencia de 20Hz a 300Hz para capturar todo el subgrave y bajo de la intro.
			if _analyzer:
				_menu_beat_cooldown = max(0.0, _menu_beat_cooldown - delta)
				var menu_mag_vec = _analyzer.get_magnitude_for_frequency_range(20.0, 300.0)
				var menu_magnitude = (menu_mag_vec.x + menu_mag_vec.y) / 2.0
				
				var menu_delta = menu_magnitude - _menu_last_magnitude
				_menu_last_magnitude = menu_magnitude
				
				# Mantener promedio dinámico de los cambios de amplitud para auto-calibrar la sensibilidad
				_menu_average_delta = lerp(_menu_average_delta, abs(menu_delta), 1.0 - exp(-3.0 * delta))
				
				# Si hay un pico transitorio que supera la media (sensibilidad adaptativa ultra-precisa)
				# Esto garantiza la pulsación rítmica perfecta incluso con volúmenes o espectros muy bajos.
				if menu_delta > max(0.00012, _menu_average_delta * 1.3) and _menu_beat_cooldown <= 0.0:
					_menu_beat_cooldown = 0.32 # Lockout de 320ms para sincronizar el golpe principal de la intro
					_title_beat_pulse = 0.15    # Latido de la sombra/proyección detrás del texto (15% de escala)

	if game_over:
		# Bucle de la intro musical tranquila (primeros 8s) al perder
		if _music_player and _music_player.playing:
			if _music_player.get_playback_position() >= 8.0:
				_music_player.seek(0.0)
				
		# Redibujar la cuadrícula en cada frame para acompañar a la cámara
		queue_redraw()
		return
		
	# Interpolar la savia mostrada con suavidad premium en tiempo de juego
	if not in_menu:
		_displayed_sap = lerp(_displayed_sap, float(sap), 1.0 - exp(-8.0 * delta))
		if abs(_displayed_sap - float(sap)) < 0.05:
			_displayed_sap = float(sap)
			
		# Interpolar el pulso de las celdas individuales de la batería hacia 0
		_battery_beat_pulse = lerp(_battery_beat_pulse, 0.0, 1.0 - exp(-12.0 * delta))
		if _battery_beat_pulse < 0.01:
			_battery_beat_pulse = 0.0
			
		if _battery_bar:
			_battery_bar.queue_redraw()
			
	# Procesamiento continuo de dibujo o retracción
	if is_drawing:
		try_add_point(get_global_mouse_position())
	elif is_retracting:
		retract_root()
		
	if not waiting_for_next and first_union_made:
		# Mover cámara implacablemente hacia abajo
		camera.position.y += camera_speed * delta
		
	# Bucle de la primera parte de la intro musical (primeros 8s) antes de la primera unión
	if _music_player and _music_player.playing and not first_union_made:
		if _music_player.get_playback_position() >= 8.0:
			_music_player.seek(0.0)
			
	# Animar tutorial visual del cursor si no se ha hecho la primera unión y no estamos en el menú
	if not first_union_made and not in_menu and _tutorial_cursor and _tutorial_line:
		_tutorial_timer += delta
		if _tutorial_timer >= 3.0:
			_tutorial_timer = 0.0
			
		var ancestor_center = ancestor.position + ancestor.size / 2.0
		var descendant_center = descendant.position + descendant.size / 2.0
		
		var phase_time = _tutorial_timer
		if phase_time < 1.5:
			# Fase 1: Deslizamiento (0.0s a 1.5s)
			var t = phase_time / 1.5
			# Interpolar de forma suave
			t = sin(t * PI / 2.0)
			var current_pos = ancestor_center.lerp(descendant_center, t)
			_tutorial_cursor.position = current_pos - Vector2(24, 24)
			_tutorial_cursor.show()
			_tutorial_cursor.modulate.a = 0.8
			_tutorial_cursor.scale = Vector2.ONE
			_tutorial_line.show()
			_tutorial_line.clear_points()
			_tutorial_line.add_point(ancestor_center)
			_tutorial_line.add_point(current_pos)
			_tutorial_line.modulate.a = 0.4
		elif phase_time < 2.5:
			# Fase 2: Mantener y simular click/pulso (1.5s a 2.5s)
			_tutorial_cursor.position = descendant_center - Vector2(24, 24)
			var pulse = 1.0 + sin((phase_time - 1.5) * 15.0) * 0.15
			_tutorial_cursor.scale = Vector2(pulse, pulse)
			_tutorial_line.clear_points()
			_tutorial_line.add_point(ancestor_center)
			_tutorial_line.add_point(descendant_center)
			_tutorial_cursor.modulate.a = 0.8
			_tutorial_line.modulate.a = 0.4
		else:
			# Fase 3: Desvanecimiento (2.5s a 3.0s)
			var t = (phase_time - 2.5) / 0.5
			var alpha = lerp(0.8, 0.0, t)
			_tutorial_cursor.modulate.a = alpha
			_tutorial_line.modulate.a = alpha * 0.5
			_tutorial_cursor.scale = Vector2.ONE
		
	# Comprobar si el linaje se ha quedado atrás (Game Over por scroll)
	var limit_y = camera.position.y
	
	# La ÚNICA condición de muerte por scroll:
	# El retrato destino (pareja) ha desaparecido completamente por arriba.
	# Si la pareja sigue en pantalla, el jugador SIEMPRE tiene la oportunidad de salvarse (usando el click derecho para retraer la raíz si se quedó atascada arriba).
	var destination_lost = (descendant.position.y + descendant.size.y) < limit_y
	
	if destination_lost and not game_over:
		trigger_game_over(false, true)
			
	# Redibujar la cuadrícula en cada frame para que acompañe a la cámara
	queue_redraw()
	
	# Sincronización Rítmica Dinámica Aislada (Espectro Físico Sub-Graves)
	if _analyzer:
		_beat_cooldown = max(0.0, _beat_cooldown - delta)
		
		# Obtener la magnitud en la banda del subgrave más profundo (20Hz a 50Hz)
		# Los coros, sintetizadores y efectos del juego NO tienen energía por debajo de 50Hz.
		var magnitude_vec = _analyzer.get_magnitude_for_frequency_range(20.0, 50.0)
		var magnitude = (magnitude_vec.x + magnitude_vec.y) / 2.0
		
		# Calcular el ataque transitorio (diferencia de volumen con el fotograma anterior)
		var delta_magnitude = magnitude - _last_magnitude
		_last_magnitude = magnitude
		
		# Si hay una subida brusca y masiva de energía en graves (solo el impacto del bombo más duro)
		# Subimos el umbral a 0.045 para ignorar cualquier bajo 808 secundario o adorno.
		# Aumentamos el cooldown a 0.38s para bloquear por completo dobles golpes rápidos (lockout).
		if delta_magnitude > 0.045 and _beat_cooldown <= 0.0:
			_beat_cooldown = 0.38 # Lockout de 380ms para filtrar dobles golpes y centrar el beat principal
			_trigger_real_beat()
	else:
		# Fallback por reloj de alta precisión si la música no está sonando
		var global_time = Time.get_ticks_msec() / 1000.0
		var beat_interval = 60.0 / music_bpm
		var current_beat = int(global_time / beat_interval)
		
		if current_beat != last_beat_index:
			last_beat_index = current_beat
			_trigger_real_beat()

func _trigger_real_beat() -> void:
	# 1. Expandir y cabecear todos los retratos en la escena (los inactivos solo pulsan su marco)
	for node in get_children():
		if node is PortraitFrame and node.has_method("trigger_beat_bob"):
			node.trigger_beat_bob()
		
	# 2. Latir los bloques grises y savias del entorno
	trigger_global_beat_pulse()
	
	# 3. Latir el indicador de combo de generación (brillo neón dorado e incremento de tamaño)
	if _generation_combo and _generation_combo.visible and _generation_combo.modulate.a > 0.01:
		_generation_combo.scale = Vector2(1.3, 1.3)
		_generation_combo.modulate = Color(1.5, 1.5, 1.2, 1.0) # Sobresaturación neón blanca/dorada
		var t = create_tween().set_parallel(true)
		t.tween_property(_generation_combo, "scale", Vector2.ONE, 0.22).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		t.tween_property(_generation_combo, "modulate", Color.WHITE, 0.22).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		
	# Latir también el contador de savia verde recolectada en perfecta sincronía
	if _green_score_label and _green_score_label.visible and _green_score_label.modulate.a > 0.01:
		_green_score_label.scale = Vector2(1.3, 1.3)
		_green_score_label.modulate = Color(1.2, 2.0, 1.2, 1.0) # Sobresaturación neón verde
		var t = create_tween().set_parallel(true)
		t.tween_property(_green_score_label, "scale", Vector2.ONE, 0.22).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		t.tween_property(_green_score_label, "modulate", Color.WHITE, 0.22).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		
	# 4. Latir las celdas/barras internas de la batería en perfecta sincronía
	_battery_beat_pulse = 1.0

func trigger_global_beat_pulse() -> void:
	# 1. Pulsar obstáculos grises (ColorRects en obstacles)
	for obs in obstacles.get_children():
		if obs.is_queued_for_deletion() or obs.has_meta("dying"):
			continue
		obs.pivot_offset = obs.size / 2.0
		obs.scale = Vector2(1.15, 1.15) # Exagerado: Crece un 15%
		var t = create_tween()
		t.tween_property(obs, "scale", Vector2.ONE, 0.25).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		
	# 2. Pulsar recompensas verdes (ColorRects en rewards_container)
	for rew in rewards_container.get_children():
		if rew.is_queued_for_deletion() or rew.has_meta("dying"):
			continue
		rew.pivot_offset = rew.size / 2.0
		rew.scale = Vector2(1.28, 1.28) # Exagerado: Crece un 28% (súper jugoso)
		var t = create_tween()
		t.tween_property(rew, "scale", Vector2.ONE, 0.25).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)

func retract_root():
	if game_over or waiting_for_next:
		return
		
	# Retraer un punto cada frame (60 puntos por segundo), muy rápido
	# pero asegurándose de no borrar el punto de inicio (el ancestro)
	if current_path.size() > 1:
		current_path.remove_at(current_path.size() - 1)
		sap += 1
		update_ui()
		root_line.points = current_path

func _draw():
	# Dibujar la cuadrícula solo en el área visible de la cámara
	var start_y = int(camera.position.y / GRID_SIZE) * GRID_SIZE
	var end_y = start_y + 648 + GRID_SIZE * 2
	var grid_color = Color(1, 1, 1, 0.05) # Muy sutil
	
	# Líneas verticales
	for x in range(0, 1152 + GRID_SIZE, GRID_SIZE):
		draw_line(Vector2(x, start_y), Vector2(x, end_y), grid_color, 1.0)
		
	# Líneas horizontales
	for y in range(start_y, end_y, GRID_SIZE):
		draw_line(Vector2(0, y), Vector2(1152, y), grid_color, 1.0)

func _input(event):
	if game_over or waiting_for_next or in_menu:
		return
		
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT:
			if event.pressed:
				var mouse_pos = get_global_mouse_position()
				var last_pos = current_path[-1]
				
				# Filtro de distancia generoso (96px = 3 celdas) para evitar que hacer clic
				# lejos (como en el retrato de la pareja) autodibuje el camino completo (auto-ganar).
				if mouse_pos.distance_to(last_pos) < 96.0:
					is_drawing = true
					is_retracting = false # Prioridad al dibujo si se pulsa
					try_add_point(mouse_pos)
			else:
				is_drawing = false
		elif event.button_index == MOUSE_BUTTON_RIGHT:
			if event.pressed:
				is_retracting = true
				is_drawing = false # Prioridad a retraer
			else:
				is_retracting = false
				
	elif event is InputEventMouseMotion:
		if Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT) and is_drawing:
			try_add_point(get_global_mouse_position())
		else:
			is_drawing = false

func try_add_point(mouse_pos: Vector2):
	if sap <= 0 or game_over or waiting_for_next:
		return
		
	var grid_pos = get_grid_pos(mouse_pos)
	if grid_pos != current_path[-1]:
		fill_path_to(grid_pos)

func fill_path_to(target_grid_pos: Vector2):
	var max_steps = 30 # Prevenir bucles infinitos si hay un bug
	var step = 0
	
	while current_path[-1].distance_to(target_grid_pos) > 5 and step < max_steps:
		var last_pos = current_path[-1]
		
		var dx = target_grid_pos.x - last_pos.x
		var dy = target_grid_pos.y - last_pos.y
		var step_x = sign(dx) * GRID_SIZE if abs(dx) > 5 else 0
		var step_y = sign(dy) * GRID_SIZE if abs(dy) > 5 else 0
		
		var moved = false
		var current_gen = generation
		
		# Intentar avanzar en el eje con mayor distancia primero (eje dominante)
		if abs(dx) >= abs(dy) and step_x != 0:
			if try_add_single_point(last_pos + Vector2(step_x, 0)):
				moved = true
			elif generation == current_gen and step_y != 0 and try_add_single_point(last_pos + Vector2(0, step_y)):
				moved = true
		elif step_y != 0:
			if try_add_single_point(last_pos + Vector2(0, step_y)):
				moved = true
			elif generation == current_gen and step_x != 0 and try_add_single_point(last_pos + Vector2(step_x, 0)):
				moved = true
				
		if generation != current_gen:
			break # El nivel ha terminado, abortar dibujo
				
		if not moved:
			break # Detener si chocamos o nos quedamos sin savia
		step += 1

func try_add_single_point(grid_pos: Vector2) -> bool:
	if sap <= 0:
		return false
		
	if is_colliding_with_obstacle(grid_pos):
		return false
		
	# Comprobar si choca con raíces antiguas
	for old_point in all_previous_paths:
		if old_point.distance_to(grid_pos) < 5:
			return false
			
	for point in current_path:
		if point.distance_to(grid_pos) < 5:
			return false
			
	current_path.append(grid_pos)
	root_line.points = current_path
	sap -= SAP_COST_PER_SEGMENT
	
	# Comprobar recolección de recompensas
	for reward in rewards_container.get_children():
		var reward_center = reward.position + reward.size / 2.0
		if grid_pos.distance_to(reward_center) < GRID_SIZE / 2.0:
			sap += 1
			green_squares_collected += 1
			if _green_score_label:
				_green_score_label.text = str(green_squares_collected)
				_green_score_label.scale = Vector2(1.3, 1.3)
				_green_score_label.modulate = Color(1.5, 2.2, 1.5, 1.0) # Súper destello neón verde
				var t = create_tween().set_parallel(true)
				t.tween_property(_green_score_label, "scale", Vector2.ONE, 0.15).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
				t.tween_property(_green_score_label, "modulate", Color.WHITE, 0.15).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
			reward.queue_free()
			
	update_ui()
	
	if check_win_condition(grid_pos):
		return false # Detener el bucle si hemos ganado
	
	if sap <= 0 and not game_over and not waiting_for_next:
		trigger_game_over(false)
		
	return true

func get_grid_pos(pos: Vector2) -> Vector2:
	var x = floor(pos.x / GRID_SIZE) * GRID_SIZE + GRID_SIZE / 2.0
	var y = floor(pos.y / GRID_SIZE) * GRID_SIZE + GRID_SIZE / 2.0
	return Vector2(x, y)
	
func get_grid_coord(pos: Vector2) -> Vector2i:
	return Vector2i(floor(pos.x / GRID_SIZE), floor(pos.y / GRID_SIZE))

func is_adjacent(pos1: Vector2, pos2: Vector2) -> bool:
	var dx = abs(pos1.x - pos2.x)
	var dy = abs(pos1.y - pos2.y)
	return (dx < 5 and abs(dy - GRID_SIZE) < 5) or (dy < 5 and abs(dx - GRID_SIZE) < 5)

func is_colliding_with_obstacle(pos: Vector2) -> bool:
	# 1. Colisión con bloques grises obstáculo
	for obs in obstacles.get_children():
		if obs is ColorRect:
			var rect = Rect2(obs.position, obs.size)
			if rect.has_point(pos):
				return true
				
	# 2. Colisión con retratos (PortraitFrame) de 3x3 celdas
	for node in get_children():
		if node is PortraitFrame:
			var rect = Rect2(node.position, node.size)
			if rect.has_point(pos):
				if node == ancestor:
					# Comprobar si la raíz ya ha salido de las 3x3 celdas del retrato inicial
					var has_left_ancestor = false
					for p in current_path:
						if not rect.has_point(p):
							has_left_ancestor = true
							break
					# Si ya salió, bloquear cualquier re-entrada para evitar bucles inválidos
					if has_left_ancestor:
						return true
				elif node == descendant:
					# El descendiente (objetivo) permite el primer contacto para ganar
					continue
				else:
					# Cualquier otro retrato antiguo visible en escena es 100% sólido e impenetrable
					return true
					
	return false

func check_win_condition(pos: Vector2) -> bool:
	var target_rect = Rect2(descendant.position, descendant.size)
	if target_rect.has_point(pos):
		trigger_game_over(true)
		return true
	return false

func update_ui():
	if sap_label:
		sap_label.text = ("Sap: " if current_language == "en" else "Savia: ") + str(sap)
	if _battery_bar:
		_battery_bar.queue_redraw()
	if gen_label:
		gen_label.text = ("Generation: " if current_language == "en" else "Generación: ") + str(generation)
	if _generation_combo:
		_generation_combo.text = "x" + str(generation) + "!"
	if _green_score_label:
		_green_score_label.text = str(green_squares_collected)

func trigger_game_over(win: bool, out_of_bounds: bool = false):
	is_drawing = false # <--- FIX: Cortar el dibujo activo inmediatamente
	is_retracting = false
	
	if win:
		camera_speed += 5.0 # Acelerar un poco la cámara con cada victoria
		start_next_generation()
	else:
		game_over = true
		
		# Ocultar cualquier texto plano viejo
		if message_label:
			message_label.hide()
			
		# Cambiar la música a la intro tranquila inmediatamente
		if _music_player and _music_player.playing:
			_music_player.seek(0.0)
			
		# Mostrar y animar el área de clasificación abajo en el mundo 2D
		if _classification_area:
			# Actualizar el texto del récord alcanzado en el contenedor
			var score_lbl = _classification_area.find_child("ScoreLabel", true, false)
			if score_lbl:
				var final_score = green_squares_collected * generation
				score_lbl.text = "PUNTUACIÓN: " + str(final_score) + "\n(Savia: " + str(green_squares_collected) + " × Gen: " + str(generation) + ")"
				
			# Posicionar exactamente un alto de pantalla por debajo de la cámara actual
			_classification_area.position = Vector2(0, camera.position.y + 648.0)
			_classification_area.modulate.a = 0.0
			_classification_area.show()
			
			var t = create_tween().set_parallel(true)
			t.tween_property(camera, "position:y", camera.position.y + 648.0, 1.5).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_IN_OUT)
			t.tween_property(_classification_area, "modulate:a", 1.0, 1.2).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)

func start_next_generation():
	waiting_for_next = false
	
	# Si es la primera unión, activar contrareloj, dar paso al drop de música y limpiar tutorial
	if not first_union_made:
		first_union_made = true
		if _music_player and _music_player.playing:
			_music_player.seek(16.0) # ¡El bombo Phonk revienta con el drop!
		
		# Animar la entrada de la barra de savia y del combo de generación de forma elástica y premium
		var ui_tween = create_tween().set_parallel(true)
		if _battery_bar:
			ui_tween.tween_property(_battery_bar, "scale", Vector2.ONE, 0.8).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
			ui_tween.tween_property(_battery_bar, "modulate:a", 1.0, 0.6).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		if _generation_combo:
			ui_tween.tween_property(_generation_combo, "scale", Vector2.ONE, 0.8).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
			ui_tween.tween_property(_generation_combo, "modulate:a", 1.0, 0.6).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		if _green_score_label:
			ui_tween.tween_property(_green_score_label, "scale", Vector2.ONE, 0.8).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
			ui_tween.tween_property(_green_score_label, "modulate:a", 1.0, 0.6).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		
		# Limpiar nodos del tutorial de forma segura
		if _tutorial_line:
			_tutorial_line.queue_free()
			_tutorial_line = null
		if _tutorial_cursor:
			_tutorial_cursor.queue_free()
			_tutorial_cursor = null
			
	# Guardar la ruta actual en el historial de colisiones
	all_previous_paths.append_array(current_path)
	
	# Cambiar color de raíces y retratos antiguos a un tono oscuro gradualmente usando un Tween
	var tween = create_tween()
	tween.set_parallel(true)
	tween.tween_property(root_line, "default_color", Color(0.6, 0.5, 0, 1), 1.0)
	tween.tween_property(ancestor, "color", ancestor.color.darkened(0.5), 1.0)
	tween.tween_property(descendant, "color", descendant.color.darkened(0.5), 1.0)
	
	# Desactivar animaciones (respiración y cabeceo) de los padres que acaban de pasar a la historia
	ancestor.active = false
	descendant.active = false
	
	var current_y = descendant.position.y
	var mid_x = (ancestor.position.x + descendant.position.x) / 2.0
	
	# 1. Encontrar el punto de la ruta más cercano al CENTRO HORIZONTAL entre los padres.
	# Si la ruta cruza el centro varias veces, elegimos la pasada que esté más profunda (mayor Y)
	var branch_point = current_path[0]
	var min_dist_to_center = 999999.0
	var local_max_y = -999999.0
	
	for p in current_path:
		var dist = abs(p.x - mid_x)
		if dist < min_dist_to_center - 10: # Mejorar si se acerca significativamente al centro
			min_dist_to_center = dist
			local_max_y = p.y
			branch_point = p
		elif abs(dist - min_dist_to_center) <= 10: # Si está igual de centrado, preferir el más profundo
			if p.y > local_max_y:
				local_max_y = p.y
				branch_point = p
				
	# 2. Encontrar la profundidad MÁXIMA ABSOLUTA de toda la ruta para garantizar que el nuevo hijo
	# aparezca por debajo de cualquier curva profunda que el jugador haya hecho buscando recompensas.
	var absolute_max_y = current_path[0].y
	for p in current_path:
		if p.y > absolute_max_y:
			absolute_max_y = p.y
	
	# Instanciar al Hijo (alineado al centro y por debajo del todo)
	var child_grid_center = get_grid_pos(Vector2(branch_point.x, absolute_max_y + 6 * GRID_SIZE))
	
	var child = PortraitFrame.new()
	child.size = Vector2(GRID_SIZE * 3, GRID_SIZE * 3)
	child.position = child_grid_center - Vector2(GRID_SIZE * 1.5, GRID_SIZE * 1.5)
	
	# 50/50 de probabilidad de ser hombre o mujer
	var is_boy = randf() > 0.5
	if is_boy:
		child.color = Color(0, 0.8, 1, 1) # Azul
	else:
		child.color = Color(1, 0, 0.8, 1) # Rosa
		
	child.z_index = 10 # Siempre por encima de las raíces
	child.mouse_filter = Control.MOUSE_FILTER_IGNORE
	child.pivot_offset = child.size / 2.0
	child.scale = Vector2.ZERO
	add_child(child)
	tween.tween_property(child, "scale", Vector2.ONE, 0.5).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	
	var descent_line = Line2D.new()
	descent_line.width = GRID_SIZE * 0.4
	descent_line.default_color = Color(1, 0.9, 0, 1) # Nace brillante
	tween.tween_property(descent_line, "default_color", Color(0.6, 0.5, 0, 1), 1.0) # Y se apaga con el resto
	descent_line.add_point(branch_point)
	descent_line.add_point(child_grid_center)
	roots_container.add_child(descent_line)
	
	# Añadir la línea vertical al historial de colisiones antiguas y destruir obstáculos en su camino
	var start_y_grid = int(branch_point.y / GRID_SIZE)
	var end_y_grid = int(child_grid_center.y / GRID_SIZE)
	var branch_x_grid = int(branch_point.x / GRID_SIZE)
	
	# Hacemos que la línea vertical sea sólida hasta el borde superior del retrato (end_y_grid - 1)
	# Esto evita que se crucen o solapen raíces antiguas directamente sobre el marco del personaje.
	for y in range(start_y_grid, end_y_grid - 1):
		var pos = get_grid_pos(Vector2(branch_x_grid * GRID_SIZE, y * GRID_SIZE))
		all_previous_paths.append(pos)
	# Instanciar a la nueva Pareja (ya no en la misma línea estricta)
	var new_partner = PortraitFrame.new()
	new_partner.size = Vector2(GRID_SIZE * 3, GRID_SIZE * 3)
	
	var offset_cells_x = randi_range(10, 16)
	var offset_cells_y = randi_range(-2, 4) # La pareja puede estar un poco más arriba o más abajo que el hijo
	
	var target_x = 0
	if child.position.x < 1152 / 2.0:
		target_x = child.position.x + offset_cells_x * GRID_SIZE
	else:
		target_x = child.position.x - offset_cells_x * GRID_SIZE
		
	target_x = clamp(target_x, GRID_SIZE * 4, 1152 - GRID_SIZE * 4) # Mayor margen en bordes para el 3x3
	
	var partner_grid_center = get_grid_pos(Vector2(target_x, child_grid_center.y + offset_cells_y * GRID_SIZE))
	new_partner.position = partner_grid_center - Vector2(GRID_SIZE * 1.5, GRID_SIZE * 1.5)
	
	if is_boy:
		new_partner.color = Color(1, 0, 0.8, 1) # Rosa
	else:
		new_partner.color = Color(0, 0.8, 1, 1) # Azul
		
	new_partner.z_index = 10 # Siempre por encima de las raíces
	new_partner.mouse_filter = Control.MOUSE_FILTER_IGNORE
	new_partner.pivot_offset = new_partner.size / 2.0
	new_partner.scale = Vector2.ZERO
	add_child(new_partner)
	tween.tween_property(new_partner, "scale", Vector2.ONE, 0.5).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	
	# --- NUEVA LÓGICA DE LIMPIEZA TOTAL ---
	# Limpiar TODO lo que estorbe visual o físicamente a la nueva generación (tanto de la generación anterior como puestos en el editor)
	# 1. El camino de la línea vertical entera (con margen ancho)
	var line_clear_rect = Rect2(
		Vector2(branch_point.x - GRID_SIZE, branch_point.y),
		Vector2(GRID_SIZE * 2, child_grid_center.y - branch_point.y + GRID_SIZE)
	)
	
	# 2. Las zonas seguras (5x5) alrededor del hijo y la pareja
	var child_clear_rect = Rect2(child.position - Vector2(GRID_SIZE, GRID_SIZE), Vector2(GRID_SIZE * 5, GRID_SIZE * 5))
	var partner_clear_rect = Rect2(new_partner.position - Vector2(GRID_SIZE, GRID_SIZE), Vector2(GRID_SIZE * 5, GRID_SIZE * 5))
	
	for obs in obstacles.get_children():
		var obs_rect = Rect2(obs.position, obs.size)
		if obs_rect.intersects(line_clear_rect) or obs_rect.intersects(child_clear_rect) or obs_rect.intersects(partner_clear_rect):
			obs.set_meta("dying", true)
			var t = create_tween()
			t.tween_property(obs, "scale", Vector2.ZERO, 0.3).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
			t.tween_callback(obs.queue_free)
			
	for rew in rewards_container.get_children():
		var rew_rect = Rect2(rew.position, rew.size)
		if rew_rect.intersects(line_clear_rect) or rew_rect.intersects(child_clear_rect) or rew_rect.intersects(partner_clear_rect):
			rew.set_meta("dying", true)
			var t = create_tween()
			t.tween_property(rew, "scale", Vector2.ZERO, 0.3).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
			t.tween_callback(rew.queue_free)
	
	# === GENERACIÓN PROCEDURAL DE OBSTÁCULOS Y RECOMPENSAS ===
	var child_coord = get_grid_coord(child_grid_center)
	var partner_coord = get_grid_coord(partner_grid_center)
	
	var astar = AStarGrid2D.new()
	var top_y = min(child_coord.y, partner_coord.y) - 4
	var bottom_y = max(child_coord.y, partner_coord.y) + 6
	var max_grid_x = floor(1152 / GRID_SIZE)
	astar.region = Rect2i(0, top_y, max_grid_x, bottom_y - top_y)
	astar.cell_size = Vector2(GRID_SIZE, GRID_SIZE)
	astar.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_NEVER
	astar.update()
	
	# MARCAR OBSTÁCULOS ANTIGUOS COMO SÓLIDOS PARA NO PISARLOS
	for obs in obstacles.get_children():
		if obs.is_queued_for_deletion() or obs.has_meta("dying"): continue
		var coord = Vector2i(round(obs.position.x / GRID_SIZE), round(obs.position.y / GRID_SIZE))
		if astar.region.has_point(coord):
			astar.set_point_solid(coord, true)
			
	for rew in rewards_container.get_children():
		if rew.is_queued_for_deletion() or rew.has_meta("dying"): continue
		var base_x = rew.position.x - GRID_SIZE * 0.2
		var base_y = rew.position.y - GRID_SIZE * 0.2
		var coord = Vector2i(round(base_x / GRID_SIZE), round(base_y / GRID_SIZE))
		if astar.region.has_point(coord):
			astar.set_point_solid(coord, true)
	# Marcar también TODAS las raíces antiguas como sólidas para el generador
	for old_path in all_previous_paths:
		var coord = get_grid_coord(old_path)
		if astar.region.has_point(coord):
			astar.set_point_solid(coord, true)
			
	# Asegurarnos de que el punto de inicio y fin NO sean sólidos, o AStar siempre fallará
	astar.set_point_solid(child_coord, false)
	astar.set_point_solid(partner_coord, false)
	
	var num_obstacles = randi_range(15, 35)
	var placed_obstacles = []
	
	for i in range(num_obstacles):
		var rx = randi_range(2, max_grid_x - 3)
		var ry = randi_range(top_y + 1, bottom_y - 1)
		var cell = Vector2i(rx, ry)
		
		# No bloquear área del retrato 3x3 ni su borde (caja de 5x5)
		var in_child_box = abs(cell.x - child_coord.x) <= 2 and abs(cell.y - child_coord.y) <= 2
		var in_partner_box = abs(cell.x - partner_coord.x) <= 2 and abs(cell.y - partner_coord.y) <= 2
		
		if in_child_box or in_partner_box:
			continue
			
		if astar.is_point_solid(cell):
			continue
			
		astar.set_point_solid(cell, true)
		
		# Garantizar que el puzzle SIEMPRE se puede resolver
		if astar.get_id_path(child_coord, partner_coord).size() == 0:
			# Si corta el único camino, deshacemos
			astar.set_point_solid(cell, false)
		else:
			placed_obstacles.append(cell)
			
	# Dibujar los obstáculos
	for cell in placed_obstacles:
		var obs = ColorRect.new()
		obs.size = Vector2(GRID_SIZE, GRID_SIZE)
		obs.position = Vector2(cell.x * GRID_SIZE, cell.y * GRID_SIZE)
		obs.color = Color(0.25, 0.25, 0.25, 1) # Gris oscuro
		obs.mouse_filter = Control.MOUSE_FILTER_IGNORE
		obs.pivot_offset = obs.size / 2.0
		obs.scale = Vector2.ZERO
		obstacles.add_child(obs)
		var t = create_tween()
		t.tween_property(obs, "scale", Vector2.ONE, randf_range(0.3, 0.6)).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT).set_delay(randf_range(0.0, 0.3))
		
	# Dibujar recompensas (Savia) en celdas vacías
	var num_rewards = randi_range(2, 6)
	for i in range(num_rewards):
		var rx = randi_range(2, max_grid_x - 3)
		var ry = randi_range(top_y + 1, bottom_y - 1)
		var cell = Vector2i(rx, ry)
		
		var in_child_box = abs(cell.x - child_coord.x) <= 2 and abs(cell.y - child_coord.y) <= 2
		var in_partner_box = abs(cell.x - partner_coord.x) <= 2 and abs(cell.y - partner_coord.y) <= 2
		
		if in_child_box or in_partner_box:
			continue
			
		if not astar.is_point_solid(cell):
			# Garantizar que la recompensa sea físicamente accesible por el jugador
			if astar.get_id_path(child_coord, cell).size() > 0:
				var reward_rect = Rect2(Vector2(cell.x * GRID_SIZE + GRID_SIZE * 0.2, cell.y * GRID_SIZE + GRID_SIZE * 0.2), Vector2(GRID_SIZE * 0.6, GRID_SIZE * 0.6))
				var is_overlapping_editor_block = false
				
				# Comprobar colisión física real contra bloques (para evitar solapamientos con bloques puestos a mano en el editor)
				for obs in obstacles.get_children():
					var obs_rect = Rect2(obs.position, obs.size)
					if obs_rect.intersects(reward_rect):
						is_overlapping_editor_block = true
						break
				
				if is_overlapping_editor_block:
					continue
					
				var reward = ColorRect.new()
				# Recompensa más pequeña para distinguirla
				reward.size = Vector2(GRID_SIZE * 0.6, GRID_SIZE * 0.6)
				reward.position = Vector2(cell.x * GRID_SIZE + GRID_SIZE * 0.2, cell.y * GRID_SIZE + GRID_SIZE * 0.2)
				reward.color = Color(0.1, 0.9, 0.1, 1) # Verde fosforito
				reward.mouse_filter = Control.MOUSE_FILTER_IGNORE
				reward.pivot_offset = reward.size / 2.0
				reward.scale = Vector2.ZERO
				rewards_container.add_child(reward)
				var t = create_tween()
				t.tween_property(reward, "scale", Vector2.ONE, randf_range(0.3, 0.6)).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT).set_delay(randf_range(0.0, 0.3))
				astar.set_point_solid(cell, true) # Evitar que salgan dos recompensas en la misma celda
	# ==========================================================
	
	# Limpieza de memoria: borrar obstáculos muy antiguos
	var limit_y = camera.position.y - 1500
	for obs in obstacles.get_children():
		if obs.position.y < limit_y:
			obs.queue_free()
	for reward in rewards_container.get_children():
		if reward.position.y < limit_y:
			reward.queue_free()
			
	# Limpiar retratos de antepasados antiguos que ya estén muy arriba del límite de cámara
	for node in get_children():
		if node is PortraitFrame and node != child and node != new_partner:
			if node.position.y < limit_y:
				node.queue_free()
				
	# Limpiar líneas de raíces antiguas del contenedor que ya estén muy arriba del límite
	for line in roots_container.get_children():
		if line is Line2D and line != root_line and line != descent_line:
			if line.points.size() > 0 and line.points[0].y < limit_y:
				line.queue_free()
			
	# Limpiar historial de rutas antiguas para liberar memoria
	var filtered_paths: Array[Vector2] = []
	for p in all_previous_paths:
		if p.y > limit_y:
			filtered_paths.append(p)
	all_previous_paths = filtered_paths
	
	ancestor = child
	descendant = new_partner
	
	root_line = Line2D.new()
	root_line.width = GRID_SIZE * 0.4
	root_line.default_color = Color(1, 0.9, 0, 1)
	root_line.joint_mode = Line2D.LINE_JOINT_ROUND
	root_line.begin_cap_mode = Line2D.LINE_CAP_ROUND
	root_line.end_cap_mode = Line2D.LINE_CAP_ROUND
	roots_container.add_child(root_line)
	
	current_path.clear()
	var start_pos = get_grid_pos(ancestor.position + ancestor.size / 2.0)
	current_path.append(start_pos)
	root_line.points = current_path
	sap = MAX_SAP
	generation += 1
	update_ui()

func _play_music() -> void:
	# Conectar señal para bucle infinito universal (funciona en OGG, MP3 y WAV por igual)
	_music_player.finished.connect(_music_player.play)
	
	# Crear el bus de audio "Music" dedicado si no existe (Aislamiento de SFX)
	var music_bus_idx = AudioServer.get_bus_index("Music")
	if music_bus_idx == -1:
		music_bus_idx = AudioServer.get_bus_count()
		AudioServer.add_bus(music_bus_idx)
		AudioServer.set_bus_name(music_bus_idx, "Music")
		AudioServer.set_bus_send(music_bus_idx, "Master") # Enviar salida a Master
		
	_music_player.bus = "Music"
	
	var paths = [
		"res://assets/Crux Noctis.mp3",
		"res://assets/music.ogg",
		"res://assets/music.mp3",
		"res://assets/music.wav"
	]
	
	var loaded_successfully = false
	
	for path in paths:
		if ResourceLoader.exists(path):
			var stream = load(path)
			_music_player.stream = stream
			_music_player.play()
			print("Music successfully loaded and playing: ", path)
			loaded_successfully = true
			break
			
	# Si la música se cargó, inicializar el analizador de espectro en el bus exclusivo "Music"
	if loaded_successfully:
		var effect_idx = -1
		for i in range(AudioServer.get_bus_effect_count(music_bus_idx)):
			if AudioServer.get_bus_effect(music_bus_idx, i) is AudioEffectSpectrumAnalyzer:
				effect_idx = i
				break
				
		if effect_idx == -1:
			var new_effect = AudioEffectSpectrumAnalyzer.new()
			AudioServer.add_bus_effect(music_bus_idx, new_effect)
			effect_idx = AudioServer.get_bus_effect_count(music_bus_idx) - 1
			
		_analyzer = AudioServer.get_bus_effect_instance(music_bus_idx, effect_idx)
		print("Audio spectrum beat analyzer successfully initialized on isolated 'Music' bus.")

# ==============================================================================
# SISTEMA DE MENÚ PRINCIPAL Y CLASIFICACIÓN (KINETIC INTEGRATION)
# ==============================================================================

func _setup_main_menu():
	# Crear el contenedor del menú posicionado a y = -648
	_menu_node = Control.new()
	_menu_node.name = "MainMenu"
	_menu_node.size = Vector2(1152, 648)
	_menu_node.position = Vector2(0, -648)
	add_child(_menu_node)
	
	# Inicializar la fuente del sistema limpia, elegante y moderna (compartida entre idioma y render)
	_title_font = SystemFont.new()
	_title_font.font_names = PackedStringArray(["Trebuchet MS", "Arial", "sans-serif"])
	_title_font.font_weight = 700 # Negrita elegante
	
	# Contenedores para el Título del juego de Alta Costura por caracteres
	var title_lbl = Control.new()
	title_lbl.name = "MenuTitle"
	title_lbl.size = Vector2(1152, 180)
	title_lbl.position = Vector2(0, 90)
	title_lbl.clip_contents = false
	title_lbl.z_index = 2
	
	var title_shadow = Control.new()
	title_shadow.name = "MenuTitleShadow"
	title_shadow.size = Vector2(1152, 180)
	title_shadow.position = Vector2(0, 90)
	title_shadow.clip_contents = false
	title_shadow.z_index = 1
	
	_menu_node.add_child(title_shadow)
	_menu_node.add_child(title_lbl)
	
	# Botones: Jugar y Clasificación
	var play_btn = Button.new()
	play_btn.name = "PlayButton"
	_menu_node.add_child(play_btn)
	_style_menu_button(play_btn, "Jugar")
	play_btn.position = Vector2((1152 - 280) / 2, 300)
	play_btn.pressed.connect(_on_play_pressed)
	
	var leader_btn = Button.new()
	leader_btn.name = "LeaderboardButton"
	_menu_node.add_child(leader_btn)
	_style_menu_button(leader_btn, "Clasificación")
	leader_btn.position = Vector2((1152 - 280) / 2, 390)
	leader_btn.pressed.connect(_on_leaderboard_pressed)
	
	# Contenedor de selección de idioma (Banderas en la esquina superior derecha)
	_lang_selector = HBoxContainer.new()
	_lang_selector.name = "LangSelector"
	_lang_selector.position = Vector2(1152 - 116, 24)
	_lang_selector.size = Vector2(92, 44)
	_lang_selector.add_theme_constant_override("separation", 12)
	_menu_node.add_child(_lang_selector)
	
	# Botón bandera Inglesa
	_en_flag_btn = Button.new()
	_en_flag_btn.name = "FlagEN"
	_en_flag_btn.text = "🇬🇧"
	_style_flag_button(_en_flag_btn)
	_lang_selector.add_child(_en_flag_btn)
	_en_flag_btn.pressed.connect(func(): _set_language("en"))
	
	# Botón bandera Española
	_es_flag_btn = Button.new()
	_es_flag_btn.name = "FlagES"
	_es_flag_btn.text = "🇪🇸"
	_style_flag_button(_es_flag_btn)
	_lang_selector.add_child(_es_flag_btn)
	_es_flag_btn.pressed.connect(func(): _set_language("es"))
	
	# Cargar panel de clasificación oculto
	_setup_leaderboard_panel()

func _style_menu_button(btn: Button, text_val: String):
	btn.text = text_val
	btn.add_theme_font_size_override("font_size", 28)
	btn.custom_minimum_size = Vector2(280, 60)
	btn.size = Vector2(280, 60)
	btn.pivot_offset = Vector2(140, 30) # Centrado para el escalado
	btn.flat = false
	
	var normal_box = StyleBoxFlat.new()
	normal_box.bg_color = Color(0.1, 0.1, 0.1, 1)
	normal_box.border_width_left = 3
	normal_box.border_width_top = 3
	normal_box.border_width_right = 3
	normal_box.border_width_bottom = 3
	normal_box.border_color = Color(0.8, 0.65, 0.1, 1) # Oro
	normal_box.corner_radius_top_left = 4
	normal_box.corner_radius_top_right = 4
	normal_box.corner_radius_bottom_left = 4
	normal_box.corner_radius_bottom_right = 4
	
	var hover_box = StyleBoxFlat.new()
	hover_box.bg_color = Color(0.15, 0.15, 0.15, 1)
	hover_box.border_width_left = 3
	hover_box.border_width_top = 3
	hover_box.border_width_right = 3
	hover_box.border_width_bottom = 3
	hover_box.border_color = Color(1.0, 0.9, 0.1, 1) # Oro brillante neón
	hover_box.corner_radius_top_left = 4
	hover_box.corner_radius_top_right = 4
	hover_box.corner_radius_bottom_left = 4
	hover_box.corner_radius_bottom_right = 4
	
	var pressed_box = StyleBoxFlat.new()
	pressed_box.bg_color = Color(0.05, 0.05, 0.05, 1)
	pressed_box.border_width_left = 3
	pressed_box.border_width_top = 3
	pressed_box.border_width_right = 3
	pressed_box.border_width_bottom = 3
	pressed_box.border_color = Color(1.0, 0.9, 0.1, 1)
	pressed_box.corner_radius_top_left = 4
	pressed_box.corner_radius_top_right = 4
	pressed_box.corner_radius_bottom_left = 4
	pressed_box.corner_radius_bottom_right = 4
	
	btn.add_theme_stylebox_override("normal", normal_box)
	btn.add_theme_stylebox_override("hover", hover_box)
	btn.add_theme_stylebox_override("pressed", pressed_box)
	btn.add_theme_stylebox_override("focus", hover_box)
	btn.add_theme_color_override("font_color", Color(1, 0.9, 0.7, 1))
	btn.add_theme_color_override("font_hover_color", Color(1, 1, 0.9, 1))
	
	# Efecto de escala al posar el cursor
	btn.mouse_entered.connect(func():
		var tween = create_tween()
		tween.tween_property(btn, "scale", Vector2(1.05, 1.05), 0.1).set_trans(Tween.TRANS_QUAD)
	)
	btn.mouse_exited.connect(func():
		var tween = create_tween()
		tween.tween_property(btn, "scale", Vector2(1.0, 1.0), 0.1).set_trans(Tween.TRANS_QUAD)
	)

func _style_flag_button(btn: Button):
	btn.custom_minimum_size = Vector2(40, 40)
	btn.size = Vector2(40, 40)
	btn.pivot_offset = Vector2(20, 20) # Pivote centrado para micro-zoom
	btn.flat = true
	btn.add_theme_font_size_override("font_size", 26)
	btn.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	
	# Estilo vacío para evitar bordes ruidosos
	var empty = StyleBoxEmpty.new()
	btn.add_theme_stylebox_override("normal", empty)
	btn.add_theme_stylebox_override("hover", empty)
	btn.add_theme_stylebox_override("pressed", empty)
	btn.add_theme_stylebox_override("focus", empty)
	
	# Micro-animaciones hover
	btn.mouse_entered.connect(func():
		var t = create_tween()
		t.tween_property(btn, "scale", Vector2(1.2, 1.2), 0.15).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	)
	btn.mouse_exited.connect(func():
		var t = create_tween()
		t.tween_property(btn, "scale", Vector2.ONE, 0.15).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	)

func _set_language(lang_code: String):
	current_language = lang_code
	
	# 1. Resaltar visualmente la bandera seleccionada (opacidad premium)
	if _en_flag_btn and _es_flag_btn:
		if current_language == "en":
			_en_flag_btn.modulate.a = 1.0
			_es_flag_btn.modulate.a = 0.4
		else:
			_en_flag_btn.modulate.a = 0.4
			_es_flag_btn.modulate.a = 1.0
			
	# 2. Actualizar el título principal con su tamaño de fuente y colores optimizados por caracteres
	if _menu_node:
		var title_lbl = _menu_node.find_child("MenuTitle", true, false)
		var title_shadow = _menu_node.find_child("MenuTitleShadow", true, false)
		if title_lbl and title_shadow:
			if current_language == "en":
				_rebuild_character_title(title_lbl, "I WAS WHAT YOU ARE\nAND YOU SHALL BE WHAT I AM", _title_font, 48, Color(1.0, 0.85, 0.15, 1.0), Color(0, 0, 0, 1), 12)
				_rebuild_character_title(title_shadow, "I WAS WHAT YOU ARE\nAND YOU SHALL BE WHAT I AM", _title_font, 48, Color(1.0, 0.8, 0.1, 0.9), Color(0.8, 0.4, 0.0, 0.5), 14)
			else:
				_rebuild_character_title(title_lbl, "FUI LO QUE ERES\nY SERÁS LO QUE SOY", _title_font, 52, Color(1.0, 0.85, 0.15, 1.0), Color(0, 0, 0, 1), 12)
				_rebuild_character_title(title_shadow, "FUI LO QUE ERES\nY SERÁS LO QUE SOY", _title_font, 52, Color(1.0, 0.8, 0.1, 0.9), Color(0.8, 0.4, 0.0, 0.5), 14)

func _rebuild_character_title(container: Control, text: String, font: Font, font_size: int, font_color: Color, outline_color: Color, outline_size: int):
	# Limpiar hijos viejos de forma segura
	for child in container.get_children():
		child.queue_free()
		container.remove_child(child)
		
	container.clip_contents = false
	var vbox = VBoxContainer.new()
	vbox.name = "VBox"
	vbox.clip_contents = false
	container.add_child(vbox)
	vbox.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	vbox.alignment = BoxContainer.ALIGNMENT_CENTER
	vbox.add_theme_constant_override("separation", 10)
	
	var lines = text.split("\n")
	for line in lines:
		var hbox = HBoxContainer.new()
		hbox.name = "HBox"
		hbox.clip_contents = false
		hbox.alignment = BoxContainer.ALIGNMENT_CENTER
		hbox.add_theme_constant_override("separation", 2)
		vbox.add_child(hbox)
		
		for i in range(line.length()):
			var char_str = line[i]
			var char_lbl = Label.new()
			char_lbl.text = char_str
			char_lbl.clip_contents = false
			char_lbl.add_theme_font_override("font", font)
			char_lbl.add_theme_font_size_override("font_size", font_size)
			char_lbl.add_theme_color_override("font_color", font_color)
			char_lbl.add_theme_color_override("font_outline_color", outline_color)
			char_lbl.add_theme_constant_override("outline_size", outline_size)
			char_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			char_lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
			
			var size_x = font_size * 0.35 if char_str == " " else font_size * 0.55
			char_lbl.custom_minimum_size = Vector2(size_x, font_size)
			
			# Asegurar pivote al centro exacto en runtime (evita que se expanda hacia un lado específico)
			char_lbl.pivot_offset = Vector2(size_x / 2.0, font_size / 2.0)
			char_lbl.resized.connect(func(): char_lbl.pivot_offset = char_lbl.size / 2.0)
			
			hbox.add_child(char_lbl)
				
		# 3. Actualizar textos de los botones principales del menú
		var play_btn = _menu_node.find_child("PlayButton", true, false)
		if play_btn:
			play_btn.text = "PLAY" if current_language == "en" else "JUGAR"
		var leader_btn = _menu_node.find_child("LeaderboardButton", true, false)
		if leader_btn:
			leader_btn.text = "LEADERBOARDS" if current_language == "en" else "CLASIFICACIÓN"
			
	# 4. Actualizar textos del área de clasificación (Game Over)
	if _classification_area:
		var go_title = _classification_area.find_child("GameOverTitle", true, false)
		if go_title:
			go_title.text = "THE LINEAGE HAS WITHERED" if current_language == "en" else "EL LINAJE SE HA MARCHITADO"
		var name_input = _classification_area.find_child("NameInput", true, false)
		if name_input:
			name_input.placeholder_text = "Enter your name (max 12)..." if current_language == "en" else "Escribe tu nombre (máx. 12)..."
		var submit_btn = _classification_area.find_child("SubmitBtn", true, false)
		if submit_btn:
			submit_btn.text = "REGISTER LINEAGE" if current_language == "en" else "REGISTRAR LINAJE"
		var cancel_btn = _classification_area.find_child("CancelBtn", true, false)
		if cancel_btn:
			cancel_btn.text = "RETURN TO MENU" if current_language == "en" else "VOLVER AL MENÚ"
			
	# 5. Actualizar los marcadores de la partida activa
	update_ui()

func _on_play_pressed():
	# Mostrar los retratos inmediatamente para que se deslicen de forma natural en la pantalla
	in_menu = false
	ancestor.show()
	descendant.show()
	
	# Iniciar transición suave de la cámara hacia el offset de juego actual
	var tween = create_tween()
	tween.tween_property(camera, "position:y", current_game_y_offset, 1.5).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_IN_OUT)
	tween.tween_callback(func():
		# Asegurar que se posicionen de forma instantánea en el centro del ancestro antes de mostrarlos para evitar parpadeos
		var ancestor_center = ancestor.position + ancestor.size / 2.0
		if _tutorial_cursor:
			_tutorial_cursor.position = ancestor_center - Vector2(24, 24)
			_tutorial_cursor.show()
		if _tutorial_line:
			_tutorial_line.clear_points()
			_tutorial_line.add_point(ancestor_center)
			_tutorial_line.add_point(ancestor_center)
			_tutorial_line.show()
	)

func _on_leaderboard_pressed():
	_update_leaderboard_content()
	
	# Colocar el panel exactamente una pantalla por debajo del menú actual y centrado verticalmente
	var menu_y = _menu_node.position.y
	_leaderboard_panel.position = Vector2((1152 - 720) / 2, menu_y + 648.0 + 104.0)
	_leaderboard_panel.show()
	
	# Posicionar el botón de atrás justo a la izquierda de la ventana de clasificaciones
	if _leaderboard_back_btn:
		_leaderboard_back_btn.position = Vector2(152, menu_y + 648.0 + 104.0)
		_leaderboard_back_btn.show()
	
	var tween = create_tween()
	tween.tween_property(camera, "position:y", menu_y + 648.0, 1.5).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_IN_OUT)

func _setup_leaderboard_panel():
	_leaderboard_panel = PanelContainer.new()
	_leaderboard_panel.name = "LeaderboardPanel"
	_leaderboard_panel.custom_minimum_size = Vector2(720, 440)
	_leaderboard_panel.size = Vector2(720, 440)
	_leaderboard_panel.position = Vector2((1152 - 720) / 2, 104)
	add_child(_leaderboard_panel) # Agregar a self para que se dibuje en el espacio del mundo 2D
	_leaderboard_panel.hide() # Inicialmente oculto
	
	# Estilo del panel
	var panel_box = StyleBoxFlat.new()
	panel_box.bg_color = Color(0.08, 0.08, 0.08, 0.96)
	panel_box.border_width_left = 3
	panel_box.border_width_top = 3
	panel_box.border_width_right = 3
	panel_box.border_width_bottom = 3
	panel_box.border_color = Color(0.8, 0.65, 0.1, 1)
	panel_box.corner_radius_top_left = 8
	panel_box.corner_radius_top_right = 8
	panel_box.corner_radius_bottom_left = 8
	panel_box.corner_radius_bottom_right = 8
	_leaderboard_panel.add_theme_stylebox_override("panel", panel_box)
	
	# Inicializar botón de volver atrás como icono redondo en la esquina superior izquierda
	_leaderboard_back_btn = Button.new()
	_leaderboard_back_btn.name = "LeaderboardBackBtn"
	_leaderboard_back_btn.text = "←" # Un icono de flecha hacia la izquierda
	_leaderboard_back_btn.custom_minimum_size = Vector2(52, 52)
	_leaderboard_back_btn.add_theme_font_size_override("font_size", 26)
	_leaderboard_back_btn.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	_leaderboard_back_btn.pivot_offset = Vector2(26, 26)
	
	var back_normal = StyleBoxFlat.new()
	back_normal.bg_color = Color(0.12, 0.04, 0.04, 0.9)
	back_normal.border_width_left = 2
	back_normal.border_width_top = 2
	back_normal.border_width_right = 2
	back_normal.border_width_bottom = 2
	back_normal.border_color = Color(0.8, 0.2, 0.2, 1)
	back_normal.corner_radius_top_left = 26
	back_normal.corner_radius_top_right = 26
	back_normal.corner_radius_bottom_left = 26
	back_normal.corner_radius_bottom_right = 26
	
	var back_hover = StyleBoxFlat.new()
	back_hover.bg_color = Color(0.25, 0.08, 0.08, 0.9)
	back_hover.border_width_left = 2
	back_hover.border_width_top = 2
	back_hover.border_width_right = 2
	back_hover.border_width_bottom = 2
	back_hover.border_color = Color(1.0, 0.35, 0.35, 1)
	back_hover.corner_radius_top_left = 26
	back_hover.corner_radius_top_right = 26
	back_hover.corner_radius_bottom_left = 26
	back_hover.corner_radius_bottom_right = 26
	
	_leaderboard_back_btn.add_theme_stylebox_override("normal", back_normal)
	_leaderboard_back_btn.add_theme_stylebox_override("hover", back_hover)
	_leaderboard_back_btn.add_theme_stylebox_override("pressed", back_normal)
	_leaderboard_back_btn.add_theme_stylebox_override("focus", back_hover)
	_leaderboard_back_btn.add_theme_color_override("font_color", Color(1, 0.8, 0.8, 1))
	
	# Efecto de escala al pasar el ratón
	_leaderboard_back_btn.mouse_entered.connect(func():
		var t = create_tween()
		t.tween_property(_leaderboard_back_btn, "scale", Vector2(1.08, 1.08), 0.15).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	)
	_leaderboard_back_btn.mouse_exited.connect(func():
		var t = create_tween()
		t.tween_property(_leaderboard_back_btn, "scale", Vector2.ONE, 0.15).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	)
	
	# Acción del botón para volver atrás
	_leaderboard_back_btn.pressed.connect(func():
		var menu_y = _menu_node.position.y
		var tween = create_tween()
		tween.tween_property(camera, "position:y", menu_y, 1.5).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_IN_OUT)
		await tween.finished
		_leaderboard_panel.hide()
		_leaderboard_back_btn.hide()
	)
	
	add_child(_leaderboard_back_btn)
	_leaderboard_back_btn.hide()
	
	_update_leaderboard_content()

func _update_leaderboard_content():
	# Limpiar hijos viejos del panel si existen
	for child in _leaderboard_panel.get_children():
		child.queue_free()
		
	# Añadir un MarginContainer para dar holgura y espacio
	var margin_container = MarginContainer.new()
	margin_container.name = "LeaderboardMargin"
	margin_container.add_theme_constant_override("margin_left", 32)
	margin_container.add_theme_constant_override("margin_top", 16)
	margin_container.add_theme_constant_override("margin_right", 32)
	margin_container.add_theme_constant_override("margin_bottom", 16)
	_leaderboard_panel.add_child(margin_container)
	
	var vbox = VBoxContainer.new()
	vbox.name = "LeaderboardVBox"
	vbox.add_theme_constant_override("separation", 10)
	margin_container.add_child(vbox)
	
	# Título
	var header = Label.new()
	header.text = "BEST BLOODLINES" if current_language == "en" else "MEJORES LINAJES"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 32)
	header.add_theme_color_override("font_color", Color(1, 0.9, 0, 1))
	vbox.add_child(header)
	
	# Separador
	var sep = ColorRect.new()
	sep.custom_minimum_size = Vector2(0, 3)
	sep.color = Color(0.8, 0.65, 0.1, 0.4)
	vbox.add_child(sep)
	
	# Cargar récord personal
	_load_high_score()
	
	# Label de Estado de Carga
	var status_lbl = Label.new()
	status_lbl.name = "StatusLabel"
	status_lbl.text = "LOADING GLOBAL BLOODLINES..." if current_language == "en" else "CARGANDO LINAJES GLOBALES..."
	status_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	status_lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	status_lbl.add_theme_font_size_override("font_size", 22)
	status_lbl.add_theme_color_override("font_color", Color(0.9, 0.8, 0.5, 0.8))
	vbox.add_child(status_lbl)
	
	# Efecto de latido suave de carga
	var t = create_tween().set_loops()
	t.tween_property(status_lbl, "modulate:a", 0.3, 0.6).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	t.tween_property(status_lbl, "modulate:a", 0.9, 0.6).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	
	# Realizar la petición GET asíncrona al VPS
	_make_http_request(
		LEADERBOARD_API_URL,
		HTTPClient.METHOD_GET,
		PackedStringArray(["Content-Type: application/json"]),
		"",
		func(result, response_code, response_body):
			# Detener animación de carga y remover status label
			t.kill()
			status_lbl.queue_free()
			
			# Debugging detallado de la petición
			print("[LEADERBOARD DEBUG] GET Request completed.")
			print("[LEADERBOARD DEBUG] Result Code (Godot OK=0): ", result)
			print("[LEADERBOARD DEBUG] Response HTTP Code: ", response_code)
			
			var scores = []
			var success = false
			
			if result == OK and response_code == 200:
				var json = JSON.new()
				var body_text = response_body.get_string_from_utf8()
				print("[LEADERBOARD DEBUG] Response Body: ", body_text)
				if json.parse(body_text) == OK:
					if json.data is Array:
						leaderboard_entries = json.data
						scores = json.data.duplicate()
						success = true
						
						# Guardar caché local
						var file = FileAccess.open("user://leaderboard_v2.dat", FileAccess.WRITE)
						if file:
							file.store_string(JSON.stringify(leaderboard_entries))
							file.close()
				else:
					print("[LEADERBOARD DEBUG] Failed to parse JSON response!")
			
			if success:
				# Renderizar la lista únicamente si la consulta tuvo éxito
				_render_leaderboard_list(vbox, scores)
			else:
				# Mostrar un mensaje de error elegante y detener la visualización de la lista
				print("[LEADERBOARD DEBUG] Leaderboard query failed. Displaying error banner.")
				
				var error_lbl = Label.new()
				error_lbl.text = "THE ORACLE DOES NOT RESPOND\n(CONNECTION FAILED)" if current_language == "en" else "EL ORÁCULO NO RESPONDE\n(CONEXIÓN FALLIDA)"
				error_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
				error_lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
				error_lbl.custom_minimum_size = Vector2(0, 200) # Centrar verticalmente en el panel
				error_lbl.add_theme_font_size_override("font_size", 22)
				error_lbl.add_theme_color_override("font_color", Color(1.0, 0.25, 0.25, 1.0))
				vbox.add_child(error_lbl)
	)

func _render_leaderboard_list(vbox: VBoxContainer, scores: Array):
	# Ordenar de mayor a menor score
	scores.sort_custom(func(a, b): return a["score"] > b["score"])
	
	# Limitar a los mejores 12 registros en la UI para no saturar
	if scores.size() > 12:
		scores.resize(12)
	
	# HBox para alojar la lista scrollable y los botones de navegación de la lista
	var content_hbox = HBoxContainer.new()
	content_hbox.add_theme_constant_override("separation", 24)
	content_hbox.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vbox.add_child(content_hbox)
	
	# ScrollContainer para la lista
	var scroll_container = ScrollContainer.new()
	scroll_container.name = "LeaderboardScroll"
	scroll_container.custom_minimum_size = Vector2(560, 300)
	scroll_container.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll_container.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll_container.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll_container.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_SHOW_NEVER
	content_hbox.add_child(scroll_container)
	
	# VBox dentro del ScrollContainer para las puntuaciones
	var list_vbox = VBoxContainer.new()
	list_vbox.name = "LeaderboardListVBox"
	list_vbox.add_theme_constant_override("separation", 12)
	list_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll_container.add_child(list_vbox)
	
	for i in range(len(scores)):
		var item = scores[i]
		var hbox = HBoxContainer.new()
		hbox.add_theme_constant_override("separation", 20)
		hbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		list_vbox.add_child(hbox)
		
		# 1. Columna de Posición: Ancho fijo de 40px
		var pos_lbl = Label.new()
		pos_lbl.text = str(i + 1) + ". "
		pos_lbl.custom_minimum_size = Vector2(40, 0)
		pos_lbl.add_theme_font_size_override("font_size", 20)
		pos_lbl.add_theme_color_override("font_color", Color(0.6, 0.6, 0.6, 1))
		hbox.add_child(pos_lbl)
		
		# 2. Columna de Nombre: Ancho mínimo de 200px con expansión fill y recorte de texto largo
		var name_lbl = Label.new()
		name_lbl.text = item["name"]
		name_lbl.custom_minimum_size = Vector2(200, 0)
		name_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		name_lbl.clip_text = true
		name_lbl.add_theme_font_size_override("font_size", 20)
		if item["name"] == "Tu Récord" or item["name"] == "Your Record":
			name_lbl.add_theme_color_override("font_color", Color(0.2, 0.8, 1, 1))
		else:
			name_lbl.add_theme_color_override("font_color", Color(0.9, 0.9, 0.9, 1))
		hbox.add_child(name_lbl)
		
		# 3. Columna de Fecha: Ancho fijo de 140px, centrado horizontalmente
		var date_lbl = Label.new()
		date_lbl.text = item.get("date", "17/05/2026")
		date_lbl.custom_minimum_size = Vector2(140, 0)
		date_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		date_lbl.add_theme_font_size_override("font_size", 16)
		date_lbl.add_theme_color_override("font_color", Color(0.5, 0.5, 0.5, 1))
		hbox.add_child(date_lbl)
		
		# 4. Columna de Puntuación (Generación): Ancho de 100px, alineado a la derecha
		var score_lbl = Label.new()
		score_lbl.text = str(int(item["score"])) + " pts"
		score_lbl.custom_minimum_size = Vector2(100, 0)
		score_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		score_lbl.add_theme_font_size_override("font_size", 20)
		if item["name"] == "Tu Récord" or item["name"] == "Your Record":
			score_lbl.add_theme_color_override("font_color", Color(0.2, 0.8, 1, 1))
		else:
			score_lbl.add_theme_color_override("font_color", Color(1, 0.9, 0.5, 1))
		hbox.add_child(score_lbl)
		
	# VBox para los dos botones de navegación de la lista (Subir y Bajar la lista)
	var nav_vbox = VBoxContainer.new()
	nav_vbox.alignment = BoxContainer.ALIGNMENT_CENTER
	nav_vbox.add_theme_constant_override("separation", 16)
	content_hbox.add_child(nav_vbox)
	
	# Botón SUBIR LISTA (▲)
	var list_up_btn = Button.new()
	list_up_btn.text = "▲"
	list_up_btn.custom_minimum_size = Vector2(48, 48)
	list_up_btn.add_theme_font_size_override("font_size", 20)
	list_up_btn.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	list_up_btn.pivot_offset = Vector2(24, 24)
	nav_vbox.add_child(list_up_btn)
	
	# Botón BAJAR LISTA (▼)
	var list_down_btn = Button.new()
	list_down_btn.text = "▼"
	list_down_btn.custom_minimum_size = Vector2(48, 48)
	list_down_btn.add_theme_font_size_override("font_size", 20)
	list_down_btn.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	list_down_btn.pivot_offset = Vector2(24, 24)
	nav_vbox.add_child(list_down_btn)
	
	# Estilos premium para los botones de la lista
	var list_btn_normal = StyleBoxFlat.new()
	list_btn_normal.bg_color = Color(0.12, 0.1, 0.06, 1)
	list_btn_normal.border_width_left = 2
	list_btn_normal.border_width_top = 2
	list_btn_normal.border_width_right = 2
	list_btn_normal.border_width_bottom = 2
	list_btn_normal.border_color = Color(0.7, 0.55, 0.15, 1)
	list_btn_normal.corner_radius_top_left = 6
	list_btn_normal.corner_radius_top_right = 6
	list_btn_normal.corner_radius_bottom_left = 6
	list_btn_normal.corner_radius_bottom_right = 6
	
	var list_btn_hover = StyleBoxFlat.new()
	list_btn_hover.bg_color = Color(0.22, 0.18, 0.1, 1)
	list_btn_hover.border_width_left = 2
	list_btn_hover.border_width_top = 2
	list_btn_hover.border_width_right = 2
	list_btn_hover.border_width_bottom = 2
	list_btn_hover.border_color = Color(0.95, 0.8, 0.25, 1)
	list_btn_hover.corner_radius_top_left = 6
	list_btn_hover.corner_radius_top_right = 6
	list_btn_hover.corner_radius_bottom_left = 6
	list_btn_hover.corner_radius_bottom_right = 6
	
	for btn in [list_up_btn, list_down_btn]:
		btn.add_theme_stylebox_override("normal", list_btn_normal)
		btn.add_theme_stylebox_override("hover", list_btn_hover)
		btn.add_theme_stylebox_override("pressed", list_btn_normal)
		btn.add_theme_stylebox_override("focus", list_btn_hover)
		btn.add_theme_color_override("font_color", Color(0.9, 0.8, 0.5, 1))
		
		# Efecto hover
		btn.mouse_entered.connect(func():
			var t = create_tween()
			t.tween_property(btn, "scale", Vector2(1.08, 1.08), 0.15).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		)
		btn.mouse_exited.connect(func():
			var t = create_tween()
			t.tween_property(btn, "scale", Vector2.ONE, 0.15).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		)
		
	# Conectar botones de navegación para deslizar la lista verticalmente de forma suave
	list_up_btn.pressed.connect(func():
		var t = create_tween()
		t.tween_property(scroll_container, "scroll_vertical", max(0, scroll_container.scroll_vertical - 60), 0.2).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	)
	list_down_btn.pressed.connect(func():
		var max_scroll = list_vbox.size.y - scroll_container.size.y
		var target_scroll = min(max_scroll, scroll_container.scroll_vertical + 60)
		var t = create_tween()
		t.tween_property(scroll_container, "scroll_vertical", target_scroll, 0.2).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	)

func _load_high_score():
	var file_path = "user://high_score_v2.dat"
	if FileAccess.file_exists(file_path):
		var file = FileAccess.open(file_path, FileAccess.READ)
		record_generation = file.get_32()
		file.close()

func _save_high_score(score: int):
	if score > record_generation:
		record_generation = score
		var file_path = "user://high_score_v2.dat"
		var file = FileAccess.open(file_path, FileAccess.WRITE)
		file.store_32(record_generation)
		file.close()

# ==============================================================================
# SISTEMA DE BATERÍA DE SAVIA PREMIUM (MOBILE CHARGER STYLE)
# ==============================================================================

func _setup_battery_ui():
	# Ocultar el sap_label viejo (texto cutre)
	if sap_label:
		sap_label.hide()
		
	# Crear el contenedor de la batería en el CanvasLayer UI
	_battery_bar = Control.new()
	_battery_bar.name = "BatteryBar"
	_battery_bar.size = Vector2(240, 44)
	_battery_bar.position = Vector2(32, 28)
	_battery_bar.pivot_offset = Vector2(0, 22) # Pivote en el borde izquierdo medio para el despliegue elástico
	_battery_bar.scale = Vector2.ZERO # Oculto en escala inicialmente
	_battery_bar.modulate.a = 0.0 # Oculto en opacidad inicialmente
	$UI.add_child(_battery_bar)
	
	_battery_bar.draw.connect(_draw_battery_bar)

func _draw_battery_bar():
	var size = _battery_bar.size
	var width = size.x
	var height = size.y
	
	# 1. Dibujar el terminal positivo (el pezón de la batería a la derecha)
	var tip_width = 8
	var tip_height = 18
	var tip_box = StyleBoxFlat.new()
	tip_box.bg_color = Color(0.8, 0.65, 0.1, 1.0) # Oro
	tip_box.corner_radius_top_right = 4
	tip_box.corner_radius_bottom_right = 4
	_battery_bar.draw_style_box(tip_box, Rect2(Vector2(width - tip_width, (height - tip_height) / 2), Vector2(tip_width, tip_height)))
	
	# 2. Dibujar el marco principal de la batería
	var body_width = width - tip_width - 2
	var frame_box = StyleBoxFlat.new()
	frame_box.bg_color = Color(0.05, 0.05, 0.05, 0.7) # Fondo semi-transparente oscuro
	frame_box.border_width_left = 3
	frame_box.border_width_top = 3
	frame_box.border_width_right = 3
	frame_box.border_width_bottom = 3
	frame_box.border_color = Color(0.8, 0.65, 0.1, 1.0) # Oro
	frame_box.corner_radius_top_left = 6
	frame_box.corner_radius_top_right = 6
	frame_box.corner_radius_bottom_left = 6
	frame_box.corner_radius_bottom_right = 6
	_battery_bar.draw_style_box(frame_box, Rect2(Vector2.ZERO, Vector2(body_width, height)))
	
	# 3. Dibujar los segmentos internos
	var padding = 6
	var max_segments = 10
	var seg_gap = 4
	var available_w = body_width - (padding * 2) - (seg_gap * (max_segments - 1))
	var seg_w = available_w / max_segments
	var seg_h = height - (padding * 2)
	
	# Usar la savia interpolada para lograr el degradado y transición fluidos
	var percentage = _displayed_sap / float(MAX_SAP)
	
	# Definir color dinámico según la carga interpolada
	var seg_color = Color(1.0, 0.9, 0, 1.0) # Oro brillante por defecto (carga alta)
	if percentage < 0.3:
		seg_color = Color(1.0, 0.25, 0.25, 1.0) # Rojo peligro (batería baja)
	elif percentage < 0.6:
		seg_color = Color(1.0, 0.55, 0.1, 1.0) # Naranja advertencia (carga media)
		
	for i in range(max_segments):
		var seg_x = padding + i * (seg_w + seg_gap)
		
		# Calcular escala rítmica para las celdas: por defecto son más pequeñas (scale 0.7)
		# y en el beat se expanden hasta su tamaño anterior de escala 1.0
		var current_seg_scale = lerp(0.7, 1.0, _battery_beat_pulse)
		var scaled_w = seg_w * current_seg_scale
		var scaled_h = seg_h * current_seg_scale
		var offset_x = (seg_w - scaled_w) / 2.0
		var offset_y = (seg_h - scaled_h) / 2.0
		var seg_rect = Rect2(Vector2(seg_x + offset_x, padding + offset_y), Vector2(scaled_w, scaled_h))
		
		var seg_box = StyleBoxFlat.new()
		seg_box.corner_radius_top_left = 2
		seg_box.corner_radius_top_right = 2
		seg_box.corner_radius_bottom_left = 2
		seg_box.corner_radius_bottom_right = 2
		
		# Calcular el nivel de encendido del segmento específico de forma suave (fading líquido)
		var seg_percentage = (percentage - (float(i) / max_segments)) * max_segments
		seg_percentage = clamp(seg_percentage, 0.0, 1.0)
		
		# Interpolar el color entre el fondo apagado (gris oscuro) y el color encendido dinámico
		var empty_color = Color(0.2, 0.2, 0.2, 0.4)
		seg_box.bg_color = empty_color.lerp(seg_color, seg_percentage)
			
		_battery_bar.draw_style_box(seg_box, seg_rect)

# ==============================================================================
# SISTEMA DE COMBO DE GENERACIÓN PREMIUM (ESTILO ARCADE)
# ==============================================================================

func _setup_combo_ui():
	# Ocultar el gen_label viejo (texto cutre)
	if gen_label:
		gen_label.hide()
		
	# Crear el Label de combo de generación neón en la esquina superior derecha
	_generation_combo = Label.new()
	_generation_combo.name = "GenerationCombo"
	_generation_combo.text = "x" + str(generation) + "!"
	_generation_combo.size = Vector2(160, 60)
	_generation_combo.position = Vector2(1152 - 160 - 32, 28) # Margen de 32px (simétrico al de la batería)
	_generation_combo.pivot_offset = Vector2(160, 30) # Pivote en el centro-derecha para escalarse hacia la izquierda de forma natural
	_generation_combo.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_generation_combo.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	
	# Estilo medieval neón dorado: fuente gigante, color oro brillante con borde grueso negro para contrastar
	_generation_combo.add_theme_font_size_override("font_size", 54)
	_generation_combo.add_theme_color_override("font_color", Color(1.0, 0.84, 0.0, 1.0)) # Oro brillante
	_generation_combo.add_theme_color_override("font_outline_color", Color(0, 0, 0, 1)) # Borde negro sólido
	_generation_combo.add_theme_constant_override("outline_size", 16) # Borde extra grueso para estilo arcade/combo
	
	_generation_combo.scale = Vector2.ZERO
	_generation_combo.modulate.a = 0.0
	$UI.add_child(_generation_combo)
	
	# Crear el Label de puntuación real (cuadros verdes recolectados) justo debajo del multiplicador
	_green_score_label = Label.new()
	_green_score_label.name = "GreenScoreLabel"
	_green_score_label.text = "0"
	_green_score_label.size = Vector2(160, 48)
	_green_score_label.position = Vector2(1152 - 160 - 32, 92) # Situado justo debajo del combo (28 + 64 = 92)
	_green_score_label.pivot_offset = Vector2(160, 24)
	_green_score_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_green_score_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	
	# Estilo neón verde savia
	_green_score_label.add_theme_font_size_override("font_size", 38)
	_green_score_label.add_theme_color_override("font_color", Color(0.1, 0.9, 0.1, 1.0)) # Verde savia brillante
	_green_score_label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 1)) # Borde negro sólido
	_green_score_label.add_theme_constant_override("outline_size", 12)
	
	_green_score_label.scale = Vector2.ZERO
	_green_score_label.modulate.a = 0.0
	$UI.add_child(_green_score_label)

# ==============================================================================
# SISTEMA DE FIN DE JUEGO (GAME OVER) PREMIUM CON REGISTRO DE HISTORIA
# ==============================================================================

func _setup_classification_area():
	_classification_area = Control.new()
	_classification_area.name = "ClassificationArea"
	_classification_area.custom_minimum_size = Vector2(1152, 648)
	_classification_area.size = Vector2(1152, 648)
	
	# Centrar el contenido usando un VBoxContainer
	var vbox = VBoxContainer.new()
	vbox.name = "VBox"
	vbox.custom_minimum_size = Vector2(560, 440)
	vbox.size = Vector2(560, 440)
	vbox.position = Vector2((1152 - 560) / 2, (648 - 440) / 2)
	vbox.add_theme_constant_override("separation", 24)
	_classification_area.add_child(vbox)
	
	# Título medieval neón vibrante rojo sangre
	var title = Label.new()
	title.name = "GameOverTitle"
	title.text = "EL LINAJE SE HA MARCHITADO"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 34)
	title.add_theme_color_override("font_color", Color(1.0, 0.2, 0.2, 1.0))
	title.add_theme_color_override("font_outline_color", Color(0, 0, 0, 1))
	title.add_theme_constant_override("outline_size", 14)
	vbox.add_child(title)
	
	# Puntuación alcanzada
	var score_lbl = Label.new()
	score_lbl.name = "ScoreLabel"
	score_lbl.text = "Llegaste a la Generación " + str(generation)
	score_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	score_lbl.add_theme_font_size_override("font_size", 24)
	score_lbl.add_theme_color_override("font_color", Color(0.95, 0.85, 0.6, 1.0)) # Elegante oro pálido
	score_lbl.add_theme_color_override("font_outline_color", Color(0, 0, 0, 1))
	score_lbl.add_theme_constant_override("outline_size", 8)
	vbox.add_child(score_lbl)
	
	# Input de nombre LineEdit
	var name_input = LineEdit.new()
	name_input.name = "NameInput"
	name_input.placeholder_text = "Escribe tu nombre (máx. 12)..."
	name_input.max_length = 12
	name_input.alignment = HORIZONTAL_ALIGNMENT_CENTER
	name_input.custom_minimum_size = Vector2(320, 48)
	name_input.add_theme_font_size_override("font_size", 20)
	
	var input_style = StyleBoxFlat.new()
	input_style.bg_color = Color(0.06, 0.01, 0.01, 0.8)
	input_style.border_width_left = 2
	input_style.border_width_right = 2
	input_style.border_width_top = 2
	input_style.border_width_bottom = 2
	input_style.border_color = Color(0.5, 0.15, 0.15, 1.0)
	input_style.corner_radius_top_left = 6
	input_style.corner_radius_top_right = 6
	input_style.corner_radius_bottom_left = 6
	input_style.corner_radius_bottom_right = 6
	name_input.add_theme_stylebox_override("normal", input_style)
	name_input.add_theme_stylebox_override("focus", input_style)
	
	var center = CenterContainer.new()
	center.add_child(name_input)
	vbox.add_child(center)
	
	# Botón de registro
	var submit_btn = Button.new()
	submit_btn.name = "SubmitBtn"
	submit_btn.text = "REGISTRAR LINAJE"
	submit_btn.custom_minimum_size = Vector2(280, 52)
	submit_btn.add_theme_font_size_override("font_size", 22)
	submit_btn.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	
	# Estilos del botón
	var btn_normal = StyleBoxFlat.new()
	btn_normal.bg_color = Color(0.18, 0.03, 0.03, 1.0)
	btn_normal.border_width_left = 2
	btn_normal.border_width_right = 2
	btn_normal.border_width_top = 2
	btn_normal.border_width_bottom = 2
	btn_normal.border_color = Color(0.85, 0.2, 0.2, 1.0)
	btn_normal.corner_radius_top_left = 6
	btn_normal.corner_radius_top_right = 6
	btn_normal.corner_radius_bottom_left = 6
	btn_normal.corner_radius_bottom_right = 6
	
	var btn_hover = StyleBoxFlat.new()
	btn_hover.bg_color = Color(0.3, 0.05, 0.05, 1.0)
	btn_hover.border_width_left = 2
	btn_hover.border_width_right = 2
	btn_hover.border_width_top = 2
	btn_hover.border_width_bottom = 2
	btn_hover.border_color = Color(1.0, 0.35, 0.35, 1.0)
	btn_hover.corner_radius_top_left = 6
	btn_hover.corner_radius_top_right = 6
	btn_hover.corner_radius_bottom_left = 6
	btn_hover.corner_radius_bottom_right = 6
	
	submit_btn.add_theme_stylebox_override("normal", btn_normal)
	submit_btn.add_theme_stylebox_override("hover", btn_hover)
	submit_btn.add_theme_stylebox_override("pressed", btn_normal)
	submit_btn.add_theme_stylebox_override("focus", btn_normal)
	
	var btn_center = CenterContainer.new()
	btn_center.add_child(submit_btn)
	vbox.add_child(btn_center)
	
	# Animación hover botón
	submit_btn.mouse_entered.connect(func():
		var t = create_tween()
		t.tween_property(submit_btn, "scale", Vector2(1.04, 1.04), 0.15).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	)
	submit_btn.mouse_exited.connect(func():
		var t = create_tween()
		t.tween_property(submit_btn, "scale", Vector2.ONE, 0.15).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	)
	
	submit_btn.pressed.connect(_on_submit_pressed)
	
	# Botón de volver al menú (Cancelar)
	var cancel_btn = Button.new()
	cancel_btn.name = "CancelBtn"
	cancel_btn.text = "RETURN TO MENU" if current_language == "en" else "VOLVER AL MENÚ"
	cancel_btn.custom_minimum_size = Vector2(280, 44)
	cancel_btn.add_theme_font_size_override("font_size", 18)
	cancel_btn.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	
	# Estilos del botón cancelar (Estilo gris oscuro y discreto, pero premium)
	var cancel_normal = StyleBoxFlat.new()
	cancel_normal.bg_color = Color(0.12, 0.12, 0.12, 0.8)
	cancel_normal.border_width_left = 1
	cancel_normal.border_width_right = 1
	cancel_normal.border_width_top = 1
	cancel_normal.border_width_bottom = 1
	cancel_normal.border_color = Color(0.4, 0.4, 0.4, 0.8)
	cancel_normal.corner_radius_top_left = 6
	cancel_normal.corner_radius_top_right = 6
	cancel_normal.corner_radius_bottom_left = 6
	cancel_normal.corner_radius_bottom_right = 6
	
	var cancel_hover = StyleBoxFlat.new()
	cancel_hover.bg_color = Color(0.2, 0.2, 0.2, 0.9)
	cancel_hover.border_width_left = 1
	cancel_hover.border_width_right = 1
	cancel_hover.border_width_top = 1
	cancel_hover.border_width_bottom = 1
	cancel_hover.border_color = Color(0.6, 0.6, 0.6, 1.0)
	cancel_hover.corner_radius_top_left = 6
	cancel_hover.corner_radius_top_right = 6
	cancel_hover.corner_radius_bottom_left = 6
	cancel_hover.corner_radius_bottom_right = 6
	
	cancel_btn.add_theme_stylebox_override("normal", cancel_normal)
	cancel_btn.add_theme_stylebox_override("hover", cancel_hover)
	cancel_btn.add_theme_stylebox_override("pressed", cancel_normal)
	cancel_btn.add_theme_stylebox_override("focus", cancel_normal)
	
	var cancel_center = CenterContainer.new()
	cancel_center.add_child(cancel_btn)
	vbox.add_child(cancel_center)
	
	# Animación hover botón cancelar
	cancel_btn.mouse_entered.connect(func():
		var t = create_tween()
		t.tween_property(cancel_btn, "scale", Vector2(1.04, 1.04), 0.15).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	)
	cancel_btn.mouse_exited.connect(func():
		var t = create_tween()
		t.tween_property(cancel_btn, "scale", Vector2.ONE, 0.15).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	)
	
	cancel_btn.pressed.connect(_on_back_to_menu_pressed)
	
	_classification_area.hide()
	add_child(_classification_area)

func _on_submit_pressed():
	var name_input = _classification_area.find_child("NameInput", true, false)
	var player_name = "Player" if current_language == "en" else "Jugador"
	if name_input and name_input.text.strip_edges() != "":
		player_name = name_input.text.strip_edges()
		
	# Guardar puntuación (Savia recolectada * Generaciones) en la lista persistente
	var final_score = green_squares_collected * generation
	_submit_player_score(player_name, final_score)
	
	var submit_btn = _classification_area.find_child("SubmitBtn", true, false)
	if submit_btn:
		submit_btn.disabled = true
		
	# Calcular la nueva posición Y del menú principal (un alto de pantalla debajo de la cámara actual)
	var new_menu_y = camera.position.y + 648.0
	
	# Reposicionar el Menú Principal
	_menu_node.position = Vector2(0, new_menu_y)
	
	# Resetear el estado del juego en-situ (limpieza, reseteo de offset y reposicionamiento de padres)
	_reset_game_state_to_menu(new_menu_y)
	
	# Transición premium: la cámara desciende al nuevo menú principal mientras el área de clasificación se desvanece
	var t = create_tween().set_parallel(true)
	t.tween_property(camera, "position:y", new_menu_y, 1.5).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_IN_OUT)
	t.tween_property(_classification_area, "modulate:a", 0.0, 1.0).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	
	await t.finished
	_classification_area.hide()
	
	# Reestablecer el botón y campo de texto para la siguiente partida
	if submit_btn:
		submit_btn.disabled = false
	if name_input:
		name_input.text = ""

func _on_back_to_menu_pressed():
	var cancel_btn = _classification_area.find_child("CancelBtn", true, false)
	if cancel_btn:
		cancel_btn.disabled = true
		
	# Calcular la nueva posición Y del menú principal (un alto de pantalla debajo de la cámara actual)
	var new_menu_y = camera.position.y + 648.0
	
	# Reposicionar el Menú Principal
	_menu_node.position = Vector2(0, new_menu_y)
	
	# Resetear el estado del juego en-situ (limpieza, reseteo de offset y reposicionamiento de padres)
	_reset_game_state_to_menu(new_menu_y)
	
	# Transición premium: la cámara desciende al nuevo menú principal mientras el área de clasificación se desvanece
	var t = create_tween().set_parallel(true)
	t.tween_property(camera, "position:y", new_menu_y, 1.5).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_IN_OUT)
	t.tween_property(_classification_area, "modulate:a", 0.0, 1.0).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	
	await t.finished
	_classification_area.hide()
	
	# Reestablecer el botón y campo de texto para la siguiente partida
	if cancel_btn:
		cancel_btn.disabled = false
	var name_input = _classification_area.find_child("NameInput", true, false)
	if name_input:
		name_input.text = ""

func _reset_game_state_to_menu(new_menu_y: float):
	# 1. Resetear variables de juego
	generation = 1
	sap = MAX_SAP
	_displayed_sap = MAX_SAP
	first_union_made = false
	game_over = false
	in_menu = true
	is_drawing = false
	is_retracting = false
	waiting_for_next = false
	camera_speed = 15.0
	
	if _leaderboard_panel: _leaderboard_panel.hide()
	if _leaderboard_back_btn: _leaderboard_back_btn.hide()
	
	# 2. Resetear offset de juego a un alto de pantalla abajo del nuevo menú
	current_game_y_offset = new_menu_y + 648.0
	
	# 3. Limpiar raíces viejas
	for child in roots_container.get_children():
		# Mantener el root_line principal pero limpiar sus puntos
		if child == root_line:
			root_line.default_color = Color(1, 0.9, 0, 1)
			root_line.points = []
		else:
			child.queue_free()
			
	all_previous_paths.clear()
	current_path.clear()
	
	# 4. Limpiar obstáculos viejos
	for obs in obstacles.get_children():
		obs.queue_free()
		
	# 5. Reposicionar y reactivar ancestro y descendiente
	ancestor.size = Vector2(GRID_SIZE * 3, GRID_SIZE * 3)
	descendant.size = Vector2(GRID_SIZE * 3, GRID_SIZE * 3)
	
	ancestor.position = Vector2(192 - GRID_SIZE, current_game_y_offset + 256.0 - GRID_SIZE)
	descendant.position = Vector2(896 - GRID_SIZE, current_game_y_offset + 256.0 - GRID_SIZE)
	
	ancestor.active = true
	descendant.active = true
	ancestor.hide()
	descendant.hide()
	# Restaurar colores originales neón vibrantes
	ancestor.color = Color(0, 0.8, 1, 1)
	descendant.color = Color(1, 0, 0.8, 1)
	
	# Inicializar punto de partida de la raíz
	var center_pos = ancestor.position + ancestor.size / 2.0
	var start_pos = get_grid_pos(center_pos)
	current_path.append(start_pos)
	root_line.points = current_path
	
	# 6. Recrear tutorial visual limpio
	if _tutorial_line: _tutorial_line.queue_free()
	if _tutorial_cursor: _tutorial_cursor.queue_free()
	
	_tutorial_line = Line2D.new()
	_tutorial_line.name = "TutorialLine"
	_tutorial_line.width = 6.0
	_tutorial_line.default_color = Color(1, 0.9, 0, 0.4)
	_tutorial_line.joint_mode = Line2D.LINE_JOINT_ROUND
	_tutorial_line.begin_cap_mode = Line2D.LINE_CAP_ROUND
	_tutorial_line.end_cap_mode = Line2D.LINE_CAP_ROUND
	add_child(_tutorial_line)
	_tutorial_line.hide()
	
	_tutorial_cursor = Label.new()
	_tutorial_cursor.name = "TutorialCursor"
	_tutorial_cursor.text = "👉"
	_tutorial_cursor.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_tutorial_cursor.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_tutorial_cursor.add_theme_font_size_override("font_size", 48)
	_tutorial_cursor.pivot_offset = Vector2(24, 24)
	add_child(_tutorial_cursor)
	_tutorial_cursor.hide()
	
	_tutorial_cursor.position = (ancestor.position + ancestor.size / 2.0) - Vector2(24, 24)
	
	# 7. Ocultar la UI de batería y combo elásticamente para el nuevo inicio
	if _battery_bar:
		_battery_bar.scale = Vector2.ZERO
		_battery_bar.modulate.a = 0.0
	if _generation_combo:
		_generation_combo.scale = Vector2.ZERO
		_generation_combo.modulate.a = 0.0
	if _green_score_label:
		_green_score_label.text = "0"
		_green_score_label.scale = Vector2.ZERO
		_green_score_label.modulate.a = 0.0
	green_squares_collected = 0
		
	# Actualizar UI
	update_ui()

func _submit_player_score(player_name: String, player_score: int):
	var final_name = player_name.strip_edges()
	if final_name == "":
		final_name = "Unnamed" if current_language == "en" else "Sin Nombre"
		
	# Obtener fecha actual
	var d = Time.get_date_dict_from_system()
	var date_str = "%02d/%02d/%04d" % [d.day, d.month, d.year]
	
	# A. Registrar localmente como respaldo/caché (¡UX premium robusta!)
	var local_exists = false
	for entry in leaderboard_entries:
		if entry["name"] == final_name and entry["score"] == player_score:
			local_exists = true
			break
	if not local_exists:
		leaderboard_entries.append({"name": final_name, "score": player_score, "date": date_str})
		leaderboard_entries.sort_custom(func(a, b): return a["score"] > b["score"])
		if leaderboard_entries.size() > 8:
			leaderboard_entries.resize(8)
		var file = FileAccess.open("user://leaderboard_v2.dat", FileAccess.WRITE)
		if file:
			var json_str = JSON.stringify(leaderboard_entries)
			file.store_string(json_str)
			file.close()

	if player_score > record_generation:
		record_generation = player_score
		var r_file = FileAccess.open("user://high_score_v2.dat", FileAccess.WRITE)
		if r_file:
			r_file.store_32(record_generation)
			r_file.close()

	# B. Enviar asíncronamente al VPS (Servidor Global)
	var body_dict = {"name": final_name, "score": player_score}
	var body_json = JSON.stringify(body_dict)
	var headers = PackedStringArray([
		"Content-Type: application/json",
		"X-Game-Key: " + LEADERBOARD_API_KEY
	])
	
	_make_http_request(
		LEADERBOARD_API_URL,
		HTTPClient.METHOD_POST,
		headers,
		body_json,
		func(result, response_code, response_body):
			print("[LEADERBOARD DEBUG] POST Request completed.")
			print("[LEADERBOARD DEBUG] Result Code (Godot OK=0): ", result)
			print("[LEADERBOARD DEBUG] Response HTTP Code: ", response_code)
			print("[LEADERBOARD DEBUG] Response Body: ", response_body.get_string_from_utf8())
			if result == OK and (response_code == 200 or response_code == 201):
				print("Puntuación subida con éxito al VPS.")
			else:
				print("No se pudo subir al VPS (Código: ", response_code, "). Guardado localmente como respaldo.")
	)

func _load_leaderboard_entries():
	var file_path = "user://leaderboard_v2.dat"
	if FileAccess.file_exists(file_path):
		var file = FileAccess.open(file_path, FileAccess.READ)
		if file:
			var json_str = file.get_as_text()
			file.close()
			var json = JSON.new()
			if json.parse(json_str) == OK:
				leaderboard_entries = json.data
				return
				
	# Iniciar vacío para la versión 2 (sistema de puntos arcade)
	leaderboard_entries = []

func _make_http_request(url: String, method: HTTPClient.Method, headers: PackedStringArray, body: String, callback: Callable):
	var http_node = HTTPRequest.new()
	add_child(http_node)
	http_node.request_completed.connect(func(result, response_code, response_headers, response_body):
		callback.call(result, response_code, response_body)
		http_node.queue_free()
	)
	var err = http_node.request(url, headers, method, body)
	if err != OK:
		callback.call(1, 0, PackedByteArray()) # Result error
		http_node.queue_free()
