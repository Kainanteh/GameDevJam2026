from flask import Flask, request, jsonify
from flask_cors import CORS
from game_state import game_manager
import time

app = Flask(__name__)
CORS(app)

@app.route('/api/update_game', methods=['POST'])
def update_game():
    try:
        data = request.get_json()
        game_id = data.get('game_id')
        
        if not game_id:
            return jsonify({"error": "No game_id provided"}), 400
        
        game_manager.update_game(game_id)
        
        return jsonify({
            "status": "success",
            "message": f"Game updated to: {game_id}",
            "current_game": game_manager.current_game,
            "previous_game": game_manager.previous_game,
            "needs_update": True
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_current_game', methods=['GET'])
def get_current_game():
    try:
        state = game_manager.get_game_state()
        return jsonify(state)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/check_updates', methods=['GET'])
def check_updates():
    try:
        needs_update = game_manager.check_updates()
        current_game = game_manager.current_game
        
        return jsonify({
            "needs_update": needs_update,
            "current_game": current_game,
            "timestamp": time.time()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/confirm_update', methods=['POST'])
def confirm_update():
    try:
        game_manager.confirm_update()
        return jsonify({
            "status": "success",
            "message": "Update confirmed",
            "needs_update": False
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reset_games', methods=['POST'])
def reset_games():
    try:
        game_manager.reset_games()
        return jsonify({
            "status": "success", 
            "message": "Game state reset successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "active", 
        "service": "interludiothumbnail",
        "current_game": game_manager.current_game,
        "needs_update": game_manager.needs_update
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007, debug=True, threaded=True)