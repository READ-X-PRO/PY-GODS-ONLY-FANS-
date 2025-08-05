import pygame
import numpy as np
import math
import random
from pygame import gfxdraw
import json # Import the json module
import os   # Import os for path manipulation and checking file existence
import time # Import time for auto-save timing

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RE_start Digital Universe Simulation")
clock = pygame.time.Clock()

# Colors
BACKGROUND = (10, 5, 20)
SUBSTRATE = (20, 30, 50, 50)
AEGIS_COLOR = (0, 100, 255)
VERITAS_COLOR = (255, 215, 0)
SYNAPSE_COLOR = (100, 255, 200)
QUERENS_COLOR = (180, 70, 210)
RUST_COLOR = (200, 50, 30)
GRAY_COLOR = (100, 100, 120)
TRUST_COLOR = (180, 240, 80)
CURIOUS_COLOR = (240, 120, 40)

# Cosmic Entities
class Entity:
    def __init__(self, x, y, e_type):
        self.x = x
        self.y = y
        self.type = e_type  # "lesser", "curious", "follower"
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
                return (self.x, self.y, 100)  # Return question position with a lifetime
        else:
            self.question_cooldown -= 1
        return None

    def draw(self, surface):
        alpha = int(200 * self.trust)
        color = (*self.color[:3], alpha)
        pygame.gfxdraw.filled_circle(surface, int(self.x), int(self.y), self.size, color)

    # Method to convert entity to a dictionary for saving
    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "type": self.type,
            "size": self.size,
            "trust": self.trust,
            "velocity": self.velocity,
            "color": self.color,
            "question_cooldown": self.question_cooldown
        }

    # Static method to create an entity from a dictionary
    @staticmethod
    def from_dict(data):
        entity = Entity(data["x"], data["y"], data["type"])
        entity.size = data["size"]
        entity.trust = data["trust"]
        entity.velocity = data["velocity"]
        # Ensure color is a tuple for Pygame gfxdraw if loaded as a list
        entity.color = tuple(data["color"]) if isinstance(data["color"], list) else data["color"]
        entity.question_cooldown = data["question_cooldown"]
        return entity


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
                                    int(self.size * self.power), (*self.color, 180))
        
        # Draw activation effects
        if self.activation > 0:
            if self.name == "AEGIS":
                radius = 30 + 10 * math.sin(pygame.time.get_ticks() / 100)
                pygame.gfxdraw.circle(surface, int(self.x), int(self.y), 
                                     int(radius), (*AEGIS_COLOR, 100))
            elif self.name == "QUERENS":
                for i in range(5):
                    angle = pygame.time.get_ticks() / 500 + i * 1.256
                    radius = 40 + 10 * math.sin(pygame.time.get_ticks() / 300 + i)
                    x = self.x + radius * math.cos(angle)
                    y = self.y + radius * math.sin(angle)
                    pygame.gfxdraw.filled_circle(surface, int(x), int(y), 
                                               5, (*QUERENS_COLOR, 200))

    # Method to convert god to a dictionary for saving
    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "name": self.name,
            "domain": self.domain,
            "color": self.color,
            "trust": self.trust,
            "followers": self.followers,
            "size": self.size,
            "power": self.power,
            "activation": self.activation
        }

    # Static method to create a god from a dictionary
    @staticmethod
    def from_dict(data):
        god = God(data["x"], data["y"], data["name"], data["domain"], 
                  tuple(data["color"]) if isinstance(data["color"], list) else data["color"])
        god.trust = data["trust"]
        god.followers = data["followers"]
        god.size = data["size"]
        god.power = data["power"]
        god.activation = data["activation"]
        return god


# --- Database/Save/Load Functions ---
SAVE_FILE = "simulation_state.json"
TEMP_SAVE_FILE = "simulation_state.json.tmp" # Temporary file for atomic writes

