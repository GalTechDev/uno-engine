from .Card import Card
from .Game import Game

class GameRule:
    name: str
    game: Game
    
    def __init__(self, game: Game):
        self.game = game

    def gen_new_Card(self) -> list[Card]:
        return []
    
    def on_Card_played(self, Card: Card, player = None) -> None: ...
    
    def on_Card_drawed(self, Card: Card) -> None: ...
    
    def is_Card_playable(self, last_Card: Card, new_Card: Card) -> bool: ...