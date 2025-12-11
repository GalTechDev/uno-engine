import sys
import threading
import time
import math
import pygame
from typing import Optional, List, Tuple

sys.path.insert(0, '.')

from src.Game import Game
from src.dev import Player, Card
from src.GameRules.classic import classicRules
from src.GameRules.Uno import UnoRule
from random import choice

# --- Constants & Config ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
COLOR_BG = (30, 35, 40)
COLOR_CARD_RED = (230, 50, 50)
COLOR_CARD_BLUE = (50, 100, 230)
COLOR_CARD_GREEN = (50, 200, 80)
COLOR_CARD_YELLOW = (240, 220, 40)
COLOR_CARD_BLACK = (40, 40, 40)
COLOR_WHITE = (255, 255, 255)
COLOR_HOVER = (255, 255, 255)

CARD_WIDTH = 100
CARD_HEIGHT = 150
CARD_RADIUS = 10

def get_card_color(card: Card) -> Tuple[int, int, int]:
    if card.color == "red": return COLOR_CARD_RED
    if card.color == "blue": return COLOR_CARD_BLUE
    if card.color == "green": return COLOR_CARD_GREEN
    if card.color == "yellow": return COLOR_CARD_YELLOW
    return COLOR_CARD_BLACK

# --- Visual Classes ---

