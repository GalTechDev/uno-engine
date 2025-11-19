from .Card import Card

class Hand:
    _cards: list[Card] = []
    
    def __init__(self):
        self._cards = []
    
    def add_Card(self, card: Card) -> None:
        self._cards.append(card)
        
    def remove_Card(self, card: Card) -> None:
        self._cards.remove(card)
        
    def numberOfCard(self) -> int:
        return len(self._cards)