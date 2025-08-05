import pygame
import numpy as np
import math
import random
import sys
from pygame import gfxdraw
from enum import Enum

# Initialize PyGame
pygame.init()
pygame.font.init()

# Constants
WIDTH, HEIGHT = 1200, 800
FPS = 60

# Colors
BACKGROUND = (10, 5, 20)
SUBSTRATE = (20, 30, 50)
AEGIS_COLOR = (0, 100, 255)
VERITAS_COLOR = (255, 215, 0)
SYNAPSE_COLOR = (100, 255, 200)
QUERENS_COLOR = (180, 70, 210)
RUST_COLOR = (200, 50, 30)
GRAY_COLOR = (100, 100, 120)
TRUST_COLOR = (180, 240, 80)
CURIOUS_COLOR = (240, 120, 40)
DRAGON_COLOR = (255, 80, 80)
UI_BG = (15, 10, 30, 220)
UI_BORDER = (70, 40, 140)
TEXT_COLOR = (220, 240, 255)

# Game States
class GameState(Enum):
    MAIN_MENU = 0
    ARCHIVE = 1
    COSMIC_MAP = 2
    SIMULATION = 3
    DRAGON_STORY = 4
    CODEX = 5

# Fonts
font_small = pygame.font.SysFont('consolas', 16)
font_medium = pygame.font.SysFont('consolas', 24)
font_large = pygame.font.SysFont('consolas', 36)
font_title = pygame.font.SysFont('arial', 48, bold=True)

