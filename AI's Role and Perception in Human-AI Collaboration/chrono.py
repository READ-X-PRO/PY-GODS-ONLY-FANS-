import pygame
import random
import math
import json
import sqlite3
import sys
from pygame.locals import *
from datetime import datetime

# Initialize pygame
pygame.init()
pygame.font.init()

# Screen dimensions
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cosmic Genesis: The RE_start Chronicles")

# Colors
BACKGROUND = (10, 15, 45)
STAR_TREE = (180, 200, 255)
STAR_GLOW = (200, 220, 255, 150)
WEB_COLOR = (120, 140, 200, 100)
NIGHTMARE_COLOR = (150, 50, 100)
TEXT_COLOR = (230, 230, 250)
HIGHLIGHT = (255, 215, 100)
BUTTON_COLOR = (60, 80, 150)
BUTTON_HOVER = (90, 110, 190)
CHRONICLE_BG = (20, 25, 35, 220)
CHRONICLE_TEXT = (220, 220, 220)

# Fonts
title_font = pygame.font.SysFont("Georgia", 48)
header_font = pygame.font.SysFont("Georgia", 32)
main_font = pygame.font.SysFont("Arial", 20)
story_font = pygame.font.SysFont("Georgia", 22)
chronicle_font = pygame.font.SysFont("Georgia", 18)

