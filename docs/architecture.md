# Architecture du Moteur

Le moteur repose sur une séparation stricte entre la logique de jeu (`Game`), les règles (`GameRule`), et les acteurs (`Player`).

## Classes Principales

### 1. `Game` (`src/Game.py`)
Le chef d'orchestre.
- **Rôle** : Gère la boucle de jeu, l'ordre des tours, et la validation des actions via les règles.
- **Méthodes Clés** :
    - `startGame()` : Lance la boucle infinie (synchrone).
    - `playTurn()` : Exécute un tour de jeu.
    - `is_Card_playable(card)` : Vérifie si une carte peut être posée.
    - `get_gamerules()` : Accès aux règles actives.

### 2. `Table` (`src/Table.py`)
L'état physique du jeu.
- **Rôle** : Contient la pioche (`draw_cards`) et la défausse (`played_cards`).
- **Fonctionnalité** : Mélange automatique de la défausse quand la pioche est vide.

### 3. `Player` (`src/dev/Player.py`)
Classe abstraite représentant un participant.
- **Rôle** : Prend les décisions.
- **Méthode Abstraite** : `getCardToPlay(last_card)` doit être implémentée par le développeur.

### 4. `GameRule` (`src/dev/GameRule.py`)
Unité logique modulaire.
- **Rôle** : Définit comment le jeu réagit aux cartes.
- **Hooks** :
    - `is_Card_playable` : Condition de pose.
    - `on_Card_played` : Effet immédiat (ex: inverser sens, faire piocher).
    - `gen_new_Card` : Crée les cartes à ajouter au paquet au début.

## Flux de Jeu (Game Loop)

1. `Game` demande au joueur courant (`get_player_turn`) de jouer via `getCardToPlay`.
2. Si le joueur retourne une carte :
    - Vérification via `is_Card_playable`.
    - Si valide :
        - Carte retirée de la main et posée sur la `Table`.
        - Appel de `on_Card_played` sur toutes les règles.
3. Si le joueur retourne `None` :
    - Il pioche une carte (`Table.draw_Card`).
    - Appel de `on_Card_drawed`.
4. Passage au tour suivant (`next_turn`).
