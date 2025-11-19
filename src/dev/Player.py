from .Hand import Hand
from .Card import Card

class Player:
    _id: str
    _data: dict = {}
    _hand: Hand
    
    def __init__(self, id: str):
        self._id = id
        self._hand = Hand()
    
    def getCardToPlay(self, last_Card_played: Card) -> Card: ...