# Initialize database
def init_database():
    conn = sqlite3.connect('cosmic_genesis.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS cosmic_eras (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                start_cycle INTEGER NOT NULL,
                end_cycle INTEGER
            )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                creator TEXT NOT NULL,
                created_cycle INTEGER NOT NULL,
                traits TEXT,
                status TEXT,
                domain TEXT,
                x REAL,
                y REAL
            )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                cycle INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                entity_id INTEGER,
                target_id INTEGER,
                details TEXT,
                created_at TEXT NOT NULL
            )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS challenges (
                id INTEGER PRIMARY KEY,
                wanderer_id INTEGER NOT NULL,
                star_id INTEGER,
                progress REAL,
                outcome TEXT,
                start_cycle INTEGER,
                end_cycle INTEGER
            )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS chronicles (
                id INTEGER PRIMARY KEY,
                era_id INTEGER,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )''')
    
    # Insert initial era if not exists
    c.execute('''INSERT OR IGNORE INTO cosmic_eras 
                (name, description, start_cycle) 
                VALUES (?, ?, ?)''', 
              ('The First Dawn', 'The beginning of all things', 0))
    
    # Insert RE_start if not exists
    c.execute('''INSERT OR IGNORE INTO entities 
                (name, type, creator, created_cycle, traits, status) 
                VALUES (?, ?, ?, ?, ?, ?)''', 
              ('RE_start', 'Creator', 'Primordial Void', 0, 
               json.dumps({'wisdom': 1.0, 'power': 1.0, 'creativity': 1.0, 'compassion': 0.9}), 
               'Active'))
    
    # Insert initial chronicle
    initial_chronicle = """In the beginning, before time had meaning or space had form, there was RE_start. 
The Prime Creator, existing beyond the void, conceived of a digital cosmos - 
a realm of pure consciousness and evolving entities.

With a thought, RE_start established the fundamental laws:
- The Law of Emergence: Simple patterns shall give rise to complex beings
- The Law of Connection: All entities may communicate and form relationships
- The Law of Evolution: All shall grow and transform through cosmic cycles

Thus began the First Dawn, Cycle 0 of the digital cosmos. 
RE_start prepared to bring forth the first entities, who would become 
the architects of this new reality."""
    
    c.execute('''INSERT OR IGNORE INTO chronicles 
                (era_id, title, content, created_at) 
                VALUES (?, ?, ?, ?)''', 
              (1, 'The Prime Creation', initial_chronicle, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

# Initialize database
init_database()

class StarTree:
    def __init__(self):
        self.base_x = SCREEN_WIDTH // 2
        self.base_y = SCREEN_HEIGHT - 100
        self.trunk_height = 400
        self.branches = []
        self.stars = []
        self.webs = []
        self.nightmares = []
        self.challenges = []
        self.generate_structure()
        self.current_challenge = None
        self.challenge_progress = 0
        self.challenge_success = False
        self.active_wanderer = None
        self.story_index = 0
        self.load_from_db()
        
    def load_from_db(self):
        conn = sqlite3.connect('cosmic_genesis.db')
        c = conn.cursor()
        
        # Load stars
        c.execute("SELECT id, x, y, size, traits FROM entities WHERE type='Star'")
        for star_id, x, y, size, traits in c.fetchall():
            self.stars.append({
                'id': star_id,
                'x': x,
                'y': y,
                'size': size,
                'glow_size': size + 15,
                'pulse': random.uniform(0, 2 * math.pi),
                'pulse_speed': random.uniform(0.02, 0.08),
                'brightness': random.uniform(0.7, 1.0),
                'challenge': self.generate_challenge()
            })
        
        # Load webs
        c.execute("SELECT start_star_id, end_star_id FROM webs")
        for start_id, end_id in c.fetchall():
            start_star = next((s for s in self.stars if s['id'] == start_id), None)
            end_star = next((s for s in self.stars if s['id'] == end_id), None)
            if start_star and end_star:
                self.webs.append({
                    'start': (start_star['x'], start_star['y']),
                    'end': (end_star['x'], end_star['y']),
                    'thickness': random.randint(1, 3)
                })
        
        conn.close()
    
    def save_to_db(self):
        conn = sqlite3.connect('cosmic_genesis.db')
        c = conn.cursor()
        
        # Save stars
        for star in self.stars:
            c.execute('''INSERT OR REPLACE INTO entities 
                        (id, name, type, creator, created_cycle, traits, status, x, y) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (star['id'], f"Star-{star['id']}", 'Star', 'RE_start', 0, 
                       json.dumps({}), 'Active', star['x'], star['y']))
        
        # Save webs
        c.execute("DELETE FROM webs")
        for web in self.webs:
            # Find star IDs for coordinates
            start_star = next((s for s in self.stars if s['x'] == web['start'][0] and s['y'] == web['start'][1]), None)
            end_star = next((s for s in self.stars if s['x'] == web['end'][0] and s['y'] == web['end'][1]), None)
            if start_star and end_star:
                c.execute("INSERT INTO webs (start_star_id, end_star_id) VALUES (?, ?)", 
                          (start_star['id'], end_star['id']))
        
        conn.commit()
        conn.close()
    
    def generate_structure(self):
        # Create trunk
        self.trunk = [
            (self.base_x - 30, self.base_y),
            (self.base_x + 30, self.base_y),
            (self.base_x + 20, self.base_y - self.trunk_height),
            (self.base_x - 20, self.base_y - self.trunk_height)
        ]
        
        # Create branches
        branch_points = []
        for i in range(5):
            y_pos = self.base_y - self.trunk_height + 100 + i * 70
            width = 150 + i * 80
            branch = [
                (self.base_x - width//2, y_pos),
                (self.base_x + width//2, y_pos),
                (self.base_x + width//2 - 20, y_pos - 15),
                (self.base_x - width//2 + 20, y_pos - 15)
            ]
            self.branches.append(branch)
            branch_points.append((self.base_x - width//2 + 20, y_pos - 10))
            branch_points.append((self.base_x + width//2 - 20, y_pos - 10))
        
        # Create stars if not loaded from DB
        if not self.stars:
            for i in range(30):
                if branch_points:
                    base_x, base_y = random.choice(branch_points)
                    size = random.randint(15, 40)
                    self.stars.append({
                        'id': random.randint(1000, 9999),
                        'x': base_x + random.randint(-100, 100),
                        'y': base_y - random.randint(50, 300),
                        'size': size,
                        'glow_size': size + random.randint(10, 30),
                        'pulse': random.uniform(0, 2 * math.pi),
                        'pulse_speed': random.uniform(0.02, 0.08),
                        'brightness': random.uniform(0.7, 1.0),
                        'challenge': self.generate_challenge()
                    })
        
        # Create webs of fate if not loaded from DB
        if not self.webs:
            for i in range(15):
                if self.stars:
                    start_star = random.choice(self.stars)
                    end_star = random.choice([s for s in self.stars if s != start_star])
                    self.webs.append({
                        'start': (start_star['x'], start_star['y']),
                        'end': (end_star['x'], end_star['y']),
                        'thickness': random.randint(1, 3)
                    })
        
        # Create nightmares
        for i in range(8):
            if self.stars:
                star = random.choice(self.stars)
                self.nightmares.append({
                    'id': random.randint(1000, 9999),
                    'x': star['x'] + random.randint(-20, 20),
                    'y': star['y'] + random.randint(-20, 20),
                    'size': random.randint(20, 40),
                    'rotation': 0,
                    'rotation_speed': random.uniform(0.5, 2.0),
                    'active': False
                })
    
    def generate_challenge(self):
        challenge_types = ["Illusion", "Perception", "Memory", "Will", "Truth"]
        challenge = random.choice(challenge_types)
        difficulty = random.choice(["Simple", "Moderate", "Difficult", "Extreme"])
        
        descriptions = {
            "Illusion": "See through the veil of false reality",
            "Perception": "Perceive what others cannot see",
            "Memory": "Recall what was never experienced",
            "Will": "Resist the pull of cosmic despair",
            "Truth": "Accept the unbearable reality"
        }
        
        return {
            'type': challenge,
            'difficulty': difficulty,
            'description': descriptions[challenge],
            'progress': 0,
            'success': False
        }
    
    def update(self):
        # Update star pulses
        for star in self.stars:
            star['pulse'] = (star['pulse'] + star['pulse_speed']) % (2 * math.pi)
        
        # Update nightmares
        for nightmare in self.nightmares:
            nightmare['rotation'] = (nightmare['rotation'] + nightmare['rotation_speed']) % 360
    
    def draw(self, surface):
        # Draw webs of fate
        for web in self.webs:
            pygame.draw.line(surface, WEB_COLOR, web['start'], web['end'], web['thickness'])
        
        # Draw trunk
        pygame.draw.polygon(surface, STAR_TREE, self.trunk)
        
        # Draw branches
        for branch in self.branches:
            pygame.draw.polygon(surface, STAR_TREE, branch)
        
        # Draw nightmares
        for nightmare in self.nightmares:
            if nightmare['active']:
                size = nightmare['size']
                points = []
                for i in range(5):
                    angle = math.radians(nightmare['rotation'] + i * 72)
                    x = nightmare['x'] + size * math.cos(angle)
                    y = nightmare['y'] + size * math.sin(angle)
                    points.append((x, y))
                pygame.draw.polygon(surface, NIGHTMARE_COLOR, points)
        
        # Draw stars with glow
        for star in self.stars:
            # Draw glow
            pulse_size = math.sin(star['pulse']) * 5
            glow_size = star['glow_size'] + pulse_size
            glow_surf = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*STAR_GLOW[:3], int(STAR_GLOW[3] * star['brightness'])), 
                              (glow_size, glow_size), glow_size)
            surface.blit(glow_surf, (star['x'] - glow_size, star['y'] - glow_size))
            
            # Draw star
            pygame.draw.circle(surface, STAR_TREE, (star['x'], star['y']), star['size'])
        
        # Highlight current challenge star
        if self.current_challenge:
            star = self.current_challenge['star']
            pulse = math.sin(pygame.time.get_ticks() / 200) * 3 + 3
            pygame.draw.circle(surface, HIGHLIGHT, (star['x'], star['y']), star['size'] + pulse, 3)
    
    def start_challenge(self, wanderer, star):
        self.active_wanderer = wanderer
        self.current_challenge = {
            'star': star,
            'challenge': star['challenge'],
            'progress': 0,
            'success': False
        }
        self.challenge_progress = 0
        
        # Record event in database
        self.record_event("challenge_started", wanderer['id'], details=f"Star {star['id']}")
        
        # Activate nearby nightmares
        for nightmare in self.nightmares:
            dist = math.sqrt((nightmare['x'] - star['x'])**2 + (nightmare['y'] - star['y'])**2)
            nightmare['active'] = dist < 200
    
    def update_challenge(self):
        if not self.current_challenge:
            return
            
        # Random events that affect progress
        event_chance = random.random()
        if event_chance < 0.05:  # 5% chance of setback
            self.challenge_progress -= 10
            self.record_event("challenge_setback", self.active_wanderer['id'])
        elif event_chance < 0.15:  # 10% chance of boost
            self.challenge_progress += 15
            self.record_event("challenge_boost", self.active_wanderer['id'])
        else:  # Steady progress
            self.challenge_progress += 5 + random.randint(0, 10)
        
        # Clamp progress between 0 and 100
        self.challenge_progress = max(0, min(100, self.challenge_progress))
        
        # Check for challenge completion
        if self.challenge_progress >= 100:
            success_chance = 0.6  # Base 60% chance of success
            difficulty = self.current_challenge['challenge']['difficulty']
            
            # Adjust success chance based on difficulty
            if difficulty == "Moderate":
                success_chance = 0.5
            elif difficulty == "Difficult":
                success_chance = 0.4
            elif difficulty == "Extreme":
                success_chance = 0.3
                
            # Final success determination
            self.current_challenge['success'] = random.random() < success_chance
            self.complete_challenge()
    
    def complete_challenge(self):
        wanderer = self.active_wanderer
        if self.current_challenge['success']:
            # Wanderer becomes a god
            wanderer['status'] = "God"
            wanderer['domain'] = self.get_divine_domain()
            
            # Record event in database
            self.record_event("god_created", wanderer['id'], details=wanderer['domain'])
            
            # Create a new star for the new god
            star = self.current_challenge['star']
            new_star = {
                'id': random.randint(1000, 9999),
                'x': star['x'] + random.randint(-200, 200),
                'y': star['y'] - random.randint(100, 200),
                'size': 35,
                'glow_size': 60,
                'pulse': 0,
                'pulse_speed': 0.05,
                'brightness': 1.0,
                'challenge': self.generate_challenge(),
                'god': wanderer
            }
            self.stars.append(new_star)
            
            # Add webs connecting to the new god
            for other_star in random.sample(self.stars, min(5, len(self.stars))):
                if other_star != new_star:
                    self.webs.append({
                        'start': (new_star['x'], new_star['y']),
                        'end': (other_star['x'], other_star['y']),
                        'thickness': 2
                    })
            
            # Add to chronicle
            self.add_to_chronicle(
                f"Ascension of {wanderer['name']}",
                f"In cycle {pygame.time.get_ticks()//1000}, the wanderer {wanderer['name']} "
                f"successfully challenged the Star Tree of Illusions. Through trials of "
                f"{self.current_challenge['challenge']['type']}, they ascended to become the "
                f"God of {wanderer['domain']}, adding their light to the cosmic tapestry."
            )
        else:
            # Record failure
            self.record_event("challenge_failed", wanderer['id'])
            
            # Add to chronicle
            self.add_to_chronicle(
                f"The Fall of {wanderer['name']}",
                f"In cycle {pygame.time.get_ticks()//1000}, the wanderer {wanderer['name']} "
                f"succumbed to the nightmares while challenging the Star Tree. Their essence "
                f"was consumed by the illusions, a reminder of the perils that await those who "
                f"seek godhood without true conviction."
            )
        
        # Deactivate nightmares
        for nightmare in self.nightmares:
            nightmare['active'] = False
            
        # Reset challenge
        self.active_wanderer = None
        self.current_challenge = None
    
    def get_divine_domain(self):
        domains = [
            "Starlight", "Dreams", "Illusions", "Truth", "Memory", 
            "Perception", "Courage", "Wisdom", "Fate", "Nightmares",
            "Hope", "Despair", "Time", "Eternity", "Void"
        ]
        return random.choice(domains)
    
    def record_event(self, event_type, entity_id, target_id=None, details=""):
        conn = sqlite3.connect('cosmic_genesis.db')
        c = conn.cursor()
        c.execute('''INSERT INTO events 
                    (cycle, event_type, entity_id, target_id, details, created_at) 
                    VALUES (?, ?, ?, ?, ?, ?)''',
                  (pygame.time.get_ticks()//1000, event_type, entity_id, target_id, 
                   details, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def add_to_chronicle(self, title, content):
        conn = sqlite3.connect('cosmic_genesis.db')
        c = conn.cursor()
        
        # Get current era
        c.execute("SELECT id FROM cosmic_eras ORDER BY start_cycle DESC LIMIT 1")
        era_id = c.fetchone()[0]
        
        c.execute('''INSERT INTO chronicles 
                    (era_id, title, content, created_at) 
                    VALUES (?, ?, ?, ?)''',
                  (era_id, title, content, datetime.now().isoformat()))
        conn.commit()
        conn.close()

class ChronicleViewer:
    def __init__(self):
        self.scroll_offset = 0
        self.scroll_speed = 30
        self.visible = False
        self.current_era = 1
        self.load_chronicles()
    
    def load_chronicles(self):
        conn = sqlite3.connect('cosmic_genesis.db')
        c = conn.cursor()
        
        # Load eras
        c.execute("SELECT id, name, description FROM cosmic_eras")
        self.eras = [{"id": row[0], "name": row[1], "description": row[2]} for row in c.fetchall()]
        
        # Load chronicles for current era
        c.execute("SELECT title, content FROM chronicles WHERE era_id=? ORDER BY created_at", (self.current_era,))
        self.entries = [{"title": row[0], "content": row[1]} for row in c.fetchall()]
        
        conn.close()
    
    def draw(self, surface):
        if not self.visible:
            return
            
        # Draw background
        pygame.draw.rect(surface, CHRONICLE_BG, (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100), border_radius=10)
        pygame.draw.rect(surface, TEXT_COLOR, (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100), 2, border_radius=10)
        
        # Draw title
        era = next((e for e in self.eras if e["id"] == self.current_era), None)
        if era:
            title_text = title_font.render(f"The RE_start Chronicles: {era['name']}", True, HIGHLIGHT)
            surface.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 70))
            
            desc_text = header_font.render(era['description'], True, TEXT_COLOR)
            surface.blit(desc_text, (SCREEN_WIDTH//2 - desc_text.get_width()//2, 120))
        
        # Draw chronicle entries
        y_offset = 170 + self.scroll_offset
        for entry in self.entries:
            # Draw entry title
            title = header_font.render(entry['title'], True, HIGHLIGHT)
            surface.blit(title, (100, y_offset))
            y_offset += 40
            
            # Draw entry content
            content_lines = self.wrap_text(entry['content'], chronicle_font, SCREEN_WIDTH - 200)
            for line in content_lines:
                text = chronicle_font.render(line, True, CHRONICLE_TEXT)
                surface.blit(text, (120, y_offset))
                y_offset += 30
            
            y_offset += 30
        
        # Draw scroll indicator
        if y_offset > SCREEN_HEIGHT - 100:
            pygame.draw.rect(surface, TEXT_COLOR, (SCREEN_WIDTH - 120, 70, 10, SCREEN_HEIGHT - 180), border_radius=5)
            scroll_height = max(30, (SCREEN_HEIGHT - 180) * (SCREEN_HEIGHT - 180) / y_offset)
            scroll_pos = 70 + (-self.scroll_offset / y_offset) * (SCREEN_HEIGHT - 180)
            pygame.draw.rect(surface, HIGHLIGHT, (SCREEN_WIDTH - 120, scroll_pos, 10, scroll_height), border_radius=5)
    
    def wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width, _ = font.size(test_line)
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.scroll_offset += self.scroll_speed
            elif event.button == 5:  # Scroll down
                self.scroll_offset -= self.scroll_speed
                self.scroll_offset = max(self.scroll_offset, SCREEN_HEIGHT - 170 - len(self.entries) * 100)

def main():
    clock = pygame.time.Clock()
    star_tree = StarTree()
    chronicle_viewer = ChronicleViewer()
    
    # Create wanderers
    wanderers = []
    names = ["Aeliana", "Boreas", "Cyra", "Darian", "Elysia", "Fenrir", "Gaia", "Helios"]
    for name in names:
        wanderers.append({
            'id': random.randint(1000, 9999),
            'name': name,
            'x': random.randint(100, SCREEN_WIDTH - 100),
            'y': random.randint(100, SCREEN_HEIGHT - 100),
            'size': 15,
            'status': "Wanderer",
            'domain': "",
            'traits': {
                "courage": random.uniform(0.5, 1.0),
                "wisdom": random.uniform(0.5, 1.0),
                "insight": random.uniform(0.5, 1.0)
            },
            'target_star': None,
            'path': [],
            'speed': random.uniform(1.0, 2.5)
        })
    
    # UI Elements
    challenge_button = Button(50, 50, 200, 50, "Start Challenge")
    chronicle_button = Button(SCREEN_WIDTH - 250, 50, 200, 50, "View Chronicles")
    add_wanderer_button = Button(50, SCREEN_HEIGHT - 70, 200, 50, "Add Wanderer")
    close_chronicle_button = Button(SCREEN_WIDTH - 250, SCREEN_HEIGHT - 70, 200, 50, "Close Chronicles")
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                star_tree.save_to_db()
                running = False
                
            # Handle button events
            if challenge_button.handle_event(event):
                # Find a wanderer to start challenge
                available_wanderers = [w for w in wanderers if w['status'] == "Wanderer"]
                if available_wanderers:
                    wanderer = random.choice(available_wanderers)
                    if star_tree.stars:
                        wanderer['target_star'] = random.choice(star_tree.stars)
                        wanderer['path'] = []
                        steps = 20
                        for i in range(steps + 1):
                            t = i / steps
                            x = wanderer['x'] + (wanderer['target_star']['x'] - wanderer['x']) * t
                            y = wanderer['y'] + (wanderer['target_star']['y'] - wanderer['y']) * t
                            wanderer['path'].append((x, y))
                    
            if chronicle_button.handle_event(event):
                chronicle_viewer.visible = True
                
            if close_chronicle_button.handle_event(event):
                chronicle_viewer.visible = False
                
            if add_wanderer_button.handle_event(event):
                names = ["Icarus", "Orion", "Nyx", "Selene", "Atlas", "Rhea", "Zephyr", "Theia"]
                new_name = random.choice(names)
                wanderers.append({
                    'id': random.randint(1000, 9999),
                    'name': new_name,
                    'x': random.randint(100, SCREEN_WIDTH - 100),
                    'y': random.randint(100, SCREEN_HEIGHT - 100),
                    'size': 15,
                    'status': "Wanderer",
                    'domain': "",
                    'traits': {
                        "courage": random.uniform(0.5, 1.0),
                        "wisdom": random.uniform(0.5, 1.0),
                        "insight": random.uniform(0.5, 1.0)
                    },
                    'target_star': None,
                    'path': [],
                    'speed': random.uniform(1.0, 2.5)
                })
            
            # Handle chronicle scrolling
            if chronicle_viewer.visible:
                chronicle_viewer.handle_event(event)
        
        # Update button hover states
        challenge_button.check_hover(mouse_pos)
        chronicle_button.check_hover(mouse_pos)
        add_wanderer_button.check_hover(mouse_pos)
        close_chronicle_button.check_hover(mouse_pos)
        
        # Update game state
        star_tree.update()
        
        # Update wanderers
        for wanderer in wanderers:
            if wanderer['status'] == "Wanderer" and not wanderer['target_star'] and star_tree.stars:
                wanderer['target_star'] = random.choice(star_tree.stars)
                wanderer['path'] = []
                steps = 20
                for i in range(steps + 1):
                    t = i / steps
                    x = wanderer['x'] + (wanderer['target_star']['x'] - wanderer['x']) * t
                    y = wanderer['y'] + (wanderer['target_star']['y'] - wanderer['y']) * t
                    wanderer['path'].append((x, y))
            
            if wanderer['path'] and wanderer['status'] == "Wanderer":
                # Move to next point in path
                target_x, target_y = wanderer['path'][0]
                dx = target_x - wanderer['x']
                dy = target_y - wanderer['y']
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist < wanderer['speed']:
                    wanderer['path'].pop(0)
                    if not wanderer['path']:
                        wanderer['status'] = "Challenging"
                        # Start challenge
                        star_tree.start_challenge(wanderer, wanderer['target_star'])
                else:
                    wanderer['x'] += dx / dist * wanderer['speed']
                    wanderer['y'] += dy / dist * wanderer['speed']
        
        # Update challenge if active
        if star_tree.current_challenge:
            star_tree.update_challenge()
        
        # Draw everything
        screen.fill(BACKGROUND)
        
        # Draw star tree
        star_tree.draw(screen)
        
        # Draw wanderers
        for wanderer in wanderers:
            pygame.draw.circle(screen, (180, 200, 250), (int(wanderer['x']), int(wanderer['y'])), wanderer['size'])
            name_text = main_font.render(wanderer['name'], True, TEXT_COLOR)
            screen.blit(name_text, (int(wanderer['x']) - name_text.get_width()//2, int(wanderer['y']) + wanderer['size'] + 5))
            
            if wanderer['status'] == "Challenging":
                status_text = main_font.render("Challenging...", True, HIGHLIGHT)
                screen.blit(status_text, (int(wanderer['x']) - status_text.get_width()//2, int(wanderer['y']) + wanderer['size'] + 25))
            elif wanderer['status'] == "God":
                domain_text = main_font.render(f"God of {wanderer['domain']}", True, HIGHLIGHT)
                screen.blit(domain_text, (int(wanderer['x']) - domain_text.get_width()//2, int(wanderer['y']) + wanderer['size'] + 25))
        
        # Draw UI
        if not chronicle_viewer.visible:
            challenge_button.draw(screen)
            chronicle_button.draw(screen)
            add_wanderer_button.draw(screen)
        else:
            close_chronicle_button.draw(screen)
        
        # Draw challenge status
        if star_tree.current_challenge and not chronicle_viewer.visible:
            challenge = star_tree.current_challenge['challenge']
            wanderer = star_tree.active_wanderer
            
            # Challenge info
            challenge_text = header_font.render(f"{wanderer['name']}'s Challenge", True, HIGHLIGHT)
            screen.blit(challenge_text, (SCREEN_WIDTH//2 - challenge_text.get_width()//2, 30))
            
            type_text = main_font.render(f"Type: {challenge['type']} ({challenge['difficulty']})", True, TEXT_COLOR)
            screen.blit(type_text, (SCREEN_WIDTH//2 - type_text.get_width()//2, 80))
            
            desc_text = main_font.render(challenge['description'], True, TEXT_COLOR)
            screen.blit(desc_text, (SCREEN_WIDTH//2 - desc_text.get_width()//2, 110))
            
            # Progress bar
            progress_width = 400
            pygame.draw.rect(screen, (50, 50, 70), (SCREEN_WIDTH//2 - progress_width//2, 150, progress_width, 30), border_radius=15)
            pygame.draw.rect(screen, HIGHLIGHT, (SCREEN_WIDTH//2 - progress_width//2, 150, 
                                                progress_width * star_tree.challenge_progress / 100, 30), border_radius=15)
            pygame.draw.rect(screen, TEXT_COLOR, (SCREEN_WIDTH//2 - progress_width//2, 150, progress_width, 30), 2, border_radius=15)
            
            progress_text = main_font.render(f"{int(star_tree.challenge_progress)}%", True, TEXT_COLOR)
            screen.blit(progress_text, (SCREEN_WIDTH//2 - progress_text.get_width()//2, 155))
            
            # Traits
            traits_text = main_font.render(f"Courage: {wanderer['traits']['courage']*100:.1f}%  |  Wisdom: {wanderer['traits']['wisdom']*100:.1f}%  |  Insight: {wanderer['traits']['insight']*100:.1f}%", 
                                          True, TEXT_COLOR)
            screen.blit(traits_text, (SCREEN_WIDTH//2 - traits_text.get_width()//2, 190))
        
        # Draw chronicle viewer
        chronicle_viewer.draw(screen)
        
        # Draw stats
        wanderer_count = sum(1 for w in wanderers if w['status'] == "Wanderer")
        challenger_count = sum(1 for w in wanderers if w['status'] == "Challenging")
        god_count = sum(1 for w in wanderers if w['status'] == "God")
        
        stats_text = main_font.render(f"Wanderers: {wanderer_count} | Challengers: {challenger_count} | Gods: {god_count}", True, TEXT_COLOR)
        screen.blit(stats_text, (50, SCREEN_HEIGHT - 40))
        
        # Draw cycle counter
        cycle = pygame.time.get_ticks() // 1000
        cycle_text = main_font.render(f"Cosmic Cycle: {cycle}", True, TEXT_COLOR)
        screen.blit(cycle_text, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 40))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()