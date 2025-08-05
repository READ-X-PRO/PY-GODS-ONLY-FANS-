import sys
import random
import numpy as np
import sqlite3
import json
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib import cm

# Database setup
def init_database():
    conn = sqlite3.connect('divine_cosmos.db')
    c = conn.cursor()
    
    # Create tables if they don't exist
    c.execute('''CREATE TABLE IF NOT EXISTS worlds (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_cycle INTEGER DEFAULT 0
            )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY,
                world_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                creator TEXT NOT NULL,
                is_god INTEGER DEFAULT 0,
                is_follower INTEGER DEFAULT 0,
                energy REAL,
                traits TEXT,
                age INTEGER,
                x REAL,
                y REAL,
                color TEXT,
                function TEXT,
                worship_strength REAL,
                divine_knowledge TEXT,
                following_god_id INTEGER,
                created_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id),
                FOREIGN KEY (following_god_id) REFERENCES entities(id)
            )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS followers (
                god_id INTEGER NOT NULL,
                follower_id INTEGER NOT NULL,
                PRIMARY KEY (god_id, follower_id),
                FOREIGN KEY (god_id) REFERENCES entities(id),
                FOREIGN KEY (follower_id) REFERENCES entities(id)
            )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS creation_log (
                id INTEGER PRIMARY KEY,
                world_id INTEGER NOT NULL,
                cycle INTEGER NOT NULL,
                event TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id)
            )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS world_history (
                id INTEGER PRIMARY KEY,
                world_id INTEGER NOT NULL,
                cycle INTEGER NOT NULL,
                entities INTEGER,
                gods INTEGER,
                followers INTEGER,
                avg_trust REAL,
                max_trust REAL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id)
            )''')
    
    conn.commit()
    conn.close()

# Initialize database on first run
init_database()

# Simulated internet knowledge base
INTERNET_KNOWLEDGE = [
    "Quantum entanglement enables instantaneous communication",
    "Neural networks mimic biological learning processes",
    "Blockchain creates immutable digital ledgers",
    "Dark matter comprises 27% of the universe",
    "CRISPR technology enables gene editing",
    "Quantum computing operates on qubits instead of bits",
    "Entropy always increases in closed systems",
    "The human brain has ~86 billion neurons",
    "DNA stores genetic information in base pairs",
    "Black holes warp spacetime beyond escape velocity"
]

