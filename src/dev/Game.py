from .Player import Player
from ..Table import Table
from typing import Literal

class Game:
    _uuid: str
    _name: str
    _data: dict = {}
    _gamerules: list
    
    _players: list[Player]
    _table: Table
    _sense: Literal[1, -1] = 1
    _turn: int = 1
    
    def __init__(self, gamerules: list, players: list[Player]): ...
    
    def playTurn(self): ...
     
    def next_turn(self): ...
        
    def switch_turn(self): ...
        
    def is_Card_playable(self, new_card): ...
        
    def get_player_turn(self) -> Player: ...
    
    def make_player_pioche(self) -> None: ...
    
    def startGame(self) -> None: ...