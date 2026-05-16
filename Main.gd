extends Node2D

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

func _ready():
	randomize()
	
	rewards_container = Node.new()
	rewards_container.name = "Rewards"
	add_child(rewards_container)
	
	# Redimensionar elementos iniciales para 3x3 celdas (retratos grandes)
	ancestor.size = Vector2(GRID_SIZE * 3, GRID_SIZE * 3)
	descendant.size = Vector2(GRID_SIZE * 3, GRID_SIZE * 3)
	
	# Asegurar que los retratos siempre se dibujen por encima de las raíces
	ancestor.z_index = 10
	descendant.z_index = 10
	
	# Centrar los recuadros originales para que no se desplacen raro al crecer
	ancestor.position -= Vector2(GRID_SIZE, GRID_SIZE)
	descendant.position -= Vector2(GRID_SIZE, GRID_SIZE)
	
	root_line.width = GRID_SIZE * 0.4
	
	var center_pos = ancestor.position + ancestor.size / 2.0
	var start_pos = get_grid_pos(center_pos)
	current_path.append(start_pos)
	root_line.points = current_path
	update_ui()

func _process(delta):
	if game_over:
		return
		
	# Procesamiento continuo de dibujo o retracción
	if is_drawing:
		try_add_point(get_global_mouse_position())
	elif is_retracting:
		retract_root()
		
	if not waiting_for_next:
		# Mover cámara implacablemente hacia abajo
		camera.position.y += camera_speed * delta
		
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

func retract_root():
	if game_over or waiting_for_next:
		return
		
	# Retraer un punto cada frame (60 puntos por segundo), muy rápido
	# pero asegurándose de no borrar el punto de inicio (el ancestro)
	if current_path.size() > 1:
		current_path.remove_at(current_path.size() - 1)
		sap += 1
		sap_label.text = "Savia: " + str(sap)
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
	if game_over or waiting_for_next:
		return
		
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT:
			if event.pressed:
				var mouse_grid_pos = get_grid_pos(get_global_mouse_position())
				var last_grid_pos = get_grid_pos(current_path[-1])
				
				# Quitar restricción de distancia inicial. En velocidades altas es muy difícil acertar 
				# el clic exacto. Si el jugador hace clic, asumimos que quiere continuar la raíz.
				is_drawing = true
				is_retracting = false # Prioridad al dibujo si se pulsa
				try_add_point(get_global_mouse_position())
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
	for obs in obstacles.get_children():
		if obs is ColorRect:
			var rect = Rect2(obs.position, obs.size)
			if rect.has_point(pos):
				return true
	return false

func check_win_condition(pos: Vector2) -> bool:
	var target_rect = Rect2(descendant.position, descendant.size)
	if target_rect.has_point(pos):
		trigger_game_over(true)
		return true
	return false

func update_ui():
	sap_label.text = "Savia: " + str(sap)
	gen_label.text = "Generación: " + str(generation)

func trigger_game_over(win: bool, out_of_bounds: bool = false):
	is_drawing = false # <--- FIX: Cortar el dibujo activo inmediatamente
	is_retracting = false
	
	if win:
		camera_speed += 5.0 # Acelerar un poco la cámara con cada victoria
		start_next_generation()
	else:
		game_over = true
		if out_of_bounds:
			message_label.text = "EL LINAJE HA QUEDADO ATRÁS"
		else:
			message_label.text = "EL LINAJE SE HA MARCHITADO"
			
		message_label.modulate = Color(1, 0, 0)
		message_label.show()

func start_next_generation():
	waiting_for_next = false
	
	# Guardar la ruta actual en el historial de colisiones
	all_previous_paths.append_array(current_path)
	
	# Cambiar color de raíces y retratos antiguos a un tono oscuro gradualmente usando un Tween
	var tween = create_tween()
	tween.set_parallel(true)
	tween.tween_property(root_line, "default_color", Color(0.6, 0.5, 0, 1), 1.0)
	tween.tween_property(ancestor, "color", ancestor.color.darkened(0.5), 1.0)
	tween.tween_property(descendant, "color", descendant.color.darkened(0.5), 1.0)
	
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
	
	var child = ColorRect.new()
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
	
	# Hacemos que los últimos bloques de la raíz justo encima del hijo NO sean sólidos
	# Esto permite al jugador hacer clic por encima del retrato sin golpear una "pared invisible"
	for y in range(start_y_grid, end_y_grid - 2):
		var pos = get_grid_pos(Vector2(branch_x_grid * GRID_SIZE, y * GRID_SIZE))
		all_previous_paths.append(pos)
	# Instanciar a la nueva Pareja (ya no en la misma línea estricta)
	var new_partner = ColorRect.new()
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
