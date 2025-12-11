from ..dev import GameRule, Card, Player

class UnoRule(GameRule):
    name = "UnoRule"
    
    declared_uno_players: set[Player]
    vulnerable_player: Player = None
    
    def __init__(self, game):
        super().__init__(game)
        self.declared_uno_players = set()
        self.vulnerable_player = None

    def action_uno(self, player: Player):
        """Called by UI when a player screams UNO"""
        self.declared_uno_players.add(player)
        if self.vulnerable_player == player:
            self.vulnerable_player = None # Saved!
        self.on_uno(player)

    def action_contest_uno(self, accuser: Player, target: Player) -> bool:
        """Called by UI when a player contests another playing not saying UNO"""
        if target == self.vulnerable_player:
            # Penalty: draw 2 cards
            for _ in range(2):
                card = self.game._table.draw_Card()
                if card:
                    target._hand.add_Card(card)
            
            self.vulnerable_player = None # Penalty applied, no longer vulnerable
            self.on_contest_uno(accuser, target, True)
            return True
            
        self.on_contest_uno(accuser, target, False)
        return False
        
    def on_uno(self, player: Player): ...
    
    def on_contest_uno(self, accuser: Player, target: Player, success: bool): ...

    def on_Card_played(self, Card: Card, player: Player = None) -> None:
        # Step 1: Window closed for previous vulnerable player
        self.vulnerable_player = None
        
        if player is None:
            return

        # Step 2: Check current player status
        if player._hand.numberOfCard() == 1:
            if player not in self.declared_uno_players:
                self.vulnerable_player = player
        else:
            # If they have != 1 cards, they don't need to (or validly can't) say Uno anymore
            if player in self.declared_uno_players:
                self.declared_uno_players.remove(player)
