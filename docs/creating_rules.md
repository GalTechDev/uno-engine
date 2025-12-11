# Créer des Règles Personnalisées

La force de ce moteur réside dans sa modularité. Vous pouvez tout changer (cartes, effets, conditions) en créant une sous-classe de `GameRule`.

## Structure d'une Règle

```python
from src.dev import GameRule, Card

class MaRegleSuperCool(GameRule):
    name = "SuperCool"
    
    # 1. Générer des cartes (Optionnel)
    def gen_new_Card(self):
        # Créer 4 cartes "Super" de chaque couleur
        return [Card(color, "Super") for color in ["red", "blue", "green", "yellow"]]
    
    # 2. Condition de jeu (Optionnel)
    def is_Card_playable(self, last_card, new_card):
        # Exemple : On peut toujours jouer une carte "Super"
        if new_card.sign == "Super":
            return True
        return False
        
    # 3. Effet au moment de jouer (Optionnel)
    def on_Card_played(self, card, player):
        if card.sign == "Super":
            print(f"{player._id} est Super Cool !")
            # Ex: Faire piocher tout le monde
            for p in self.game._players:
                if p != player:
                    self.game.make_player_pioche()
```

## Intégration

Ajoutez simplement votre classe (pas une instance, la classe elle-même ou une factory) à la liste lors de la création du jeu.

```python
rules = [MaRegleSuperCool] + classicRules
game = Game(rules, players)
```

## Règles Avancées : Hooks d'Evénements

Certaines règles comme `UnoRule` nécessitent des interactions complexes. Vous pouvez définir vos propres méthodes et les appeler depuis votre interface (`mainr.py` ou `gui.py`).

Exemple `UnoRule` :
- `action_uno(player)` : Méthode personnalisée appelée par l'UI.
- `on_uno(player)` : Hook appelé par la règle pour notifier l'UI (pattern Observer).

Voir `src/GameRules/Uno.py` pour un exemple complet.
