from .dev import Card
from random import shuffle

class Table:
    _draw_Cards: list[Card]
    _played_Cards: list[Card] = []
    
    def __init__(self, cards: list[Card]):
        self._draw_Cards = cards
        shuffle(self._draw_Cards)
        self.place_Card(self.draw_Card())
    
    def get_last_Card_played(self):
        return self._played_Cards[-1]
    
    def place_Card(self, new_card: Card) -> None:
        self._played_Cards.append(new_card)
        
    def draw_Card(self) -> Card:
        if len(self._draw_Cards) == 0:
            self._draw_Cards += self._played_Cards[:-1]
            self._played_Cards = self._played_Cards[-1:]
            shuffle(self._draw_Cards)
            
        return self._draw_Cards.pop()