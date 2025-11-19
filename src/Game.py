from .dev import Player
from .Table import Table

from .dev import GameRule
from typing import Literal

class Game:
    _uuid: str
    _name: str
    _data: dict = {}
    _gamerules: list[GameRule]
    
    _players: list[Player]
    _table: Table
    _sense: Literal[1, -1] = 1
    _turn: int = 1
    
    def __init__(self, gamerules: list[GameRule], players: list[Player]):
        self._gamerules = [gamerule(self) for gamerule in gamerules]
        cards = []
        for gamerule in self._gamerules:
            cards+=gamerule.gen_new_Card()
        self._players = players
        self._table = Table(cards)
    
    def playTurn(self):
        
        cardToPlay = self.get_player_turn().getCardToPlay(self._table.get_last_Card_played())
        
        if cardToPlay:
            #play
            if self.is_Card_playable(cardToPlay):
                self.get_player_turn()._hand.remove_Card(cardToPlay)
                self._table.place_Card(cardToPlay)
                
                for gamerule in self._gamerules:
                    gamerule.on_Card_played(cardToPlay)
            else:
                self.playTurn()
        else:
            #draw
            cardDrawed = self._table.draw_Card()
            self.get_player_turn()._hand.add_Card(cardDrawed)
            
            for gamerule in self._gamerules:
                gamerule.on_Card_drawed(cardDrawed)
                    
        self.next_turn()
        
    def next_turn(self):
        self._turn += 1 * self._sense
        self._turn = self._turn%len(self._players)
    
    def switch_turn(self):
        self._sense = -self._sense
        
    def is_Card_playable(self, new_card):
        return (True in [gamerule.is_Card_playable(self._table.get_last_Card_played(), new_card) for gamerule in self._gamerules])
        
    def get_player_turn(self) -> Player:
        return self._players[self._turn]
    
    def make_player_pioche(self) -> None:
        card = self._table.draw_Card()
        if card:
            self.get_player_turn()._hand.add_Card(card)
            
    def startGame(self):
        for i in range(7):
            for player in self._players:
                player._hand.add_Card(self._table.draw_Card())
                
        while not 0 in [player._hand.numberOfCard() for player in self._players]:
            self.playTurn()