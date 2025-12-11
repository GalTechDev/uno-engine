from ..dev import GameRule, Card

class ClassicCard(GameRule):
    name = "ClassicCard"
    
    def gen_new_Card(self):
        cards = [Card(color, str(sign)) for color in ["blue", "yellow", "red", "green"] for sign in range(10)]
        cards += [Card(color, sign) for color in ["blue", "yellow", "red", "green"] for sign in ["+2", "pass", "reverse"]]
        cards *= 2
        
        return cards
        

class SameColor(GameRule):
    name = "SameColor"
    
    def is_Card_playable(self, last_Card: Card, new_Card: Card) -> bool:
        return last_Card.color == new_Card.color
    
class SameSign(GameRule):
    name = "SameSign"
    
    def is_Card_playable(self, last_Card: Card, new_Card: Card) -> bool:
        return last_Card.sign == new_Card.sign
    
class Plus2(GameRule):
    name = "Plus2"
    
    def on_Card_played(self, Card: Card, player = None) -> None:
        if Card.sign == "+2":
            self.game.next_turn()
            for i in range(2):
                self.game.make_player_pioche()

class Plus4(GameRule):
    name = "Plus4"
    
    def on_Card_played(self, Card: Card, player = None) -> None:
        if Card.sign == "+4":
            self.game.next_turn()
            for i in range(4):
                self.game.make_player_pioche()
                
class Pass(GameRule):
    name = "Pass"
    
    def on_Card_played(self, Card: Card, player = None) -> None:
        if Card.sign == "pass":
            self.game.next_turn()
            
class Reverse(GameRule):
    name = "Reverse"
    
    def on_Card_played(self, Card: Card, player = None) -> None:
        if Card.sign == "reverse":
            self.game.switch_turn()
                
classicRules = [ClassicCard, SameColor, SameSign, Plus2, Plus4, Pass, Reverse]