<?php
/**
 * Crux Noctis - Global Leaderboard Backend (PHP Edition)
 * Place this file on your VPS web root (e.g. /var/www/html/leaderboard.php)
 * Stores scores securely in a portable JSON file.
 */

// 1. Configuración de Cabeceras CORS (Permite consultas desde cualquier plataforma y exportaciones Web/HTML5)
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Headers: Content-Type, X-Game-Key");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Content-Type: application/json; charset=UTF-8");

// 2. Clave secreta anti-trampas (Debe coincidir con la de Godot)
define("GAME_SECRET_KEY", "crux-noctis-2026-key");
define("DATA_FILE", "scores.json");

// Manejo de peticiones de tipo OPTIONS (Preflight de CORS en navegadores Web)
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

$method = $_SERVER['REQUEST_METHOD'];

// ==============================================================================
// METODO GET: Obtener las mejores puntuaciones
// ==============================================================================
if ($method === 'GET') {
    // ✅ NUEVO: Permite al administrador/desarrollador reiniciar las puntuaciones de forma segura desde el navegador
    if (isset($_GET['clear']) && isset($_GET['key']) && $_GET['key'] === GAME_SECRET_KEY) {
        if (file_exists(DATA_FILE)) {
            unlink(DATA_FILE);
        }
        echo json_encode(["status" => "success", "message" => "Clasificaciones globales reiniciadas correctamente."]);
        exit();
    }

    $scores = [];
    if (file_exists(DATA_FILE)) {
        $json_data = file_get_contents(DATA_FILE);
        $scores = json_decode($json_data, true);
        if (!is_array($scores)) {
            $scores = [];
        }
    }
    
    // Devolver las mejores 50 puntuaciones ordenadas descendentemente
    usort($scores, function($a, $b) {
        return $b['score'] - $a['score'];
    });
    $scores = array_slice($scores, 0, 50);
    
    echo json_encode($scores);
    exit();
}

// ==============================================================================
// METODO POST: Registrar una nueva puntuación
// ==============================================================================
if ($method === 'POST') {
    // A. Validar la clave de seguridad del juego (X-Game-Key)
    $client_key = '';
    
    // 1. Intentar obtener la cabecera directamente desde el superglobal $_SERVER (100% compatible con Nginx y PHP-FPM)
    if (isset($_SERVER['HTTP_X_GAME_KEY'])) {
        $client_key = $_SERVER['HTTP_X_GAME_KEY'];
    }
    
    // 2. Si no está en $_SERVER, intentar usar getallheaders() si la función existe en el entorno
    if (empty($client_key) && function_exists('getallheaders')) {
        $headers = getallheaders();
        if (isset($headers['X-Game-Key'])) {
            $client_key = $headers['X-Game-Key'];
        }
    }
    
    if ($client_key !== GAME_SECRET_KEY) {
        http_response_code(403);
        echo json_encode(["error" => "No autorizado. Firma de juego incorrecta."]);
        exit();
    }
    
    // B. Leer y parsear los datos recibidos en el cuerpo (JSON)
    $input_json = file_get_contents('php://input');
    $data = json_decode($input_json, true);
    
    if (!$data || !isset($data['name']) || !isset($data['score'])) {
        http_response_code(400);
        echo json_encode(["error" => "Datos inválidos o incompletos."]);
        exit();
    }
    
    // C. Sanitizar y validar los campos recibidos
    $name = trim(strip_tags($data['name']));
    
    // Limitar a 12 caracteres máximo de forma ultra-portátil (evita cuelgues si php-mbstring no está instalado en el VPS)
    if (function_exists('mb_substr')) {
        $name = mb_substr($name, 0, 12);
    } else {
        $name = substr($name, 0, 12);
    }
    
    if (empty($name)) {
        $name = "Unnamed";
    }
    
    $score = intval($data['score']);
    if ($score < 0) {
        $score = 0;
    }
    
    // Obtener la fecha del sistema (formato dd/mm/YYYY)
    $date = date("d/m/Y");
    
    // D. Cargar base de datos JSON local
    $scores = [];
    if (file_exists(DATA_FILE)) {
        $json_data = file_get_contents(DATA_FILE);
        $scores = json_decode($json_data, true);
        if (!is_array($scores)) {
            $scores = [];
        }
    }
    
    // E. Añadir o Actualizar la puntuación del jugador (Récord Único por Nombre)
    $existing_index = -1;
    for ($i = 0; $i < count($scores); $i++) {
        // Hacemos una comparación insensible a mayúsculas/minúsculas para evitar duplicados como "Kain" y "kain"
        if (strcasecmp($scores[$i]['name'], $name) === 0) {
            $existing_index = $i;
            break;
        }
    }
    
    if ($existing_index !== -1) {
        // Si el jugador ya existe, solo actualizamos si la nueva puntuación es SUPERIOR a su récord anterior
        if ($score > $scores[$existing_index]['score']) {
            $scores[$existing_index]['score'] = $score;
            $scores[$existing_index]['date'] = $date;
            // Aseguramos que se guarde con la grafía del nombre más reciente
            $scores[$existing_index]['name'] = $name; 
        }
    } else {
        // Si es un jugador nuevo, lo añadimos directamente
        $scores[] = [
            "name" => $name,
            "score" => $score,
            "date" => $date
        ];
    }
    
    // F. Ordenar descendentemente por puntuación
    usort($scores, function($a, $b) {
        return $b['score'] - $a['score'];
    });
    
    // Mantener un historial general de máximo 50 puntuaciones (óptimo para la UI del juego)
    if (count($scores) > 50) {
        $scores = array_slice($scores, 0, 50);
    }
    
    // G. Guardar a disco con Bloqueo de Escritura Exclusivo (LOCK_EX)
    // Esto previene al 100% que múltiples peticiones simultáneas corrompan el archivo JSON
    $json_content = json_encode($scores, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
    if (file_put_contents(DATA_FILE, $json_content, LOCK_EX) === false) {
        http_response_code(500);
        echo json_encode(["error" => "Error de escritura en el servidor."]);
        exit();
    }
    
    echo json_encode(["status" => "success", "message" => "Puntuación registrada con éxito."]);
    exit();
}

// Si llega otra solicitud no soportada
http_response_code(405);
echo json_encode(["error" => "Método no permitido."]);
