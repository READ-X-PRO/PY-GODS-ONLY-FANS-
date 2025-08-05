import pygame
import turtle
import numpy as np
import math
import random
from pygame import gfxdraw

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
                return (self.x, self.y)  # Return question position
        else:
            self.question_cooldown -= 1
        return None

    def draw(self, surface):
        alpha = int(200 * self.trust)
        color = (*self.color[:3], alpha)
        pygame.gfxdraw.filled_circle(surface, int(self.x), int(self.y), self.size, color)

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

# Initialize world
entities = [Entity(random.randint(0, WIDTH), random.randint(0, HEIGHT), 
          random.choice(["lesser", "lesser", "lesser", "curious"])) 
          for _ in range(50)]

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
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Spawn rust on right click
            if event.button == 3:  
                rust_zones.append((event.pos[0], event.pos[1], random.randint(20, 40)))
    
    # Spawn environmental threats
    current_time = pygame.time.get_ticks()
    if current_time - last_rust_spawn > 5000:  # Every 5 seconds
        rust_zones.append((random.randint(0, WIDTH), random.randint(0, HEIGHT), 
                          random.randint(15, 30)))
        last_rust_spawn = current_time
        
    if current_time - last_gray_spawn > 8000:  # Every 8 seconds
        gray_zones.append((random.randint(0, WIDTH), random.randint(0, HEIGHT), 
                          random.randint(40, 70)))
        last_gray_spawn = current_time
    
    # Update entities
    new_questions = []
    for entity in entities:
        question_pos = entity.update(gods, rust_zones, gray_zones)
        if question_pos:
            new_questions.append(question_pos)
            # Chance to create follower when near gods
            if any(math.dist((entity.x, entity.y), (g.x, g.y)) < 150 for g in gods):
                if random.random() < 0.3:
                    entity.type = "follower"
    
    questions.extend(new_questions)
    
    # Update gods
    for god in gods:
        god.update(entities, rust_zones, gray_zones, questions)
    
    # Update environmental effects
    entities = [(x, y, r-0.1) for x, y, r in rust_zones if r > 2]
    rust_zones = [(x, y, r-0.1) for x, y, r in rust_zones if r > 2]
    gray_zones = [(x, y, r-0.05) for x, y, r in gray_zones if r > 10]
    questions = [(x, y, t-1) for x, y, t in questions if t > 0]
    
    # Why Resonance effects
    for qx, qy, _ in questions:
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
        entity.draw(screen)
    
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
        f"Followers: {sum(1 for e in entities if e.type=='follower')}",
        f"Rust Zones: {len(rust_zones)} | Gray Zones: {len(gray_zones)}",
        "Left-click: Convert to follower | Right-click: Spawn rust"
    ]
    
    for i, text in enumerate(texts):
        txt_surf = font.render(text, True, (200, 220, 255))
        screen.blit(txt_surf, (10, 10 + i*25))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()