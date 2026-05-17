import time
import threading

class GameStateManager:
    def __init__(self):
        self.current_game = None
        self.previous_game = None
        self.last_update = None
        self.lock = threading.Lock()
        self.needs_update = False
    
    def update_game(self, game_id):
        with self.lock:
            if self.current_game and self.current_game != game_id:
                self.previous_game = self.current_game
            
            self.current_game = game_id
            self.last_update = time.time()
            self.needs_update = True
            print(f"🎮 Game updated: {game_id} (needs_update: True)")
    
    def get_game_state(self):
        with self.lock:
            return {
                "current_game": self.current_game,
                "previous_game": self.previous_game,
                "last_update": self.last_update,
                "needs_update": self.needs_update
            }
    
    def check_updates(self):
        with self.lock:
            needs = self.needs_update
            return needs
    
    def confirm_update(self):
        with self.lock:
            self.needs_update = False
            print(f"✅ Update confirmed (needs_update: False)")
    
    def reset_games(self):
        with self.lock:
            self.current_game = None
            self.previous_game = None
            self.last_update = None
            self.needs_update = False
            return True

game_manager = GameStateManager()