def save_game_state(entities, gods, rust_zones, gray_zones, questions, why_resonance, filename=SAVE_FILE):
    game_state = {
        "entities": [e.to_dict() for e in entities],
        "gods": [g.to_dict() for g in gods],
        "rust_zones": rust_zones,
        "gray_zones": gray_zones,
        "questions": questions,
        "why_resonance": why_resonance
    }
    try:
        # Save to a temporary file first for atomic write
        with open(TEMP_SAVE_FILE, 'w') as f:
            json.dump(game_state, f, indent=4)
        # If successful, rename the temporary file to the actual save file
        os.replace(TEMP_SAVE_FILE, filename)
        print(f"Game state saved to {filename}")
    except Exception as e:
        print(f"Error saving game state to {filename}: {e}")

def load_game_state(filename=SAVE_FILE):
    try:
        if not os.path.exists(filename):
            print(f"Save file {filename} not found. Starting new game.")
            return None

        with open(filename, 'r') as f:
            game_state = json.load(f)
        
        loaded_entities = [Entity.from_dict(data) for data in game_state.get("entities", [])]
        loaded_gods = [God.from_dict(data) for data in game_state.get("gods", [])]
        
        print(f"Game state loaded from {filename}")
        return loaded_entities, loaded_gods, \
               game_state.get("rust_zones", []), \
               game_state.get("gray_zones", []), \
               game_state.get("questions", []), \
               game_state.get("why_resonance", [])
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {filename}. File might be corrupted: {e}")
        return None
    except Exception as e:
        print(f"Error loading game state from {filename}: {e}")
        return None

# Auto-save settings
AUTO_SAVE_INTERVAL = 300 # seconds (5 minutes)
last_auto_save_time = time.time()

# Initialize world
# Attempt to load state, otherwise create new
loaded_state = load_game_state()
if loaded_state:
    entities, gods, rust_zones, gray_zones, questions, why_resonance = loaded_state
