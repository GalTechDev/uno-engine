# Documentation Moteur Uno

Bienvenue dans la documentation du moteur de jeu Uno. Ce projet est conçu comme une bibliothèque flexible permettant aux développeurs de créer leurs propres interfaces (CLI, GUI, Web) et règles personnalisées.

## Structure du Projet

- `src/` : Code source du moteur.
    - `Game.py` : Cœur du jeu.
    - `Table.py` : Gestion du plateau (pioche/défausse).
    - `dev/` : Classes de base (`Player`, `Card`, `GameRule`).
    - `GameRules/` : Implémentations des règles (Classic, Uno).
- `exemple/` : Exemples d'implémentation.
    - `gui.py` : Interface graphique complète avec Pygame.
    - `console.py` : Exemple en ligne de commande.

## Démarrage Rapide

Pour lancer une partie standard :

```python
from src.Game import Game
from src.GameRules.classic import classicRules
from src.dev import Player

# 1. Créer vos joueurs
class MonJoueur(Player):
    def getCardToPlay(self, last_card):
        # Logique pour choisir une carte
        # Retourne une Card ou None (pour piocher)
        return None 

players = [MonJoueur("J1"), MonJoueur("J2")]

# 2. Initialiser le jeu avec les règles classiques
game = Game(classicRules, players)

# 3. Lancer la boucle principale
game.startGame()
```

Consultez les autres sections pour :
- [Architecture](architecture.md) : Comprendre le fonctionnement interne.
- [Créer des Règles](creating_rules.md) : Ajouter des cartes spéciales ou modifier le gameplay.
- [Créer des Joueurs](creating_players.md) : Connecter une IA ou une Interface Graphique.
