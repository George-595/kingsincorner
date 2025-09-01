"""
Main game logic for Kings in the Corner.
"""
import uuid
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from cards import Card, Deck, GamePile


@dataclass
class Player:
    """Represents a player in the game."""
    id: str
    name: str
    hand: List[Card] = field(default_factory=list)
    
    def add_card(self, card: Card):
        """Add a card to the player's hand."""
        self.hand.append(card)
    
    def remove_card(self, card: Card) -> bool:
        """Remove a card from the player's hand."""
        if card in self.hand:
            self.hand.remove(card)
            return True
        return False
    
    def has_won(self) -> bool:
        """Check if the player has won (empty hand)."""
        return len(self.hand) == 0
    
    def can_play_card(self, card: Card, pile: GamePile) -> bool:
        """Check if the player can play a specific card on a pile."""
        return card in self.hand and card.can_play_on(pile.get_top_card(), pile.pile_type)


class KingsCornerGame:
    """Main game class for Kings in the Corner."""
    
    def __init__(self, game_id: str = None):
        self.game_id = game_id or str(uuid.uuid4())
        self.players: List[Player] = []
        self.current_player_index = 0
        self.deck = Deck()
        
        # Foundation piles (4 main piles)
        self.foundation_piles = {
            'north': GamePile('North', 'foundation'),
            'south': GamePile('South', 'foundation'),
            'east': GamePile('East', 'foundation'),
            'west': GamePile('West', 'foundation')
        }
        
        # Corner piles (for Kings)
        self.corner_piles = {
            'ne': GamePile('Northeast', 'corner'),
            'nw': GamePile('Northwest', 'corner'),
            'se': GamePile('Southeast', 'corner'),
            'sw': GamePile('Southwest', 'corner')
        }
        
        self.game_started = False
        self.game_over = False
        self.winner = None
        self.turn_actions_taken = 0
        self.max_actions_per_turn = 10  # Allow multiple actions per turn
        self.must_draw_to_end_turn = True  # Must draw a card to end turn
    
    def add_player(self, player_name: str) -> str:
        """Add a player to the game."""
        if len(self.players) >= 4:
            raise ValueError("Game is full (max 4 players)")
        
        if self.game_started:
            raise ValueError("Game has already started")
        
        player_id = str(uuid.uuid4())
        player = Player(player_id, player_name)
        self.players.append(player)
        return player_id
    
    def start_game(self):
        """Start the game."""
        if len(self.players) < 2:
            raise ValueError("Need at least 2 players to start")
        
        if self.game_started:
            raise ValueError("Game already started")
        
        # Deal 7 cards to each player
        for player in self.players:
            player.hand = self.deck.deal(7)
        
        # Deal 1 card to each foundation pile
        for pile in self.foundation_piles.values():
            if not self.deck.is_empty():
                pile.add_card(self.deck.deal(1)[0], force=True)
        
        self.game_started = True
        self.current_player_index = 0
    
    def get_current_player(self) -> Optional[Player]:
        """Get the current player."""
        if not self.players:
            return None
        return self.players[self.current_player_index]
    
    def play_card(self, player_id: str, card: Card, pile_name: str) -> Tuple[bool, str]:
        """Play a card from a player's hand to a pile."""
        if not self.game_started or self.game_over:
            return False, "Game not in progress"
        
        current_player = self.get_current_player()
        if not current_player or current_player.id != player_id:
            return False, "Not your turn"
        
        # Allow unlimited card plays per turn (only drawing ends turn)
        # if self.turn_actions_taken >= self.max_actions_per_turn:
        #     return False, "No more actions allowed this turn"
        
        # Find the target pile
        target_pile = None
        if pile_name in self.foundation_piles:
            target_pile = self.foundation_piles[pile_name]
        elif pile_name in self.corner_piles:
            target_pile = self.corner_piles[pile_name]
        
        if not target_pile:
            return False, "Invalid pile"
        
        # Check if the move is valid
        if not current_player.can_play_card(card, target_pile):
            return False, "Invalid move"
        
        # Make the move
        current_player.remove_card(card)
        target_pile.add_card(card)
        self.turn_actions_taken += 1
        
        # Check for win condition
        if current_player.has_won():
            self.game_over = True
            self.winner = current_player
            return True, f"{current_player.name} wins!"
        
        return True, "Card played successfully"
    
    def move_pile(self, player_id: str, from_pile: str, to_pile: str) -> Tuple[bool, str]:
        """Move an entire pile to another pile."""
        if not self.game_started or self.game_over:
            return False, "Game not in progress"
        
        current_player = self.get_current_player()
        if not current_player or current_player.id != player_id:
            return False, "Not your turn"
        
        # Allow unlimited pile moves per turn
        # if self.turn_actions_taken >= self.max_actions_per_turn:
        #     return False, "No more actions allowed this turn"
        
        # Get source and destination piles
        source = self._get_pile(from_pile)
        destination = self._get_pile(to_pile)
        
        if not source or not destination:
            return False, "Invalid pile names"
        
        if source.is_empty():
            return False, "Source pile is empty"
        
        # Attempt the move
        if source.move_pile_to(destination):
            self.turn_actions_taken += 1
            return True, "Pile moved successfully"
        else:
            return False, "Invalid pile move"
    
    def draw_card(self, player_id: str) -> Tuple[bool, str]:
        """Draw a card from the deck (ends turn)."""
        if not self.game_started or self.game_over:
            return False, "Game not in progress"
        
        current_player = self.get_current_player()
        if not current_player or current_player.id != player_id:
            return False, "Not your turn"
        
        if self.deck.is_empty():
            return False, "Deck is empty"
        
        # Draw a card and end turn
        card = self.deck.deal(1)[0]
        current_player.add_card(card)
        self.end_turn()
        return True, f"Drew {card.display_name}"
    
    def end_turn(self):
        """End the current player's turn."""
        self.turn_actions_taken = 0
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
    
    def _get_pile(self, pile_name: str) -> Optional[GamePile]:
        """Get a pile by name."""
        if pile_name in self.foundation_piles:
            return self.foundation_piles[pile_name]
        elif pile_name in self.corner_piles:
            return self.corner_piles[pile_name]
        return None
    
    def get_game_state(self) -> Dict:
        """Get the current game state."""
        return {
            'game_id': self.game_id,
            'players': [
                {
                    'id': p.id,
                    'name': p.name,
                    'hand_size': len(p.hand),
                    'hand': [{'rank': c.rank, 'suit': c.suit.value, 'color': c.color.value} 
                            for c in p.hand]
                } for p in self.players
            ],
            'current_player': self.current_player_index,
            'current_player_name': self.get_current_player().name if self.get_current_player() else None,
            'foundation_piles': {
                name: {
                    'cards': [{'rank': c.rank, 'suit': c.suit.value, 'color': c.color.value} 
                             for c in pile.cards],
                    'top_card': {'rank': pile.get_top_card().rank, 
                               'suit': pile.get_top_card().suit.value,
                               'color': pile.get_top_card().color.value} if pile.get_top_card() else None,
                    'size': len(pile)
                } for name, pile in self.foundation_piles.items()
            },
            'corner_piles': {
                name: {
                    'cards': [{'rank': c.rank, 'suit': c.suit.value, 'color': c.color.value} 
                             for c in pile.cards],
                    'top_card': {'rank': pile.get_top_card().rank, 
                               'suit': pile.get_top_card().suit.value,
                               'color': pile.get_top_card().color.value} if pile.get_top_card() else None,
                    'size': len(pile)
                } for name, pile in self.corner_piles.items()
            },
            'deck_size': self.deck.cards_remaining(),
            'game_started': self.game_started,
            'game_over': self.game_over,
            'winner': self.winner.name if self.winner else None,
            'turn_actions_taken': self.turn_actions_taken,
            'max_actions_per_turn': self.max_actions_per_turn
        }
