##### For embeded Python #####
import sys                   #
sys.path.insert(0, '.')      #
##############################

from src.Game import Game
from src.GameRules.classic import classicRules

from src.dev import Player

from random import choice

class CustomPlayer(Player):
    def __init__(self, nom, is_bot=True):
        super().__init__(nom)
        self.is_bot = is_bot
        
    def getCardToPlay_Player(self, last_Card_played):
        print(f"\n\nTapis : {last_Card_played}")
        print(f"\nA {self._id} de jouer")
        for i, card in enumerate(self._hand._cards):
            print(f"{i}) {card}")
        print(f"{len(self._hand._cards)}) Piocher")
            
        num_card = int(input("Choisi une carte : "))
        if num_card == len(self._hand._cards):
            return
        return self._hand._cards[num_card]
    
    def getCardToPlay_Bot(self):
        cards_playable = [card for card in self._hand._cards if game.is_Card_playable(card)]
        if cards_playable:
            card = choice(cards_playable)
            print(f"\n{self._id} a joué : {card}")
            return card
        else:
            print(f"\n{self._id} a pioché")
            return
        
    
    def getCardToPlay(self, last_Card_played):
        if self.is_bot:
            return self.getCardToPlay_Bot()
        else:
            return self.getCardToPlay_Player(last_Card_played)
    

noms = ["Gali", "Damien", "Henri"]
players = [CustomPlayer(nom) for nom in noms]
players[0].is_bot = False

game = Game(classicRules, players)

game.startGame()