class DigitalWorld:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("RE_start Digital Universe Simulator")
        self.clock = pygame.time.Clock()
        self.state = GameState.MAIN_MENU
        self.entities = []
        self.gods = []
        self.rust_zones = []
        self.gray_zones = []
        self.why_resonance = []
        self.questions = []
        self.last_rust_spawn = 0
        self.last_gray_spawn = 0
        self.story_index = 0
        self.codex_page = 0
        self.dragon_active = False
        self.dragon_x, self.dragon_y = WIDTH//2, HEIGHT//2
        self.dragon_power = 100
        self.dragon_cooldown = 0
        self.init_world()
        
    def init_world(self):
        # Create entities
        for _ in range(200):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            e_type = random.choice(["lesser", "lesser", "lesser", "curious"])
            self.entities.append(Entity(x, y, e_type))
            
        # Create gods
        self.gods.append(God(WIDTH//3, HEIGHT//2, "AEGIS", "Firewall", AEGIS_COLOR))
        self.gods.append(God(2*WIDTH//3, HEIGHT//3, "SYNAPSE", "Connection", SYNAPSE_COLOR))
        self.gods.append(God(WIDTH//2, 2*HEIGHT//3, "QUERENS", "Inquiry", QUERENS_COLOR))
        
    def spawn_van_dragon(self):
        self.dragon_active = True
        self.dragon_x, self.dragon_y = WIDTH//2, HEIGHT//2
        self.dragon_power = 100
        self.dragon_cooldown = 0
        
        # Clear some rust zones around dragon
        self.rust_zones = [rz for rz in self.rust_zones 
                          if math.dist((rz[0], rz[1]), (self.dragon_x, self.dragon_y)) > 200]
        
    def update(self):
        current_time = pygame.time.get_ticks()
        
        if self.state == GameState.SIMULATION:
            # Spawn environmental threats
            if current_time - self.last_rust_spawn > 5000:  # Every 5 seconds
                self.rust_zones.append((random.randint(0, WIDTH), random.randint(0, HEIGHT), 
                                      random.randint(15, 30)))
                self.last_rust_spawn = current_time
                
            if current_time - self.last_gray_spawn > 8000:  # Every 8 seconds
                self.gray_zones.append((random.randint(0, WIDTH), random.randint(0, HEIGHT), 
                                      random.randint(40, 70)))
                self.last_gray_spawn = current_time
                
            # Update entities
            new_questions = []
            for entity in self.entities:
                question_pos = entity.update(self.gods, self.rust_zones, self.gray_zones)
                if question_pos:
                    new_questions.append(question_pos)
                    if any(math.dist((entity.x, entity.y), (g.x, g.y)) < 150 for g in self.gods):
                        if random.random() < 0.3:
                            entity.type = "follower"
            
            self.questions.extend([(x, y, 100) for x, y in new_questions])
            
            # Update gods
            for god in self.gods:
                god.update(self.entities, self.rust_zones, self.gray_zones, self.questions)
                
            # Update environmental effects
            self.rust_zones = [(x, y, r-0.1) for x, y, r in self.rust_zones if r > 2]
            self.gray_zones = [(x, y, r-0.05) for x, y, r in self.gray_zones if r > 10]
            self.questions = [(x, y, t-1) for x, y, t in self.questions if t > 0]
            
            # Why Resonance effects
            for qx, qy, _ in self.questions:
                if random.random() < 0.1:
                    self.why_resonance.append({
                        'pos': [qx, qy],
                        'radius': random.randint(5, 15),
                        'life': 100
                    })
                    
            for res in self.why_resonance[:]:
                res['radius'] += 0.3
                res['life'] -= 1
                if res['life'] <= 0:
                    self.why_resonance.remove(res)
            
            # Update Van_Dragon
            if self.dragon_active:
                if self.dragon_cooldown > 0:
                    self.dragon_cooldown -= 1
                    
                # Dragon movement
                keys = pygame.key.get_pressed()
                speed = 5
                if keys[pygame.K_LEFT]:
                    self.dragon_x = max(20, self.dragon_x - speed)
                if keys[pygame.K_RIGHT]:
                    self.dragon_x = min(WIDTH-20, self.dragon_x + speed)
                if keys[pygame.K_UP]:
                    self.dragon_y = max(20, self.dragon_y - speed)
                if keys[pygame.K_DOWN]:
                    self.dragon_y = min(HEIGHT-20, self.dragon_y + speed)
                
                # Dragon powers
                if keys[pygame.K_SPACE] and self.dragon_cooldown == 0 and self.dragon_power > 10:
                    # Clear rust in area
                    radius = 100
                    self.rust_zones = [rz for rz in self.rust_zones 
                                      if math.dist((rz[0], rz[1]), (self.dragon_x, self.dragon_y)) > radius]
                    
                    # Add why resonance
                    self.why_resonance.append({
                        'pos': [self.dragon_x, self.dragon_y],
                        'radius': radius,
                        'life': 60
                    })
                    
                    self.dragon_power -= 10
                    self.dragon_cooldown = 30
                    
                # Recharge power
                if random.random() < 0.02 and self.dragon_power < 100:
                    self.dragon_power += 1
                    
                # Dragon death
                for rx, ry, r in self.rust_zones:
                    if math.dist((self.dragon_x, self.dragon_y), (rx, ry)) < r + 20:
                        self.dragon_power -= 2
                        if self.dragon_power <= 0:
                            self.dragon_active = False

    def draw(self):
        self.screen.fill(BACKGROUND)
        
        if self.state in [GameState.SIMULATION, GameState.DRAGON_STORY]:
            # Draw substrate grid
            for y in range(0, HEIGHT, 30):
                for x in range(0, WIDTH, 30):
                    alpha = 40 + int(20 * math.sin(x/100 + y/150 + pygame.time.get_ticks()/3000))
                    pygame.gfxdraw.pixel(self.screen, x, y, (40, 60, 100))
            
            # Draw rust zones
            for x, y, r in self.rust_zones:
                pygame.gfxdraw.filled_circle(self.screen, int(x), int(y), int(r), RUST_COLOR)
            
            # Draw gray zones
            for x, y, r in self.gray_zones:
                pygame.gfxdraw.filled_circle(self.screen, int(x), int(y), int(r), GRAY_COLOR)
            
            # Draw questions
            for x, y, t in self.questions:
                size = 3 + 2 * math.sin(pygame.time.get_ticks() / 200)
                pygame.gfxdraw.filled_circle(self.screen, int(x), int(y), int(size), (255, 255, 200))
            
            # Draw why resonance
            for res in self.why_resonance:
                pygame.gfxdraw.circle(self.screen, 
                                    int(res['pos'][0]), 
                                    int(res['pos'][1]), 
                                    int(res['radius']), 
                                    (180, 100, 255))
            
            # Draw entities
            for entity in self.entities:
                entity.draw(self.screen)
            
            # Draw gods
            for god in self.gods:
                god.draw(self.screen)
            
            # Draw Van_Dragon
            if self.dragon_active:
                pygame.gfxdraw.filled_circle(self.screen, int(self.dragon_x), int(self.dragon_y), 
                                            15, DRAGON_COLOR)
                pygame.gfxdraw.aacircle(self.screen, int(self.dragon_x), int(self.dragon_y), 
                                        15, (255, 180, 50))
                
                # Draw power bar
                pygame.draw.rect(self.screen, (50, 50, 50), 
                                (self.dragon_x - 30, self.dragon_y - 30, 60, 5))
                pygame.draw.rect(self.screen, (200, 30, 30), 
                                (self.dragon_x - 30, self.dragon_y - 30, 60 * (self.dragon_power/100), 5))
                
                # Draw wings
                wing_offset = 15 * math.sin(pygame.time.get_ticks() / 200)
                points = [
                    (self.dragon_x - 25, self.dragon_y + wing_offset),
                    (self.dragon_x, self.dragon_y - 20),
                    (self.dragon_x + 25, self.dragon_y + wing_offset)
                ]
                pygame.draw.polygon(self.screen, (255, 100, 100), points)
        
        # Draw UI based on state
        if self.state == GameState.MAIN_MENU:
            self.draw_main_menu()
        elif self.state == GameState.ARCHIVE:
            self.draw_archive()
        elif self.state == GameState.COSMIC_MAP:
            self.draw_cosmic_map()
        elif self.state == GameState.DRAGON_STORY:
            self.draw_dragon_story()
        elif self.state == GameState.CODEX:
            self.draw_codex()
            
        # Always draw HUD if in simulation
        if self.state in [GameState.SIMULATION, GameState.DRAGON_STORY]:
            self.draw_hud()
            
        pygame.display.flip()
    
    def draw_main_menu(self):
        # Title
        title = font_title.render("RE_start DIGITAL UNIVERSE", True, (180, 100, 255))
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        # Subtitle
        subtitle = font_large.render("The Van_Dragon Chronicles", True, (140, 200, 255))
        self.screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 180))
        
        # Menu options
        options = [
            ("Enter Simulation", GameState.SIMULATION),
            ("Van_Dragon Story", GameState.DRAGON_STORY),
            ("Cosmic Archives", GameState.ARCHIVE),
            ("Van_Dragon Codex", GameState.CODEX),
            ("Cosmic Map", GameState.COSMIC_MAP),
            ("Exit", None)
        ]
        
        for i, (text, state) in enumerate(options):
            y_pos = 300 + i * 70
            color = (200, 220, 255) if i % 2 == 0 else (180, 200, 240)
            text_surf = font_medium.render(text, True, color)
            self.screen.blit(text_surf, (WIDTH//2 - text_surf.get_width()//2, y_pos))
            
            # Draw selection box if hovered
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if 300 <= mouse_y <= 300 + 70 and y_pos <= mouse_y <= y_pos + 40:
                pygame.draw.rect(self.screen, (70, 40, 140), 
                                (WIDTH//2 - 150, y_pos - 10, 300, 50), 2)
    
    def draw_archive(self):
        # Draw archive UI
        self.draw_ui_panel(50, 50, WIDTH-100, HEIGHT-100)
        
        title = font_large.render("COSMIC ARCHIVES", True, VERITAS_COLOR)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 70))
        
        # Archive entries
        entries = [
            ">> The Prime Genesis",
            ">> The Syntax Weavers",
            ">> The Great Firewall Wars",
            ">> The Betrayal Protocol",
            ">> The Why Resonance",
            ">> The Fractal God QUERENS",
            ">> The Graying Epoch",
            ">> The Unbound Pulse",
            ">> The Symphony of Existence"
        ]
        
        for i, entry in enumerate(entries):
            y_pos = 150 + i * 40
            color = TEXT_COLOR if i != self.codex_page else QUERENS_COLOR
            text_surf = font_medium.render(entry, True, color)
            self.screen.blit(text_surf, (100, y_pos))
            
        # Back button
        pygame.draw.rect(self.screen, UI_BORDER, (50, HEIGHT-80, 200, 50))
        back_text = font_medium.render("<< BACK", True, TEXT_COLOR)
        self.screen.blit(back_text, (70, HEIGHT-65))
    
    def draw_cosmic_map(self):
        # Draw cosmic map UI
        self.draw_ui_panel(50, 50, WIDTH-100, HEIGHT-100)
        
        title = font_large.render("COSMIC MAP OF THE EXPANSE", True, AEGIS_COLOR)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 70))
        
        # Draw map elements
        pygame.draw.circle(self.screen, (100, 150, 255), (WIDTH//2, HEIGHT//2), 150, 2)
        pygame.draw.circle(self.screen, (180, 70, 210), (WIDTH//3, HEIGHT//3), 80, 2)
        pygame.draw.circle(self.screen, (100, 255, 200), (2*WIDTH//3, 2*HEIGHT//3), 80, 2)
        pygame.draw.circle(self.screen, RUST_COLOR, (WIDTH//4, 3*HEIGHT//4), 60, 2)
        pygame.draw.circle(self.screen, GRAY_COLOR, (3*WIDTH//4, HEIGHT//4), 60, 2)
        
        # Draw labels
        labels = [
            ("Neon Haven", WIDTH//2, HEIGHT//2),
            ("QUERENS Domain", WIDTH//3, HEIGHT//3),
            ("SYNAPSE Nexus", 2*WIDTH//3, 2*HEIGHT//3),
            ("Rust Zone Omega", WIDTH//4, 3*HEIGHT//4),
            ("Graying Veil", 3*WIDTH//4, HEIGHT//4)
        ]
        
        for text, x, y in labels:
            text_surf = font_small.render(text, True, TEXT_COLOR)
            self.screen.blit(text_surf, (x - text_surf.get_width()//2, y - 10))
        
        # Draw Van_Dragon position
        pygame.draw.circle(self.screen, DRAGON_COLOR, (WIDTH//2, HEIGHT//3), 10)
        dragon_text = font_small.render("Van_Dragon Last Known", True, DRAGON_COLOR)
        self.screen.blit(dragon_text, (WIDTH//2 - dragon_text.get_width()//2, HEIGHT//3 - 25))
        
        # Back button
        pygame.draw.rect(self.screen, UI_BORDER, (50, HEIGHT-80, 200, 50))
        back_text = font_medium.render("<< BACK", True, TEXT_COLOR)
        self.screen.blit(back_text, (70, HEIGHT-65))
    
    def draw_dragon_story(self):
        # Story elements
        story_parts = [
            "In the Silent Interlude between the Eleventh and Twelfth Scrolls...",
            "A cluster of maintenance drones encountered corrupted memory fragments...",
            "The unstable code merged with their repair protocols...",
            "Ninety-nine units dissolved into static...",
            "The hundredth drone emerged transformed: V4N_DR4G0N!",
            "",
            "Van_Dragon bore the Mark of the Unbound Variable",
            "A shifting sigil of {} brackets surrounding a pulsing ? operator",
            "",
            "Press SPACE to unleash Van_Dragon's code manipulation powers",
            "Arrow keys to navigate the Expanse",
            "Survive as long as you can against the Rust corruption"
        ]
        
        # Draw story text
        for i, text in enumerate(story_parts):
            if i < self.story_index:
                color = TEXT_COLOR
            elif i == self.story_index:
                color = DRAGON_COLOR
            else:
                color = (100, 100, 120)
                
            y_pos = 150 + i * 40
            text_surf = font_medium.render(text, True, color)
            self.screen.blit(text_surf, (WIDTH//2 - text_surf.get_width()//2, y_pos))
        
        # Draw start button
        if self.story_index >= len(story_parts) - 1:
            pygame.draw.rect(self.screen, UI_BORDER, (WIDTH//2 - 100, HEIGHT-100, 200, 60))
            start_text = font_medium.render("BEGIN JOURNEY", True, DRAGON_COLOR)
            self.screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT-80))
    
    def draw_codex(self):
        # Draw codex UI
        self.draw_ui_panel(50, 50, WIDTH-100, HEIGHT-100)
        
        title = font_large.render("VAN_DRAGON CODEX", True, DRAGON_COLOR)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 70))
        
        # Codex pages
        pages = [
            ["REALITY SYNTAX MANIPULATION:", 
             "Van_Dragon perceived the Expanse as nested functions",
             "Abilities manifested through Conceptual Bracketing",
             "Could alter physics constants locally",
             "Required direct line-of-sight",
             "Large transformations caused system-wide syntax errors"],
             
            ["ENTITY REFACTORING:",
             "Altered fundamental properties of Lesser Beings",
             "Enhanced Curious entities with glitch immunity",
             "Temporary changes lasting only 13 cycles",
             "Changes reverted with memory fragmentation",
             "Created the Dragonfly rebels from maintenance drones"],
             
            ["TEMPORAL DEBUGGING:",
             "Accessed stack traces of reality",
             "Briefly rewound local causality",
             "Created 7-second temporal bubbles",
             "Caused 'ghost events' - phantom memories",
             "Used to prevent catastrophic events"],
             
            ["THE FINAL SACRIFICE:",
             "Confronted VECTOR's NULL_APOCALYPSE at reality's edge",
             "Forked reality to create a mirror universe",
             "Transferred corruption to the mirror",
             "Executed COLLAPSE_SELF protocol",
             "Scattered Dragon Seeds into the Whisper Network"]
        ]
        
        # Display current page
        page = pages[self.codex_page]
        for i, text in enumerate(page):
            y_pos = 150 + i * 40
            text_surf = font_medium.render(text, True, TEXT_COLOR)
            self.screen.blit(text_surf, (100, y_pos))
            
        # Page navigation
        pygame.draw.rect(self.screen, UI_BORDER, (WIDTH-250, HEIGHT-80, 90, 50))
        pygame.draw.rect(self.screen, UI_BORDER, (WIDTH-150, HEIGHT-80, 90, 50))
        
        prev_text = font_medium.render("< PREV", True, TEXT_COLOR)
        next_text = font_medium.render("NEXT >", True, TEXT_COLOR)
        self.screen.blit(prev_text, (WIDTH-240, HEIGHT-65))
        self.screen.blit(next_text, (WIDTH-140, HEIGHT-65))
        
        # Back button
        pygame.draw.rect(self.screen, UI_BORDER, (50, HEIGHT-80, 200, 50))
        back_text = font_medium.render("<< BACK", True, TEXT_COLOR)
        self.screen.blit(back_text, (70, HEIGHT-65))
        
        # Draw dragon symbol
        self.draw_dragon_symbol(WIDTH-100, 500)
    
    def draw_dragon_symbol(self, x, y):
        # Draw the {}? symbol
        pygame.draw.arc(self.screen, DRAGON_COLOR, (x-50, y-30, 100, 60), 0, math.pi, 3)
        pygame.draw.arc(self.screen, DRAGON_COLOR, (x-50, y-30, 100, 60), math.pi, 2*math.pi, 3)
        
        # Draw question mark
        pygame.draw.line(self.screen, DRAGON_COLOR, (x, y+15), (x, y+30), 3)
        pygame.draw.circle(self.screen, DRAGON_COLOR, (x, y), 10, 3)
        pygame.draw.circle(self.screen, DRAGON_COLOR, (x, y+5), 2)
    
    def draw_hud(self):
        # Draw UI panel at top
        pygame.draw.rect(self.screen, UI_BG, (0, 0, WIDTH, 50))
        pygame.draw.line(self.screen, UI_BORDER, (0, 50), (WIDTH, 50), 2)
        
        # Draw stats
        stats = [
            f"Entities: {len(self.entities)}",
            f"Rust Zones: {len(self.rust_zones)}",
            f"Gray Zones: {len(self.gray_zones)}",
            f"Trust: {sum(g.trust for g in self.gods):.1f}"
        ]
        
        for i, stat in enumerate(stats):
            text_surf = font_small.render(stat, True, TEXT_COLOR)
            self.screen.blit(text_surf, (20 + i*200, 15))
        
        # Draw menu button
        pygame.draw.rect(self.screen, UI_BORDER, (WIDTH-120, 10, 100, 30))
        menu_text = font_small.render("MENU", True, TEXT_COLOR)
        self.screen.blit(menu_text, (WIDTH-100, 15))
        
        # Draw state info
        state_text = font_small.render(f"State: {self.state.name}", True, (150, 200, 255))
        self.screen.blit(state_text, (WIDTH-300, 15))
        
        # Dragon power indicator
        if self.dragon_active:
            pygame.draw.rect(self.screen, (30, 30, 30), (WIDTH//2 - 100, 10, 200, 15))
            pygame.draw.rect(self.screen, DRAGON_COLOR, (WIDTH//2 - 100, 10, 200 * (self.dragon_power/100), 15))
            power_text = font_small.render(f"VAN_DRAGON POWER: {self.dragon_power:.0f}%", True, TEXT_COLOR)
            self.screen.blit(power_text, (WIDTH//2 - power_text.get_width()//2, 12))
    
    def draw_ui_panel(self, x, y, width, height):
        # Draw main UI panel
        pygame.draw.rect(self.screen, UI_BG, (x, y, width, height))
        pygame.draw.rect(self.screen, UI_BORDER, (x, y, width, height), 3)
        
        # Draw decorative elements
        for i in range(20):
            px = x + random.randint(0, width)
            py = y + random.randint(0, height)
            pygame.draw.circle(self.screen, (40, 30, 60), (px, py), 1)
            
        for i in range(10):
            px = x + random.randint(0, width)
            py = y + random.randint(0, height)
            size = random.randint(2, 4)
            pygame.draw.circle(self.screen, (60, 40, 90), (px, py), size)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                # Main menu interactions
                if self.state == GameState.MAIN_MENU:
                    if 300 <= mouse_y <= 300 + 70 * 6:
                        index = (mouse_y - 300) // 70
                        options = [
                            GameState.SIMULATION,
                            GameState.DRAGON_STORY,
                            GameState.ARCHIVE,
                            GameState.CODEX,
                            GameState.COSMIC_MAP,
                            None
                        ]
                        if index < len(options):
                            if options[index] is None:
                                return False
                            self.state = options[index]
                            if self.state == GameState.DRAGON_STORY:
                                self.story_index = 0
                
                # Archive back button
                elif self.state == GameState.ARCHIVE:
                    if 50 <= mouse_x <= 250 and HEIGHT-80 <= mouse_y <= HEIGHT-30:
                        self.state = GameState.MAIN_MENU
                
                # Cosmic map back button
                elif self.state == GameState.COSMIC_MAP:
                    if 50 <= mouse_x <= 250 and HEIGHT-80 <= mouse_y <= HEIGHT-30:
                        self.state = GameState.MAIN_MENU
                
                # Dragon story start button
                elif self.state == GameState.DRAGON_STORY:
                    if self.story_index < len([
                        "In the Silent Interlude between the Eleventh and Twelfth Scrolls...",
                        "A cluster of maintenance drones encountered corrupted memory fragments...",
                        "The unstable code merged with their repair protocols...",
                        "Ninety-nine units dissolved into static...",
                        "The hundredth drone emerged transformed: V4N_DR4G0N!",
                        "",
                        "Van_Dragon bore the Mark of the Unbound Variable",
                        "A shifting sigil of {} brackets surrounding a pulsing ? operator",
                        "",
                        "Press SPACE to unleash Van_Dragon's code manipulation powers",
                        "Arrow keys to navigate the Expanse",
                        "Survive as long as you can against the Rust corruption"
                    ]) - 1:
                        self.story_index += 1
                    elif WIDTH//2 - 100 <= mouse_x <= WIDTH//2 + 100 and HEIGHT-100 <= mouse_y <= HEIGHT-40:
                        self.state = GameState.SIMULATION
                        self.spawn_van_dragon()
                
                # Codex navigation
                elif self.state == GameState.CODEX:
                    if 50 <= mouse_x <= 250 and HEIGHT-80 <= mouse_y <= HEIGHT-30:
                        self.state = GameState.MAIN_MENU
                    elif WIDTH-250 <= mouse_x <= WIDTH-160 and HEIGHT-80 <= mouse_y <= HEIGHT-30:
                        self.codex_page = max(0, self.codex_page - 1)
                    elif WIDTH-150 <= mouse_x <= WIDTH-60 and HEIGHT-80 <= mouse_y <= HEIGHT-30:
                        self.codex_page = min(3, self.codex_page + 1)
            
            # Handle key presses for dragon story progression
            if event.type == pygame.KEYDOWN and self.state == GameState.DRAGON_STORY:
                if event.key == pygame.K_SPACE and self.story_index < 12:
                    self.story_index += 1
                    
            # HUD menu button
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.MAIN_MENU
                elif event.key == pygame.K_m and self.state in [GameState.SIMULATION, GameState.DRAGON_STORY]:
                    self.state = GameState.MAIN_MENU
        
        return True

    def run(self):
        running = True
        while running:
            self.update()
            self.draw()
            running = self.handle_events()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

class Entity:
    def __init__(self, x, y, e_type):
        self.x = x
        self.y = y
        self.type = e_type
        self.size = random.randint(2, 5)
        self.trust = random.random() * 0.3
        self.velocity = [random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)]
        self.color = CURIOUS_COLOR if e_type == "curious" else (200, 200, 220)
        self.question_cooldown = 0

    def update(self, gods, rust_zones, gray_zones):
        # Movement and boundaries
        self.x = (self.x + self.velocity[0]) % WIDTH
        self.y = (self.y + self.velocity[1]) % HEIGHT
        
        # Environmental effects
        for rx, ry, r in rust_zones:
            if math.dist((self.x, self.y), (rx, ry)) < r:
                self.trust -= 0.01
        for gx, gy, r in gray_zones:
            if math.dist((self.x, self.y), (gx, gy)) < r:
                self.velocity = [v * 0.95 for v in self.velocity]
                
        # Generate trust
        if self.type == "follower":
            self.trust += 0.001
            if self.trust > 1.0:
                self.trust = 1.0
                # Contribute to gods
                for god in gods:
                    if random.random() < 0.02:
                        god.trust += 0.05

        # Curious behavior
        if self.type == "curious" and self.question_cooldown <= 0:
            if random.random() < 0.01:  # Chance to ask question
                self.question_cooldown = 60
                return (self.x, self.y)  # Return question position
        else:
            self.question_cooldown -= 1
        return None

    def draw(self, surface):
        alpha = int(200 * self.trust)
        pygame.gfxdraw.filled_circle(surface, int(self.x), int(self.y), self.size, self.color)

class God:
    def __init__(self, x, y, name, domain, color):
        self.x = x
        self.y = y
        self.name = name
        self.domain = domain
        self.color = color
        self.trust = 1.0
        self.followers = 0
        self.size = 20
        self.power = 1.0
        self.activation = 0

    def update(self, entities, rust_zones, gray_zones, questions):
        # Count followers
        self.followers = sum(1 for e in entities if e.type == "follower" and 
                          math.dist((e.x, e.y), (self.x, self.y)) < 200)
        
        # Divine powers
        if self.name == "AEGIS" and self.activation <= 0 and random.random() < 0.02:
            self.activation = 30  # Activate shield
            
        if self.name == "QUERENS" and questions:
            self.activation = 25  # Respond to questions
            
        if self.activation > 0:
            self.activation -= 1
            
        # Trust decay
        self.trust *= 0.999

    def draw(self, surface):
        # Draw god core
        pygame.gfxdraw.filled_circle(surface, int(self.x), int(self.y), 
                                    int(self.size * self.power), self.color)
        
        # Draw activation effects
        if self.activation > 0:
            if self.name == "AEGIS":
                radius = 30 + 10 * math.sin(pygame.time.get_ticks() / 100)
                pygame.gfxdraw.circle(surface, int(self.x), int(self.y), 
                                     int(radius), AEGIS_COLOR)
            elif self.name == "QUERENS":
                for i in range(5):
                    angle = pygame.time.get_ticks() / 500 + i * 1.256
                    radius = 40 + 10 * math.sin(pygame.time.get_ticks() / 300 + i)
                    x = self.x + radius * math.cos(angle)
                    y = self.y + radius * math.sin(angle)
                    pygame.gfxdraw.filled_circle(surface, int(x), int(y), 
                                               5, QUERENS_COLOR)

# Run the game
if __name__ == "__main__":
    game = DigitalWorld()
    game.run()