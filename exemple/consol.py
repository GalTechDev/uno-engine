import sys
sys.path.insert(0, '.')

from src.GameRules.classic import classicRules
from src.dev import Player
from random import choice
from src.Game import Game
from src.GameRules.Uno import UnoRule

class CustomPlayer(Player):
    def __init__(self, nom, is_bot=True):
        super().__init__(nom)
        self.is_bot = is_bot
        
    def getCardToPlay_Player(self, last_Card_played):
        uno_rule = next(r for r in game.get_gamerules() if isinstance(r, UnoRule))

        print(f"\n\nTapis : {last_Card_played}")
        print(f"\nA {self._id} de jouer")
        
        while True:
            for i, card in enumerate(self._hand._cards):
                print(f"{i}) {card}")
            print(f"{len(self._hand._cards)}) Piocher")
            if len(self._hand._cards) == 1:
                print("u) UNO!")
            print("c [nom]) Contre-Uno (ex: c Damien)")
                
            choice_str = input("Choix : ")
            
            if choice_str.lower() in ['u', 'uno']:
                uno_rule.action_uno(self)
                continue

            if choice_str.lower().startswith('c '):
                parts = choice_str.split(maxsplit=1)
                if len(parts) > 1:
                    target_name = parts[1]
                    target = next((p for p in game._players if p._id == target_name), None)
                    if target:
                        uno_rule.action_contest_uno(self, target)
                    else:
                        print("-> Joueur introuvable.")
                continue

            try:
                num_card = int(choice_str)
                if num_card == len(self._hand._cards):
                    return None
                if 0 <= num_card < len(self._hand._cards):
                    return self._hand._cards[num_card]
            except ValueError:
                pass

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

class ConsoleUnoRule(UnoRule):
    def on_uno(self, player: Player):
        print(f"-> UNO déclaré par {player._id}!")
        
    def on_contest_uno(self, accuser: Player, target: Player, success: bool):
        if success:
            print(f"-> CONTRE-UNO! {target._id} a oublié UNO et est catché par {accuser._id}!")
            print(f"-> {target._id} pioche 2 cartes!")
        else:
            print(f"-> Raté, {target._id} n'était pas vulnérable.")

# Add UnoRule BEFORE classic rules so it sees the player state before +2 advances turn
game = Game([ConsoleUnoRule] + classicRules, players)

game.startGame()