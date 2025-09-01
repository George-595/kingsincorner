"""
Card and Deck classes for Kings in the Corner game.
"""
import random
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum


class Suit(Enum):
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"


class Color(Enum):
    RED = "red"
    BLACK = "black"


@dataclass
class Card:
    """Represents a playing card."""
    suit: Suit
    rank: str
    value: int
    
    def __post_init__(self):
        self.color = Color.RED if self.suit in [Suit.HEARTS, Suit.DIAMONDS] else Color.BLACK
    
    @property
    def display_name(self):
        """Return the display name of the card."""
        return f"{self.rank}{self.suit.value}"
    
    def can_play_on(self, other: Optional['Card'], pile_type: str = "foundation") -> bool:
        """Check if this card can be played on another card."""
        if other is None:
            # Empty pile rules depend on pile type
            if pile_type == "corner":
                # Corner piles can only start with Kings
                return self.rank == "K"
            else:
                # Foundation piles can start with any card
                return True
        
        # Must be descending order and alternating colors
        return (self.value == other.value - 1 and 
                self.color != other.color)
    
    def __str__(self):
        return self.display_name


class Deck:
    """Represents a deck of playing cards."""
    
    def __init__(self):
        self.cards: List[Card] = []
        self._create_deck()
        self.shuffle()
    
    def _create_deck(self):
        """Create a standard 52-card deck."""
        ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        
        for suit in Suit:
            for rank, value in zip(ranks, values):
                self.cards.append(Card(suit, rank, value))
    
    def shuffle(self):
        """Shuffle the deck."""
        random.shuffle(self.cards)
    
    def deal(self, num_cards: int) -> List[Card]:
        """Deal a specified number of cards from the deck."""
        if len(self.cards) < num_cards:
            raise ValueError("Not enough cards in deck")
        
        dealt_cards = []
        for _ in range(num_cards):
            dealt_cards.append(self.cards.pop())
        
        return dealt_cards
    
    def is_empty(self) -> bool:
        """Check if the deck is empty."""
        return len(self.cards) == 0
    
    def cards_remaining(self) -> int:
        """Return the number of cards remaining in the deck."""
        return len(self.cards)


class GamePile:
    """Represents a pile of cards in the game."""
    
    def __init__(self, name: str, pile_type: str = "foundation"):
        self.name = name
        self.pile_type = pile_type  # "foundation" or "corner"
        self.cards: List[Card] = []
    
    def add_card(self, card: Card, force: bool = False) -> bool:
        """Add a card to the pile if valid or forced."""
        if force:
            self.cards.append(card)
            return True
        
        top_card = self.get_top_card()
        if card.can_play_on(top_card, self.pile_type):
            self.cards.append(card)
            return True
        return False
    
    def get_top_card(self) -> Optional[Card]:
        """Get the top card of the pile."""
        return self.cards[-1] if self.cards else None
    
    def is_empty(self) -> bool:
        """Check if the pile is empty."""
        return len(self.cards) == 0
    
    def move_pile_to(self, other_pile: 'GamePile') -> bool:
        """Move this entire pile to another pile if valid."""
        if not self.cards:
            return False
        
        bottom_card = self.cards[0]
        other_top = other_pile.get_top_card()
        
        if bottom_card.can_play_on(other_top, other_pile.pile_type):
            other_pile.cards.extend(self.cards)
            self.cards = []
            return True
        return False
    
    def __len__(self):
        return len(self.cards)
    
    def __str__(self):
        if self.is_empty():
            return f"{self.name}: Empty"
        return f"{self.name}: {self.get_top_card()}"