class VisualCard:
    def __init__(self, card: Card, start_pos: Tuple[float, float], target_pos: Tuple[float, float]):
        self.card = card
        self.x, self.y = start_pos
        self.target_x, self.target_y = target_pos
        
        self.width = CARD_WIDTH
        self.height = CARD_HEIGHT
        
        self.scale = 1.0
        self.target_scale = 1.0
        self.rotation = 0
        self.target_rotation = 0
        
        self.is_hovered = False
        self.visible = True
        self.z_index = 0

    def set_target(self, x, y, rot=0, scale=1.0):
        self.target_x = x
        self.target_y = y
        self.target_rotation = rot
        self.target_scale = scale

    def update(self, dt: float):
        # Lerp positions (smooth movement)
        lerp_speed = 10 * dt
        self.x += (self.target_x - self.x) * lerp_speed
        self.y += (self.target_y - self.y) * lerp_speed
        self.rotation += (self.target_rotation - self.rotation) * lerp_speed
        self.scale += (self.target_scale - self.scale) * lerp_speed

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, small_font: pygame.font.Font):
        if not self.visible:
            return

        # Prepare dimensions
        w = int(self.width * self.scale)
        h = int(self.height * self.scale)
        
        # Create a surface for rotation
        card_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        
        # Draw Body
        color = get_card_color(self.card) if self.card else COLOR_CARD_BLACK
        
        # Shadow
        shadow_rect = pygame.Rect(4, 4, w, h)
        pygame.draw.rect(card_surf, (0,0,0, 100), shadow_rect, border_radius=int(CARD_RADIUS*self.scale))
        
        # Main Rect
        rect = pygame.Rect(0, 0, w, h)
        pygame.draw.rect(card_surf, color, rect, border_radius=int(CARD_RADIUS*self.scale))
        pygame.draw.rect(card_surf, COLOR_WHITE, rect, width=2, border_radius=int(CARD_RADIUS*self.scale))
        
        if self.card:
            # Center Circle
            center = (w//2, h//2)
            pygame.draw.circle(card_surf, COLOR_WHITE, center, int(w*0.35))
            
            # Text (Sign)
            sign_str = str(self.card.sign)
            # Adjust font size for long text like "reverse"
            txt_surf = font.render(sign_str, True, color)
            if txt_surf.get_width() > w * 0.6:
                txt_surf = small_font.render(sign_str, True, color)
                
            txt_rect = txt_surf.get_rect(center=center)
            card_surf.blit(txt_surf, txt_rect)
            
            # Corner Text
            corner_surf = small_font.render(sign_str, True, COLOR_WHITE)
            card_surf.blit(corner_surf, (5, 5))
            card_surf.blit(pygame.transform.rotate(corner_surf, 180), (w - corner_surf.get_width() - 5, h - corner_surf.get_height() - 5))

        else:
            # Back of card
            pygame.draw.circle(card_surf, (200, 50, 50), (w//2, h//2), int(w*0.2))
            txt = small_font.render("UNO", True, COLOR_WHITE)
            card_surf.blit(txt, txt.get_rect(center=(w//2, h//2)))

        # Hover Glint
        if self.is_hovered:
            pygame.draw.rect(card_surf, (255, 255, 255, 50), rect, border_radius=int(CARD_RADIUS*self.scale))

        # Rotate and Blit to screen
        rotated_surf = pygame.transform.rotate(card_surf, self.rotation)
        blit_rect = rotated_surf.get_rect(center=(self.x, self.y))
        surface.blit(rotated_surf, blit_rect)
        
        return blit_rect # Return for collision detection

# --- Button ---
class Button:
    def __init__(self, x, y, w, h, text, callback, color=(50, 50, 50)):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = tuple(min(c + 50, 255) for c in color)
        self.is_hovered = False

    def draw(self, surface, font):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_WHITE, self.rect, width=2, border_radius=8)
        
        txt_surf = font.render(self.text, True, COLOR_WHITE)
        surface.blit(txt_surf, txt_surf.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            self.callback()

# --- Player Adapters ---

class PygameGuiPlayer(Player):
    def __init__(self, nom, app_ref):
        super().__init__(nom)
        self.app = app_ref
        self.selected_card: Optional[Card] = None
        self.input_event = threading.Event()
        self.is_human = True

    def getCardToPlay(self, last_Card_played: Card) -> Optional[Card]:
        # Signal app to enable input
        self.app.set_input_mode(True, self)
        
        self.input_event.clear()
        self.selected_card = None
        
        # Block
        self.input_event.wait()
        
        self.app.set_input_mode(False, None)
        return self.selected_card

class BotPlayer(Player):
    def __init__(self, nom, game_ref):
        super().__init__(nom)
        self.game = game_ref

    def getCardToPlay(self, last_Card_played: Card) -> Optional[Card]:
        time.sleep(1.0) # Bot thinking time
        cards_playable = [card for card in self._hand._cards if self.game.is_Card_playable(card)]
        if cards_playable:
            return choice(cards_playable)
        return None

# --- Logic Hooks ---
class PygameUnoRule(UnoRule):
    def __init__(self, game, app_ref):
        super().__init__(game)
        self.app = app_ref
        
    def on_uno(self, player):
        self.app.add_notification(f"UNO! ({player._id})", color=(255, 50, 50))
        
    def on_contest_uno(self, accuser, target, success):
        if success:
            self.app.add_notification(f"Valid Contest! {target._id} +2 cards", color=(255, 100, 0))
        else:
            self.app.add_notification("Contest Failed", color=(100, 100, 100))

# --- Main App ---

class UnoPygameApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Uno - Pygame Edition")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font_large = pygame.font.SysFont("Verdana", 40, bold=True)
        self.font_medium = pygame.font.SysFont("Verdana", 24, bold=True)
        self.font_small = pygame.font.SysFont("Verdana", 14, bold=True)
        
        # Game State
        self.game = None
        self.user_player = None
        self.visual_hand: List[VisualCard] = []
        self.table_card: Optional[VisualCard] = None
        
        self.buttons = []
        self.notifications = [] # (text, time_end, color)
        
        self.waiting_for_input = False
        
        self.deck_pos = (SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2)
        self.discard_pos = (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)
        
        # Initialize Buttons
        self.setup_buttons()
        
        # Start Game Thread
        threading.Thread(target=self.init_and_run_game, daemon=True).start()

    def setup_buttons(self):
        btn_y = SCREEN_HEIGHT - 80
        self.buttons.append(Button(SCREEN_WIDTH - 220, btn_y, 200, 50, "Piocher / Passer", self.on_draw_click, (80, 80, 80)))
        
        self.buttons.append(Button(20, SCREEN_HEIGHT - 140, 150, 40, "📢 UNO!", self.on_uno_click, (200, 50, 50)))
        self.buttons.append(Button(20, SCREEN_HEIGHT - 90, 150, 40, "🚨 Contre-Uno", self.on_contest_click, (220, 120, 0)))

    def init_and_run_game(self):
        self.user_player = PygameGuiPlayer("Vous", self)
        players = [self.user_player]
        
        # Lazy bots
        bots = [BotPlayer("Bot 1", None), BotPlayer("Bot 2", None), BotPlayer("Bot 3", None)]
        all_players = players + bots
        
        def RuleFactory(g): return PygameUnoRule(g, self)
        RuleFactory.name = "UnoRule"
        
        self.game = Game([RuleFactory] + classicRules, all_players)
        self.uno_rule = next(r for r in self.game.get_gamerules() if isinstance(r, UnoRule))
        
        for bot in bots:
            bot.game = self.game

        # Initial Table Card Visual
        first_card = self.game._table.get_last_Card_played()
        self.table_card = VisualCard(first_card, self.deck_pos, self.discard_pos)
        self.table_card.rotation = choice([-15, -5, 5, 15])
        
        # Initial Hand Sync
        self.sync_hand(animation_source="deck")
        
        time.sleep(1)
        self.game.startGame()

    # --- Sync & hooks ---
    def set_input_mode(self, active: bool, player):
        self.waiting_for_input = active
        if active:
            self.sync_hand() # Refresh hand visuals

    def sync_hand(self, animation_source="deck"):
        """Syncs the user's hand visual state with the Engine's logical hand."""
        if not self.user_player: return
        
        # Create new logical mapping
        new_visuals = []
        hand_cards = self.user_player._hand._cards
        
        # Simple algorithm: Try to keep existing visual updates if card matches, else separate
        # For simplicity in this demo: Rebuild list but try to animate positions
        
        hand_len = len(hand_cards)
        center_x = SCREEN_WIDTH // 2
        
        # Calculate positions
        fan_spread = min(60, SCREEN_WIDTH / (hand_len + 1) if hand_len > 0 else 0)
        start_x = center_x - ((hand_len - 1) * fan_spread) / 2
        
        current_visual_map = {vc.card: vc for vc in self.visual_hand}
        
        for i, card in enumerate(hand_cards):
            target_x = start_x + i * fan_spread
            target_y = SCREEN_HEIGHT - 100
            target_rot = (i - (hand_len-1)/2) * -3
            
            if card in current_visual_map:
                # Update existing
                vc = current_visual_map[card]
                vc.set_target(target_x, target_y, target_rot)
                new_visuals.append(vc)
            else:
                # New card! Animate from source
                start_x_anim, start_y_anim = self.deck_pos
                vc = VisualCard(card, (start_x_anim, start_y_anim), (target_x, target_y))
                vc.set_target(target_x, target_y, target_rot)
                new_visuals.append(vc)
                
        self.visual_hand = new_visuals

    # --- Interaction ---
    def on_draw_click(self):
        if self.waiting_for_input:
            self.user_player.selected_card = None
            self.user_player.input_event.set()

    def on_card_click(self, vc: VisualCard):
        if self.waiting_for_input:
            if self.game.is_Card_playable(vc.card):
                # Animate to table
                vc.set_target(*self.discard_pos, rot=choice([-20, 20]), scale=0.8)
                self.table_card = vc # Optimistic update
                
                self.user_player.selected_card = vc.card
                self.user_player.input_event.set()
            else:
                self.add_notification("Cette carte n'est pas jouable!", color=(200, 50, 50))
    
    def on_uno_click(self):
        if self.uno_rule and self.user_player:
            self.uno_rule.action_uno(self.user_player)
            
    def on_contest_click(self):
        if self.uno_rule and self.user_player and self.uno_rule.vulnerable_player:
             self.uno_rule.action_contest_uno(self.user_player, self.uno_rule.vulnerable_player)

    def add_notification(self, text, color=(255, 255, 255)):
        self.notifications.append((text, time.time() + 3.0, color))

    # --- Main Loop ---
    def main_loop(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            
            # 1. Event Handling
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                for btn in self.buttons:
                    btn.handle_event(event)
                    
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Check card clicks (reverse order for top-first)
                    clicked = False
                    for vc in reversed(self.visual_hand):
                        rect = vc.draw(self.screen, self.font_large, self.font_small) # Dirty way to get rect, better store it
                        # Since we clear screen, we can't reliably get rect from draw here unless we separate update/draw logic strictly or cache rect
                        # Let's use simplified collision based on vc.x, vc.y
                        dist_sq = (mouse_pos[0] - vc.x)**2 + (mouse_pos[1] - vc.y)**2
                        if dist_sq < (CARD_WIDTH/2)**2 + (CARD_HEIGHT/2)**2: # Approx collision
                            self.on_card_click(vc)
                            clicked = True
                            break

            # 2. Update
            # Check for Table update from engine
            if self.game and self.game._table:
                engine_top_card = self.game._table.get_last_Card_played()
                if self.table_card is None or self.table_card.card != engine_top_card:
                    # New card on table (played by bot likely)
                    # We should spawn it originating from the player who played it
                    # For now, spawn from center for bots
                    if self.table_card is None or self.table_card.card != engine_top_card:
                        self.table_card = VisualCard(engine_top_card, self.deck_pos, self.discard_pos)
                        self.table_card.rotation = choice([-15, 15])
                        
                        # Trigger hand sync if it was player's turn to ensure card removed
                        self.sync_hand()
            
            # Hover logic
            hovered_card = None
            # Check collisions in reverse (render order top-to-bottom)
            for vc in reversed(self.visual_hand):
                dist_sq = (mouse_pos[0] - vc.x)**2 + (mouse_pos[1] - vc.y)**2
                if dist_sq < (CARD_WIDTH/2)**2 + (CARD_HEIGHT/2)**2:
                    hovered_card = vc
                    break
            
            # Apply states
            for vc in self.visual_hand:
                # Reset defaults
                vc.target_y = SCREEN_HEIGHT - 100 
                vc.target_scale = 1.0
                vc.z_index = 0
                vc.is_hovered = False
                
                if vc == hovered_card:
                    vc.target_y = SCREEN_HEIGHT - 130
                    vc.target_scale = 1.2
                    vc.z_index = 1
                    vc.is_hovered = True
            
            # Sort visual hand by z-index for drawing order
            self.visual_hand.sort(key=lambda x: x.z_index)

            for vc in self.visual_hand:
                vc.update(dt)
            
            if self.table_card:
                self.table_card.update(dt)

            # 3. Draw
            self.screen.fill(COLOR_BG)
            
            # Draw Opponents
            if self.game:
                current_player = self.game.get_player_turn()
                opponents = [p for p in self.game._players if p != self.user_player]
                
                # Top layout x positions
                spacing = SCREEN_WIDTH // (len(opponents) + 1)
                for i, p in enumerate(opponents):
                    x = spacing * (i + 1)
                    y = 80
                    
                    # Highlight active turn
                    color = COLOR_WHITE
                    if p == current_player:
                        pygame.draw.circle(self.screen, (50, 150, 255), (x, y), 50, width=4)
                        color = (100, 200, 255)
                        
                    # Avatar
                    pygame.draw.circle(self.screen, (100, 100, 100), (x, y), 40)
                    
                    # Name
                    lbl = self.font_medium.render(p._id, True, color)
                    self.screen.blit(lbl, lbl.get_rect(center=(x, y + 50)))
                    
                    # Cards
                    count = p._hand.numberOfCard()
                    lbl_count = self.font_small.render(f"{count} Cards", True, (200, 200, 200))
                    self.screen.blit(lbl_count, lbl_count.get_rect(center=(x, y + 70)))
                    
                    # Uno Badge
                    if self.uno_rule and p in self.uno_rule.declared_uno_players:
                        lbl_uno = self.font_small.render("UNO!", True, (255, 50, 50))
                        self.screen.blit(lbl_uno, lbl_uno.get_rect(center=(x, y - 60)))

            # Draw Center
            # Deck
            pygame.draw.rect(self.screen, (150, 50, 50), 
                             (self.deck_pos[0]-CARD_WIDTH//2, self.deck_pos[1]-CARD_HEIGHT//2, CARD_WIDTH, CARD_HEIGHT), 
                             border_radius=CARD_RADIUS)
            pygame.draw.rect(self.screen, COLOR_WHITE, 
                             (self.deck_pos[0]-CARD_WIDTH//2, self.deck_pos[1]-CARD_HEIGHT//2, CARD_WIDTH, CARD_HEIGHT), 
                             width=2, border_radius=CARD_RADIUS)
            
            # Table Card
            if self.table_card:
                self.table_card.draw(self.screen, self.font_large, self.font_small)

            # Draw Hand
            if self.user_player:
                # Highlight if turn
                if self.game.get_player_turn() == self.user_player:
                     pygame.draw.rect(self.screen, (50, 200, 50), (0, SCREEN_HEIGHT-10, SCREEN_WIDTH, 10))
                
                for vc in self.visual_hand:
                    vc.draw(self.screen, self.font_large, self.font_small)
            
            # Buttons
            for btn in self.buttons:
                btn.draw(self.screen, self.font_small)
                
            # Notification Overlay
            current_time = time.time()
            self.notifications = [n for n in self.notifications if n[1] > current_time]
            for i, (text, _, color) in enumerate(self.notifications):
                lbl = self.font_medium.render(text, True, color)
                # Draw with background for readability
                bg_rect = lbl.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100 - i*40))
                bg_rect.inflate_ip(20, 10)
                pygame.draw.rect(self.screen, (0,0,0, 180), bg_rect, border_radius=10)
                self.screen.blit(lbl, lbl.get_rect(center=bg_rect.center))

            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    UnoPygameApp().main_loop()
