"""
Game session management for multiplayer Kings in the Corner.
This module handles game state persistence and multiplayer session management.
"""
import json
import time
from typing import Dict, Optional, List
from game import KingsCornerGame
from cards import Card, Suit


class GameSessionManager:
    """Manages game sessions for multiplayer gameplay."""
    
    def __init__(self):
        # In-memory storage for game sessions
        # In production, this would be replaced with Redis or a database
        self._games: Dict[str, KingsCornerGame] = {}
        self._player_sessions: Dict[str, str] = {}  # player_id -> game_id
        self._last_activity: Dict[str, float] = {}  # game_id -> timestamp
        self.session_timeout = 3600  # 1 hour timeout
    
    def create_game(self, creator_name: str) -> tuple[str, str]:
        """Create a new game and return (game_id, player_id)."""
        game = KingsCornerGame()
        player_id = game.add_player(creator_name)
        
        self._games[game.game_id] = game
        self._player_sessions[player_id] = game.game_id
        self._last_activity[game.game_id] = time.time()
        
        return game.game_id, player_id
    
    def join_game(self, game_id: str, player_name: str) -> Optional[str]:
        """Join an existing game and return player_id."""
        game = self._games.get(game_id)
        if not game:
            return None
        
        try:
            player_id = game.add_player(player_name)
            self._player_sessions[player_id] = game_id
            self._last_activity[game_id] = time.time()
            return player_id
        except ValueError:
            return None
    
    def get_game(self, game_id: str) -> Optional[KingsCornerGame]:
        """Get a game by ID."""
        self._cleanup_expired_games()
        game = self._games.get(game_id)
        if game:
            self._last_activity[game_id] = time.time()
        return game
    
    def get_player_game(self, player_id: str) -> Optional[KingsCornerGame]:
        """Get the game a player is in."""
        game_id = self._player_sessions.get(player_id)
        if game_id:
            return self.get_game(game_id)
        return None
    
    def start_game(self, game_id: str, player_id: str) -> bool:
        """Start a game."""
        game = self.get_game(game_id)
        if not game:
            return False
        
        try:
            game.start_game()
            self._last_activity[game_id] = time.time()
            return True
        except ValueError:
            return False
    
    def play_card(self, player_id: str, rank: str, suit_symbol: str, pile_name: str) -> tuple[bool, str]:
        """Play a card."""
        game = self.get_player_game(player_id)
        if not game:
            return False, "Game not found"
        
        # Convert suit symbol back to Suit enum
        suit_map = {"♥": Suit.HEARTS, "♦": Suit.DIAMONDS, "♣": Suit.CLUBS, "♠": Suit.SPADES}
        suit = suit_map.get(suit_symbol)
        if not suit:
            return False, "Invalid suit"
        
        # Find the card in player's hand
        player = None
        for p in game.players:
            if p.id == player_id:
                player = p
                break
        
        if not player:
            return False, "Player not found"
        
        # Find the specific card
        target_card = None
        for card in player.hand:
            if card.rank == rank and card.suit == suit:
                target_card = card
                break
        
        if not target_card:
            return False, "Card not in hand"
        
        success, message = game.play_card(player_id, target_card, pile_name)
        if success:
            self._last_activity[game.game_id] = time.time()
        
        return success, message
    
    def draw_card(self, player_id: str) -> tuple[bool, str]:
        """Draw a card."""
        game = self.get_player_game(player_id)
        if not game:
            return False, "Game not found"
        
        success, message = game.draw_card(player_id)
        if success:
            self._last_activity[game.game_id] = time.time()
        
        return success, message
    
    def end_turn(self, player_id: str) -> bool:
        """End a player's turn."""
        game = self.get_player_game(player_id)
        if not game:
            return False
        
        current_player = game.get_current_player()
        if current_player and current_player.id == player_id:
            game.end_turn()
            self._last_activity[game.game_id] = time.time()
            return True
        
        return False
    
    def move_pile(self, player_id: str, from_pile: str, to_pile: str) -> tuple[bool, str]:
        """Move an entire pile to another pile."""
        game = self.get_player_game(player_id)
        if not game:
            return False, "Game not found"
        
        success, message = game.move_pile(player_id, from_pile, to_pile)
        if success:
            self._last_activity[game.game_id] = time.time()
        
        return success, message
    
    def get_game_state(self, game_id: str) -> Optional[Dict]:
        """Get the current game state."""
        game = self.get_game(game_id)
        if game:
            return game.get_game_state()
        return None
    
    def list_active_games(self) -> List[Dict]:
        """List all active games."""
        self._cleanup_expired_games()
        games = []
        for game_id, game in self._games.items():
            games.append({
                'game_id': game_id,
                'players': len(game.players),
                'max_players': 4,
                'started': game.game_started,
                'game_over': game.game_over
            })
        return games
    
    def _cleanup_expired_games(self):
        """Remove expired games."""
        current_time = time.time()
        expired_games = []
        
        for game_id, last_activity in self._last_activity.items():
            if current_time - last_activity > self.session_timeout:
                expired_games.append(game_id)
        
        for game_id in expired_games:
            self._remove_game(game_id)
    
    def _remove_game(self, game_id: str):
        """Remove a game and clean up associated data."""
        if game_id in self._games:
            game = self._games[game_id]
            # Remove player sessions
            for player in game.players:
                if player.id in self._player_sessions:
                    del self._player_sessions[player.id]
            
            del self._games[game_id]
            del self._last_activity[game_id]


# Global game manager instance
game_manager = GameSessionManager()
