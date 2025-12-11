# Créer des Joueurs (Bots & UI)

La classe `Player` fait le pont entre le moteur et l'utilisateur (humain ou IA).

## Implémentation de Base

Toute implémentation doit hériter de `src.dev.Player` et définir `getCardToPlay`.

```python
from src.dev import Player

class RandomBot(Player):
    def getCardToPlay(self, last_card):
        # Accès à self._hand pour voir ses cartes
        # Accès à self.game (si injecté) pour vérifier la jouabilité
        pass
```

## Intégrer une Interface Graphique (GUI)

Le moteur `Game.startGame()` est **bloquant** (boucle infinie). Pour une interface graphique (Tkinter, Pygame), vous devez généralement :
1. Exécuter le jeu dans un **Thread séparé**.
2. Utiliser un mécanisme de synchronisation (comme `threading.Event`) dans votre `GuiPlayer` pour mettre le jeu en pause le temps que l'utilisateur clique.

### Pattern Recommandé (Thread-Safe)

```python
import threading

class GuiPlayer(Player):
    def __init__(self, name, app):
        super().__init__(name)
        self.app = app
        self.input_event = threading.Event()
        self.selected_card = None

    def getCardToPlay(self, last_card):
        # 1. Demander à l'UI de s'activer (afficher les boutons, etc.)
        self.app.enable_input(self)
        
        # 2. Attendre que l'utilisateur clique (bloque le thread du JEU, pas l'UI)
        self.input_event.wait()
        self.input_event.clear()
        
        # 3. Retourner la carte choisie (définie par l'UI lors du clic)
        return self.selected_card

    # Appelé par l'UI (Main Thread)
    def on_user_click(self, card):
        self.selected_card = card
        self.input_event.set() # Réveille le thread du jeu
```

L'exemple complet se trouve dans `exemple/gui.py` (version Pygame).