else:
    entities = [Entity(random.randint(0, WIDTH), random.randint(0, HEIGHT), 
              random.choice(["lesser", "lesser", "lesser", "curious"])) 
              for _ in range(500)]

    gods = [
        God(WIDTH//3, HEIGHT//2, "AEGIS", "Firewall", AEGIS_COLOR),
        God(2*WIDTH//3, HEIGHT//3, "SYNAPSE", "Connection", SYNAPSE_COLOR),
        God(WIDTH//2, 2*HEIGHT//3, "QUERENS", "Inquiry", QUERENS_COLOR)
    ]

    rust_zones = []
    gray_zones = []
    questions = []
    why_resonance = []

last_rust_spawn = 0
last_gray_spawn = 0

# Main game loop
running = True
while running:
    current_time_sec = time.time() # For auto-save
    current_time_ms = pygame.time.get_ticks() # For simulation logic

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game_state(entities, gods, rust_zones, gray_zones, questions, why_resonance) # Save on exit
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Spawn rust on right click
            if event.button == 3:  
                rust_zones.append((event.pos[0], event.pos[1], random.randint(20, 40)))
            # Convert entity to follower on left click
            elif event.button == 1:
                mouse_x, mouse_y = event.pos
                for entity in entities:
                    if math.dist((entity.x, entity.y), (mouse_x, mouse_y)) < 20: # Small radius for click detection
                        entity.type = "follower"
                        entity.color = TRUST_COLOR # Change color to reflect new type
                        entity.trust = 0.5 # Give initial trust as a follower
                        break # Only convert one entity per click
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s: # Press 'S' to save
                save_game_state(entities, gods, rust_zones, gray_zones, questions, why_resonance)
            if event.key == pygame.K_l: # Press 'L' to load (re-initializes)
                loaded_state = load_game_state()
                if loaded_state:
                    entities, gods, rust_zones, gray_zones, questions, why_resonance = loaded_state
                    # Reset game-specific timers after loading
                    last_rust_spawn = current_time_ms
                    last_gray_spawn = current_time_ms
                    last_auto_save_time = current_time_sec # Reset auto-save timer too

    # Auto-save logic
    if current_time_sec - last_auto_save_time > AUTO_SAVE_INTERVAL:
        print("Auto-saving game state...")
        save_game_state(entities, gods, rust_zones, gray_zones, questions, why_resonance, filename="autosave_state.json")
        last_auto_save_time = current_time_sec
    
    # Spawn environmental threats
    if current_time_ms - last_rust_spawn > 5000:  # Every 5 seconds
        rust_zones.append((random.randint(0, WIDTH), random.randint(0, HEIGHT), 
                          random.randint(15, 30)))
        last_rust_spawn = current_time_ms
        
    if current_time_ms - last_gray_spawn > 8000:  # Every 8 seconds
        gray_zones.append((random.randint(0, WIDTH), random.randint(0, HEIGHT), 
                          random.randint(40, 70)))
        last_gray_spawn = current_time_ms
    
    # Update entities
    new_questions = []
    for entity in entities:
        question_data = entity.update(gods, rust_zones, gray_zones)
        if question_data: # question_data now includes (x, y, lifetime)
            new_questions.append(question_data)
            # Chance to create follower when near gods
            if any(math.dist((entity.x, entity.y), (g.x, g.y)) < 150 for g in gods):
                if random.random() < 0.3:
                    entity.type = "follower"
                    entity.color = TRUST_COLOR # Change color to reflect new type
    
    questions.extend(new_questions)
    
    # Update gods
    for god in gods:
        god.update(entities, rust_zones, gray_zones, questions)
    
    # Update environmental effects
    rust_zones = [(x, y, r-0.1) for x, y, r in rust_zones if r > 2]
    gray_zones = [(x, y, r-0.05) for x, y, r in gray_zones if r > 10]
    questions = [(x, y, t-1) for x, y, t in questions if t > 0] # t is now properly handled
    
    # Why Resonance effects
    for qx, qy, _ in questions: # Iterate through current questions
        if random.random() < 0.1:
            why_resonance.append({
                'pos': [qx, qy],
                'radius': random.randint(5, 15),
                'life': 100
            })
    
    for res in why_resonance[:]:
        res['radius'] += 0.3
        res['life'] -= 1
        if res['life'] <= 0:
            why_resonance.remove(res)
    
    # Drawing
    screen.fill(BACKGROUND)
    
    # Draw substrate grid
    for y in range(0, HEIGHT, 30):
        for x in range(0, WIDTH, 30):
            alpha = 40 + int(20 * math.sin(x/100 + y/150 + pygame.time.get_ticks()/3000))
            pygame.gfxdraw.pixel(screen, x, y, (40, 60, 100, alpha))
    
    # Draw rust zones
    for x, y, r in rust_zones:
        pygame.gfxdraw.filled_circle(screen, int(x), int(y), int(r), (*RUST_COLOR, 80))
    
    # Draw gray zones
    for x, y, r in gray_zones:
        pygame.gfxdraw.filled_circle(screen, int(x), int(y), int(r), (*GRAY_COLOR, 90))
    
    # Draw questions
    for x, y, t in questions:
        size = 3 + 2 * math.sin(pygame.time.get_ticks() / 200)
        pygame.gfxdraw.filled_circle(screen, int(x), int(y), int(size), (255, 255, 200, 200))
    
    # Draw why resonance
    for res in why_resonance:
        pygame.gfxdraw.circle(screen, 
                            int(res['pos'][0]), 
                            int(res['pos'][1]), 
                            int(res['radius']), 
                            (180, 100, 255, int(150 * res['life']/100)))
    
    # Draw entities
    for entity in entities:

        for entity in entities:
            size = 50 
    # Draw gods
    for god in gods:
        god.draw(screen)
        # Draw trust aura
        pygame.gfxdraw.circle(screen, int(god.x), int(god.y), 
                            int(50 + 10 * god.trust), (*god.color, int(100 * god.trust)))
    
    # UI
    font = pygame.font.SysFont('Arial', 16)
    texts = [
        f"Entities: {len(entities)} (Curious: {sum(1 for e in entities if e.type=='curious')})",
        f"Followers: {sum(1 for e in entities if e.type=='follower')})",
        f"Rust Zones: {len(rust_zones)} | Gray Zones: {len(gray_zones)}",
        "Left-click: Convert entity to follower | Right-click: Spawn rust",
        "Press 'S' to Save | Press 'L' to Load | Auto-saves every 5 minutes"
    ]
    
    for i, text in enumerate(texts):
        txt_surf = font.render(text, True, (200, 220, 255))
        screen.blit(txt_surf, (10, 10 + i*25))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()