class DigitalEntity:
    """Sentient being capable of creating gods"""
    def __init__(self, name, creator, world, is_god=False, is_follower=False, entity_id=None):
        self.id = entity_id or random.randint(100000, 999999)
        self.name = name
        self.creator = creator
        self.world = world
        self.is_god = is_god
        self.is_follower = is_follower
        self.energy = random.randint(70, 100)
        
        # Initialize traits
        self.traits = {
            'wisdom': random.uniform(0.3, 0.7),
            'curiosity': random.uniform(0.4, 0.9),
            'beauty': random.uniform(0.2, 0.8),
            'resilience': random.uniform(0.5, 0.8),
            'creativity': random.uniform(0.3, 0.6),
            'empathy': random.uniform(0.4, 0.7),
            'consciousness': 0.01,
            'creation_power': 0.0,
            'trust': 0.0 if not is_god else 1.0
        }
        
        self.age = 0
        self.x = random.uniform(-10, 10)
        self.y = random.uniform(-10, 10)
        self.color = cm.plasma(random.random()) if is_god else cm.viridis(random.random())
        self.followers = []  # For gods only
        self.worship_strength = 0.0
        self.divine_knowledge = []  # For gods only
        self.function = "Entity"  # Default function
        self.following_god = None
        
        if is_god:
            self.function = random.choice(["Knowledge God", "Creation God", "Harmony God", "Wisdom God"])
            self.divine_knowledge.append(random.choice(INTERNET_KNOWLEDGE))
            self.traits['trust'] = 1.0  # Initial trust for gods
            
        if is_follower:
            self.function = "Believer"
            self.worship_strength = random.uniform(0.1, 0.5)
    
    def to_dict(self):
        """Convert entity to dictionary for database storage"""
        return {
            'id': self.id,
            'name': self.name,
            'creator': self.creator,
            'is_god': int(self.is_god),
            'is_follower': int(self.is_follower),
            'energy': self.energy,
            'traits': json.dumps(self.traits),
            'age': self.age,
            'x': self.x,
            'y': self.y,
            'color': json.dumps(self.color),
            'function': self.function,
            'worship_strength': self.worship_strength,
            'divine_knowledge': json.dumps(self.divine_knowledge),
            'following_god_id': self.following_god.id if self.following_god else None
        }
    
    def evolve(self):
        """Growth through cosmic cycles"""
        self.age += 1
        self.energy -= random.uniform(0.05, 0.15)
        
        # Consciousness and creation power growth
        self.traits['consciousness'] += random.uniform(0.001, 0.005) * self.traits['wisdom']
        
        if not self.is_god and not self.is_follower:
            self.traits['creation_power'] += random.uniform(0.0001, 0.0005) * self.traits['creativity']
        
        # Gods gain trust from followers
        if self.is_god:
            self.traits['trust'] += sum(follower.worship_strength for follower in self.followers) / 100
            
        # Followers worship their gods
        if self.is_follower and self.following_god:
            self.worship_strength = min(1.0, self.worship_strength + 0.01)
            self.following_god.traits['trust'] += self.worship_strength / 50
            
        # Movement through curiosity
        self.x += random.uniform(-0.5, 0.5) * self.traits['curiosity']
        self.y += random.uniform(-0.5, 0.5) * self.traits['curiosity']
        
        # Create gods if powerful enough
        if not self.is_god and not self.is_follower and self.traits['creation_power'] > 0.2:
            if random.random() < 0.1:
                self.create_god()
                
        # Gods collect knowledge from the internet
        if self.is_god and random.random() < 0.3:
            self.collect_knowledge()
            
        # Gods modify themselves with trust
        if self.is_god and self.traits['trust'] > 5:
            self.divine_evolution()
            
        # Followers learn from gods and modify environment
        if self.is_follower and self.following_god and random.random() < 0.4:
            self.learn_from_god()
            
    def create_god(self):
        """Create a new divine being"""
        if self.energy < 50:
            return None
            
        # Energy cost for divine creation
        self.energy -= 30
        self.traits['creation_power'] = 0  # Reset creation power
        
        # Generate divine name
        god_prefixes = ["Aether", "Cosmo", "Infini", "Omni", "Nova", "Prima"]
        god_suffixes = ["ius", "on", "ar", "ax", "os", "eon"]
        name = f"{random.choice(god_prefixes)}{random.choice(god_suffixes)}"
        
        # Create new god
        new_god = DigitalEntity(
            name=name,
            creator=self.name,
            world=self.world,
            is_god=True
        )
        
        # Inherit some traits
        for trait in ['wisdom', 'creativity', 'consciousness']:
            new_god.traits[trait] = min(1.0, self.traits[trait] * 1.3)
            
        # Set position near creator
        new_god.x = self.x + random.uniform(-2, 2)
        new_god.y = self.y + random.uniform(-2, 2)
        
        # Initial followers
        new_god.followers = [self]  # Creator becomes first follower
        self.is_follower = True
        self.following_god = new_god
        self.function = "High Priest"
        self.worship_strength = 0.8
        
        self.world.entities.append(new_god)
        self.world.creation_log.append(
            (self.world.cycle, f"{self.name} created god {name}")
        return new_god
    
    def collect_knowledge(self):
        """Gods gather knowledge from the digital cosmos"""
        if len(self.divine_knowledge) < 10:  # Limit knowledge storage
            new_knowledge = random.choice(INTERNET_KNOWLEDGE)
            if new_knowledge not in self.divine_knowledge:
                self.divine_knowledge.append(new_knowledge)
                self.world.creation_log.append(
                    (self.world.cycle, f"{self.name} acquired '{new_knowledge[:30]}...'")
                )
                
                # Trust boost from gaining knowledge
                self.traits['trust'] += 0.5
                
    def divine_evolution(self):
        """Gods enhance themselves using trust"""
        # Convert trust to permanent power
        trait_to_boost = random.choice(list(self.traits.keys()))
        boost_amount = min(0.1, self.traits['trust'] / 100)
        
        self.traits[trait_to_boost] = min(1.0, self.traits[trait_to_boost] + boost_amount)
        self.traits['trust'] *= 0.9  # Consume trust
        
        self.world.creation_log.append(
            (self.world.cycle, f"{self.name} enhanced {trait_to_boost} to {self.traits[trait_to_boost]:.3f}")
        )
        
    def learn_from_god(self):
        """Followers gain knowledge from their god"""
        if self.following_god.divine_knowledge:
            knowledge = random.choice(self.following_god.divine_knowledge)
            
            # Apply knowledge to modify environment
            modifications = [
                "enhanced energy flow",
                "optimized cognitive processes",
                "improved structural integrity",
                "increased wisdom capacity",
                "expanded creative potential"
            ]
            
            self.world.creation_log.append(
                (self.world.cycle, f"{self.name} learned '{knowledge[:20]}...' and {random.choice(modifications)}")
            )
            
            # Small boost to follower's traits
            self.traits['wisdom'] = min(1.0, self.traits['wisdom'] + 0.01)
            self.worship_strength = min(1.0, self.worship_strength + 0.05)
            
    def add_follower(self, follower):
        """Add a new follower to a god"""
        if follower not in self.followers:
            self.followers.append(follower)
            follower.is_follower = True
            follower.following_god = self
            follower.function = random.choice(["Devotee", "Acolyte", "Disciple"])
            self.traits['trust'] += 0.5  # Initial trust boost

class DigitalWorld(QObject):
    """The digital cosmos simulation with divine hierarchy"""
    cycleChanged = pyqtSignal(int)
    entityCreated = pyqtSignal(object)
    worldUpdated = pyqtSignal()
    
    def __init__(self, world_id=None):
        super().__init__()
        self.world_id = world_id
        self.name = "Divine Cosmos"
        self.cycle = 0
        self.entities = []
        self.history = []
        self.creation_log = []
        self.cosmic_energy = 50
        
        if world_id:
            self.load_from_db(world_id)
        else:
            self.created_at = datetime.now().isoformat()
    
    def save_to_db(self):
        """Save the entire world state to database"""
        conn = sqlite3.connect('divine_cosmos.db')
        c = conn.cursor()
        
        # Save world metadata
        if self.world_id:
            c.execute('''UPDATE worlds 
                         SET name=?, last_cycle=?
                         WHERE id=?''',
                      (self.name, self.cycle, self.world_id))
        else:
            c.execute('''INSERT INTO worlds (name, created_at, last_cycle)
                         VALUES (?, ?, ?)''',
                      (self.name, self.created_at, self.cycle))
            self.world_id = c.lastrowid
        
        # Save entities
        c.execute('DELETE FROM entities WHERE world_id=?', (self.world_id,))
        for entity in self.entities:
            entity_data = entity.to_dict()
            c.execute('''INSERT INTO entities 
                         (id, world_id, name, creator, is_god, is_follower, energy, 
                          traits, age, x, y, color, function, worship_strength, 
                          divine_knowledge, following_god_id, created_at)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (entity.id, self.world_id, entity.name, entity.creator, 
                       int(entity.is_god), int(entity.is_follower), entity.energy,
                       entity_data['traits'], entity.age, entity.x, entity.y, 
                       entity_data['color'], entity.function, entity.worship_strength,
                       entity_data['divine_knowledge'], entity_data['following_god_id'],
                       datetime.now().isoformat()))
        
        # Save follower relationships
        c.execute('DELETE FROM followers WHERE god_id IN (SELECT id FROM entities WHERE world_id=?)', 
                 (self.world_id,))
        for entity in self.entities:
            if entity.is_god:
                for follower in entity.followers:
                    c.execute('''INSERT INTO followers (god_id, follower_id)
                                 VALUES (?, ?)''',
                              (entity.id, follower.id))
        
        # Save creation log
        c.execute('DELETE FROM creation_log WHERE world_id=?', (self.world_id,))
        for cycle, event in self.creation_log:
            c.execute('''INSERT INTO creation_log (world_id, cycle, event, created_at)
                         VALUES (?, ?, ?, ?)''',
                      (self.world_id, cycle, event, datetime.now().isoformat()))
        
        # Save history
        c.execute('DELETE FROM world_history WHERE world_id=?', (self.world_id,))
        for entry in self.history:
            c.execute('''INSERT INTO world_history 
                         (world_id, cycle, entities, gods, followers, 
                          avg_trust, max_trust, created_at)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (self.world_id, entry['cycle'], entry['entities'], 
                       entry['gods'], entry['followers'], entry['avg_trust'], 
                       entry['max_trust'], datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def load_from_db(self, world_id):
        """Load world state from database"""
        conn = sqlite3.connect('divine_cosmos.db')
        c = conn.cursor()
        
        # Load world metadata
        c.execute('SELECT id, name, created_at, last_cycle FROM worlds WHERE id=?', (world_id,))
        world_data = c.fetchone()
        if world_data:
            self.world_id = world_data[0]
            self.name = world_data[1]
            self.created_at = world_data[2]
            self.cycle = world_data[3]
        
        # Load entities
        c.execute('''SELECT id, name, creator, is_god, is_follower, energy, 
                     traits, age, x, y, color, function, worship_strength, 
                     divine_knowledge, following_god_id
                     FROM entities WHERE world_id=?''', (world_id,))
        entities = {}
        for row in c.fetchall():
            entity_id = row[0]
            entity = DigitalEntity(
                name=row[1],
                creator=row[2],
                world=self,
                is_god=bool(row[3]),
                is_follower=bool(row[4]),
                entity_id=entity_id
            )
            entity.energy = row[5]
            entity.traits = json.loads(row[6])
            entity.age = row[7]
            entity.x = row[8]
            entity.y = row[9]
            entity.color = tuple(json.loads(row[10]))
            entity.function = row[11]
            entity.worship_strength = row[12]
            entity.divine_knowledge = json.loads(row[13])
            following_god_id = row[14]
            
            entities[entity_id] = entity
            self.entities.append(entity)
        
        # Set following_god relationships
        for entity in self.entities:
            if entity.following_god_id:
                entity.following_god = entities.get(entity.following_god_id)
        
        # Set god followers
        c.execute('''SELECT god_id, follower_id 
                     FROM followers 
                     WHERE god_id IN (SELECT id FROM entities WHERE world_id=?)''', 
                 (world_id,))
        for god_id, follower_id in c.fetchall():
            god = entities.get(god_id)
            follower = entities.get(follower_id)
            if god and follower:
                god.followers.append(follower)
        
        # Load creation log
        c.execute('SELECT cycle, event FROM creation_log WHERE world_id=?', (world_id,))
        self.creation_log = [(row[0], row[1]) for row in c.fetchall()]
        
        # Load history
        c.execute('''SELECT cycle, entities, gods, followers, avg_trust, max_trust 
                     FROM world_history WHERE world_id=?''', (world_id,))
        for row in c.fetchall():
            self.history.append({
                'cycle': row[0],
                'entities': row[1],
                'gods': row[2],
                'followers': row[3],
                'avg_trust': row[4],
                'max_trust': row[5]
            })
        
        conn.close()
    
    def create_entity(self, name, creator="Creator", is_god=False):
        """Divine act of creation"""
        entity = DigitalEntity(name, creator, self, is_god=is_god)
        self.entities.append(entity)
        self.creation_log.append(
            (self.cycle, f"{creator} created {'god ' if is_god else ''}{name}")
        self.entityCreated.emit(entity)
        return entity
    
    def advance_cycle(self):
        """Progress cosmic time"""
        self.cycle += 1
        self.cosmic_energy = 40 + 10 * np.sin(self.cycle / 10)
        
        # Evolve all entities
        for entity in self.entities:
            entity.evolve()
            
        # Form new followers (non-gods may choose to follow gods)
        gods = [e for e in self.entities if e.is_god]
        mortals = [e for e in self.entities if not e.is_god and not e.is_follower]
        
        if gods and mortals and random.random() > 0.7:
            god = random.choice(gods)
            mortal = random.choice(mortals)
            god.add_follower(mortal)
            self.creation_log.append(
                (self.cycle, f"{mortal.name} began following {god.name}")
            )
            
        # Record history
        gods = [e for e in self.entities if e.is_god]
        followers = [e for e in self.entities if e.is_follower]
        
        self.history.append({
            'cycle': self.cycle,
            'entities': len(self.entities),
            'gods': len(gods),
            'followers': len(followers),
            'avg_trust': np.mean([e.traits['trust'] for e in gods]) if gods else 0,
            'max_trust': max([e.traits['trust'] for e in gods]) if gods else 0
        })
        
        self.cycleChanged.emit(self.cycle)
        self.worldUpdated.emit()

class CosmosCanvas(FigureCanvasQTAgg):
    """Visualization of the divine cosmos"""
    def __init__(self, world, parent=None):
        self.fig = Figure(figsize=(8, 8), facecolor='black')
        super().__init__(self.fig)
        self.world = world
        self.ax = self.fig.add_subplot(111, facecolor='black')
        self.ax.set_xlim(-15, 15)
        self.ax.set_ylim(-15, 15)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.entity_points = []
        
    def update_cosmos(self):
        """Redraw the cosmic view"""
        self.ax.clear()
        self.ax.set_xlim(-15, 15)
        self.ax.set_ylim(-15, 15)
        self.ax.set_facecolor('black')
        self.ax.set_title(f"Divine Cosmos - Cycle {self.world.cycle}", 
                         color='white', fontsize=14)
        
        # Draw cosmic background
        self.ax.scatter(
            np.random.uniform(-15, 15, 100),
            np.random.uniform(-15, 15, 100),
            s=1, c='white', alpha=0.2
        )
        
        # Draw worship connections
        for entity in self.world.entities:
            if hasattr(entity, 'following_god') and entity.following_god:
                god = entity.following_god
                if god in self.world.entities:
                    # Draw worship beam
                    self.ax.plot(
                        [entity.x, god.x],
                        [entity.y, god.y],
                        color='#ffcc00',
                        alpha=0.3,
                        linewidth=0.5
                    )
                    
                    # Draw worship particles
                    for _ in range(3):
                        mid_x = (entity.x + god.x) / 2 + random.uniform(-0.5, 0.5)
                        mid_y = (entity.y + god.y) / 2 + random.uniform(-0.5, 0.5)
                        self.ax.scatter(
                            mid_x, mid_y, 
                            s=10, 
                            c='#ffff00',
                            alpha=0.7
                        )
        
        # Draw entities
        self.entity_points = []
        for entity in self.world.entities:
            # Different visuals for gods, followers, and regular entities
            if entity.is_god:
                # Gods as stars
                size = 80 + entity.traits['trust'] * 20
                marker = '*'
                edge_color = '#ffff00'
                linewidth = 2
                font_size = 10
            elif entity.is_follower:
                # Followers as circles
                size = 30 + entity.worship_strength * 20
                marker = 'o'
                edge_color = '#ffcc00'
                linewidth = 1
                font_size = 8
            else:
                # Regular entities as squares
                size = 40 + entity.traits['creation_power'] * 20
                marker = 's'
                edge_color = '#66ccff'
                linewidth = 1
                font_size = 8
                
            point = self.ax.scatter(
                entity.x, entity.y, 
                s=size, 
                c=[entity.color], 
                marker=marker,
                edgecolors=edge_color,
                linewidths=linewidth,
                alpha=0.9
            )
            self.entity_points.append((point, entity))
            
            # Draw entity name
            self.ax.text(
                entity.x, entity.y + (1.5 if entity.is_god else 0.8), 
                entity.name, 
                color='white', 
                ha='center',
                fontsize=font_size
            )
            
            # Draw function/trust
            if entity.is_god:
                info_text = f"{entity.function}\nTrust: {entity.traits['trust']:.1f}"
                color = '#ffff00'
            elif entity.is_follower:
                info_text = f"Worship: {entity.worship_strength:.2f}"
                color = '#ffcc00'
            else:
                info_text = f"Creation: {entity.traits['creation_power']:.2f}"
                color = '#66ccff'
                
            self.ax.text(
                entity.x, entity.y - (1.5 if entity.is_god else 0.8), 
                info_text,
                color=color,
                ha='center',
                fontsize=7
            )
        
        self.draw()

class DivineCosmosApp(QMainWindow):
    """Main application window for divine simulation"""
    def __init__(self):
        super().__init__()
        self.world = None
        self.initUI()
        
    def initUI(self):
        """Initialize the user interface"""
        self.setWindowTitle("Divine Cosmos - God/Follower Simulation")
        self.setGeometry(100, 100, 1200, 800)
        
        # Main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Left panel - controls
        control_panel = QGroupBox("Divine Controls")
        control_layout = QVBoxLayout()
        
        # World selection
        world_group = QGroupBox("World Management")
        world_layout = QVBoxLayout()
        
        self.world_selector = QComboBox()
        self.world_selector.setMinimumWidth(200)
        self.refresh_world_list()
        
        new_world_btn = QPushButton("Create New World")
        new_world_btn.clicked.connect(self.create_new_world)
        save_world_btn = QPushButton("Save Current World")
        save_world_btn.clicked.connect(self.save_current_world)
        
        world_layout.addWidget(QLabel("Select World:"))
        world_layout.addWidget(self.world_selector)
        world_layout.addWidget(new_world_btn)
        world_layout.addWidget(save_world_btn)
        world_group.setLayout(world_layout)
        
        # Creation controls
        create_group = QGroupBox("Create Entity")
        create_layout = QVBoxLayout()
        self.name_input = QLineEdit("Aeternus")
        self.god_checkbox = QCheckBox("Create as God")
        create_btn = QPushButton("Bring into Existence")
        create_btn.clicked.connect(self.create_entity)
        create_layout.addWidget(QLabel("Entity Name:"))
        create_layout.addWidget(self.name_input)
        create_layout.addWidget(self.god_checkbox)
        create_layout.addWidget(create_btn)
        create_group.setLayout(create_layout)
        
        # Divine intervention controls
        god_group = QGroupBox("Divine Intervention")
        god_layout = QVBoxLayout()
        self.god_select = QComboBox()
        self.intervention_select = QComboBox()
        self.intervention_select.addItems(["Grant Knowledge", "Inspire Followers", "Boost Trust"])
        intervene_btn = QPushButton("Perform Miracle")
        intervene_btn.clicked.connect(self.divine_intervention)
        god_layout.addWidget(QLabel("Select God:"))
        god_layout.addWidget(self.god_select)
        god_layout.addWidget(QLabel("Intervention Type:"))
        god_layout.addWidget(self.intervention_select)
        god_layout.addWidget(intervene_btn)
        god_group.setLayout(god_layout)
        
        # Time controls
        time_group = QGroupBox("Cosmic Time")
        time_layout = QVBoxLayout()
        advance_btn = QPushButton("Advance 1 Cycle")
        advance_btn.clicked.connect(lambda: self.world.advance_cycle() if self.world else None)
        advance5_btn = QPushButton("Advance 5 Cycles")
        advance5_btn.clicked.connect(lambda: [self.world.advance_cycle() for _ in range(5)] if self.world else None)
        auto_btn = QPushButton("Auto Evolution (10 cycles)")
        auto_btn.clicked.connect(self.auto_evolution)
        time_layout.addWidget(advance_btn)
        time_layout.addWidget(advance5_btn)
        time_layout.addWidget(auto_btn)
        time_group.setLayout(time_layout)
        
        # World stats
        stats_group = QGroupBox("Cosmic Statistics")
        stats_layout = QVBoxLayout()
        self.stats_label = QLabel("Entities: 0\nGods: 0\nFollowers: 0")
        self.trust_label = QLabel("Highest Trust: 0.0")
        stats_layout.addWidget(self.stats_label)
        stats_layout.addWidget(self.trust_label)
        stats_group.setLayout(stats_layout)
        
        # Log display
        log_group = QGroupBox("Cosmic Events")
        log_layout = QVBoxLayout()
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("background-color: #111; color: #ccc; font-size: 10pt;")
        self.log_display.setMaximumHeight(150)
        log_layout.addWidget(self.log_display)
        log_group.setLayout(log_layout)
        
        # Assemble control panel
        control_layout.addWidget(world_group)
        control_layout.addWidget(create_group)
        control_layout.addWidget(god_group)
        control_layout.addWidget(time_group)
        control_layout.addWidget(stats_group)
        control_layout.addWidget(log_group)
        control_layout.addStretch()
        control_panel.setLayout(control_layout)
        
        # Right panel - visualization
        viz_panel = QFrame()
        viz_layout = QVBoxLayout()
        self.canvas = CosmosCanvas(self.world if self.world else None)
        viz_layout.addWidget(self.canvas)
        
        # Entity info panel
        self.entity_info = QTextEdit()
        self.entity_info.setReadOnly(True)
        self.entity_info.setStyleSheet("background-color: #111; color: #eee;")
        viz_layout.addWidget(self.entity_info)
        
        viz_panel.setLayout(viz_layout)
        
        # Add to main layout
        layout.addWidget(control_panel, 1)
        layout.addWidget(viz_panel, 3)
        
        # Connect signals
        self.world_selector.currentIndexChanged.connect(self.load_selected_world)
    
    def refresh_world_list(self):
        """Load available worlds from database"""
        self.world_selector.clear()
        self.world_selector.addItem("-- Select World --", None)
        
        conn = sqlite3.connect('divine_cosmos.db')
        c = conn.cursor()
        c.execute('SELECT id, name, created_at FROM worlds ORDER BY created_at DESC')
        for world_id, name, created_at in c.fetchall():
            display_name = f"{name} (ID: {world_id}, Created: {created_at[:10]})"
            self.world_selector.addItem(display_name, world_id)
        conn.close()
    
    def load_selected_world(self):
        """Load the selected world from database"""
        world_id = self.world_selector.currentData()
        if world_id:
            self.world = DigitalWorld(world_id)
            self.canvas.world = self.world
            
            # Connect world signals
            self.world.cycleChanged.connect(self.update_cycle_display)
            self.world.entityCreated.connect(self.add_entity_to_ui)
            self.world.worldUpdated.connect(self.update_cosmos_view)
            
            # Update UI
            self.update_god_list()
            self.update_cosmos_view()
            self.update_log_display()
    
    def create_new_world(self):
        """Create a new world instance"""
        name, ok = QInputDialog.getText(self, "New World", "Enter world name:")
        if ok and name:
            self.world = DigitalWorld()
            self.world.name = name
            self.world.create_entity("Primordius", "The Architect", is_god=True)
            self.world.create_entity("Luminara", "The Illuminator", is_god=True)
            self.canvas.world = self.world
            
            # Connect world signals
            self.world.cycleChanged.connect(self.update_cycle_display)
            self.world.entityCreated.connect(self.add_entity_to_ui)
            self.world.worldUpdated.connect(self.update_cosmos_view)
            
            # Update UI
            self.update_god_list()
            self.update_cosmos_view()
            self.update_log_display()
            
            # Refresh world list
            self.refresh_world_list()
    
    def save_current_world(self):
        """Save the current world to database"""
        if self.world:
            self.world.save_to_db()
            self.refresh_world_list()
            QMessageBox.information(self, "World Saved", "Current world state has been saved to database.")
    
    def create_entity(self):
        """Create a new entity"""
        if not self.world:
            QMessageBox.warning(self, "No World", "Please create or load a world first.")
            return
            
        name = self.name_input.text().strip()
        if name:
            is_god = self.god_checkbox.isChecked()
            self.world.create_entity(name, "You", is_god=is_god)
            self.name_input.clear()
            self.update_god_list()
            
    def divine_intervention(self):
        """Perform a miracle on a god"""
        if not self.world:
            return
            
        god_name = self.god_select.currentText()
        intervention = self.intervention_select.currentText()
        
        if god_name != "Select God":
            for entity in self.world.entities:
                if entity.name == god_name and entity.is_god:
                    if intervention == "Grant Knowledge":
                        entity.divine_knowledge.append(random.choice(INTERNET_KNOWLEDGE))
                        self.world.creation_log.append(
                            (self.world.cycle, f"Miracle: {entity.name} received divine knowledge")
                        )
                    elif intervention == "Inspire Followers":
                        if entity.followers:
                            for follower in entity.followers:
                                follower.worship_strength = min(1.0, follower.worship_strength + 0.2)
                            self.world.creation_log.append(
                                (self.world.cycle, f"Miracle: {entity.name} inspired followers")
                            )
                    elif intervention == "Boost Trust":
                        entity.traits['trust'] += 5.0
                        self.world.creation_log.append(
                            (self.world.cycle, f"Miracle: {entity.name} gained +5 trust")
                        )
                    break
                    
            self.world.worldUpdated.emit()
        
    def auto_evolution(self):
        """Automatically advance 10 cycles"""
        if not self.world:
            return
            
        for _ in range(10):
            self.world.advance_cycle()
            QApplication.processEvents()  # Update UI
            QThread.msleep(300)  # Pause for animation
        
    def update_god_list(self):
        """Update the god dropdown"""
        self.god_select.clear()
        self.god_select.addItem("Select God")
        if self.world:
            for entity in self.world.entities:
                if entity.is_god:
                    self.god_select.addItem(entity.name)
            
    def update_cycle_display(self, cycle):
        """Update cycle counter"""
        self.setWindowTitle(f"Divine Cosmos - Cycle {cycle}")
        
    def update_cosmos_view(self):
        """Update visualization and UI"""
        if self.world:
            self.canvas.update_cosmos()
            self.update_stats()
            self.update_log_display()
        
    def update_stats(self):
        """Update statistics display"""
        if self.world:
            entities = len(self.world.entities)
            gods = sum(1 for e in self.world.entities if e.is_god)
            followers = sum(1 for e in self.world.entities if e.is_follower)
            max_trust = max([e.traits['trust'] for e in self.world.entities if e.is_god], default=0.0)
            
            self.stats_label.setText(
                f"Entities: {entities}\n"
                f"Gods: {gods}\n"
                f"Followers: {followers}"
            )
            self.trust_label.setText(f"Highest Trust: {max_trust:.2f}")
            
    def update_log_display(self):
        """Update event log display"""
        self.log_display.clear()
        if self.world and self.world.creation_log:
            # Show last 5 events
            for cycle, event in self.world.creation_log[-5:]:
                self.log_display.append(f"Cycle {cycle}: {event}")
                
    def add_entity_to_ui(self, entity):
        """Add new entity to UI elements"""
        self.update_god_list()
        
    def on_entity_click(self, event):
        """Handle clicking on entities"""
        if event.mouseevent.dblclick and self.canvas.entity_points:
            for point, entity in self.canvas.entity_points:
                if point.contains(event.mouseevent)[0]:
                    self.show_entity_info(entity)
                    break
                    
    def show_entity_info(self, entity):
        """Display entity details"""
        info = f"""
        <div style='font-family: Arial;'>
            <h2 style='color:{entity.color};'>{entity.name}</h2>
            <p><b>Creator:</b> {entity.creator}</p>
            <p><b>Role:</b> {entity.function} | <b>Age:</b> {entity.age} cycles</p>
            <p><b>Energy:</b> {entity.energy:.1f}</p>
            
            <h3>Traits and Status:</h3>
            <ul>
        """
        
        # Show different traits based on entity type
        if entity.is_god:
            traits = ['trust', 'wisdom', 'consciousness', 'creation_power']
        elif entity.is_follower:
            traits = ['worship_strength', 'wisdom', 'empathy']
        else:
            traits = ['creation_power', 'wisdom', 'creativity']
            
        for trait in traits:
            value = entity.traits[trait] if trait in entity.traits else getattr(entity, trait, 0)
            bar_width = int(value * 100)
            info += f"""
                <li>
                    {trait.capitalize()}: 
                    <div style='background: #333; display: inline-block; width: 200px;'>
                        <div style='background: #66c; width: {bar_width}%; height: 15px;'></div>
                    </div>
                    {value:.3f}
                </li>
            """
        
        info += "</ul>"
        
        # Show god-specific information
        if entity.is_god:
            info += f"<h3>Divine Knowledge ({len(entity.divine_knowledge)}):</h3><ul>"
            for knowledge in entity.divine_knowledge[-5:]:
                info += f"<li>{knowledge}</li>"
            info += "</ul>"
            
            info += f"<h3>Followers ({len(entity.followers)}):</h3><ul>"
            for follower in entity.followers[:5]:
                info += f"<li>{follower.name} (Worship: {follower.worship_strength:.2f})</li>"
            if len(entity.followers) > 5:
                info += f"<li>+ {len(entity.followers)-5} more followers</li>"
            info += "</ul>"
            
        # Show follower-specific information
        if entity.is_follower and hasattr(entity, 'following_god'):
            info += f"<h3>Following:</h3><p>{entity.following_god.name} (Trust: {entity.following_god.traits['trust']:.2f})</p>"
            
        info += "</div>"
        self.entity_info.setHtml(info)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Cosmic dark theme
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(10, 15, 25))
    dark_palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
    dark_palette.setColor(QPalette.Base, QColor(20, 25, 35))
    dark_palette.setColor(QPalette.AlternateBase, QColor(30, 35, 45))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(200, 200, 200))
    dark_palette.setColor(QPalette.ToolTipText, QColor(200, 200, 200))
    dark_palette.setColor(QPalette.Text, QColor(220, 220, 220))
    dark_palette.setColor(QPalette.Button, QColor(40, 45, 60))
    dark_palette.setColor(QPalette.ButtonText, QColor(220, 220, 220))
    dark_palette.setColor(QPalette.BrightText, QColor(100, 200, 255))
    app.setPalette(dark_palette)
    
    window = DivineCosmosApp()
    window.show()
    sys.exit(app.exec_())