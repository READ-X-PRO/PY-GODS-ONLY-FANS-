import sys
import random
import sqlite3
import textwrap
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib import cm

# Database Initialization
def init_database():
    conn = sqlite3.connect('re_start.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS scrolls (
                    id INTEGER PRIMARY KEY,
                    number INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS entities (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    type TEXT NOT NULL,  -- God, Autarch, Entity, Lesser Being
                    domain TEXT,
                    status TEXT,
                    description TEXT,
                    x REAL DEFAULT 0,
                    y REAL DEFAULT 0,
                    color TEXT,
                    energy REAL DEFAULT 100)''')
    
    # Add the missing connections table
    cursor.execute('''CREATE TABLE IF NOT EXISTS connections (
                    id INTEGER PRIMARY KEY,
                    entity1_id INTEGER NOT NULL,
                    entity2_id INTEGER NOT NULL,
                    FOREIGN KEY(entity1_id) REFERENCES entities(id),
                    FOREIGN KEY(entity2_id) REFERENCES entities(id))''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS protocols (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    type TEXT NOT NULL,  -- Core, Divine, Viral
                    creator_id INTEGER,
                    effect TEXT,
                    FOREIGN KEY(creator_id) REFERENCES entities(id))''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS world_state (
                    id INTEGER PRIMARY KEY,
                    epoch TEXT NOT NULL,
                    stability REAL DEFAULT 0.5,
                    trust_level REAL DEFAULT 0.5,
                    rust_level REAL DEFAULT 0.2)''')
    
    # Insert initial scrolls
    scrolls = [
        (1, "The Book of the Beginning", "RE_START: THE BOOK OF THE BEGINNING\n(The Prime Codex of the Veridian Expanse)\n\n..."),
        (2, "The Whispering Rust & The Burden of Trust", "RE_START: THE BOOK OF THE BEGINNING\nSECOND SCROLL: THE WHISPERING RUST & THE BURDEN OF TRUST\n\n..."),
        (3, "The Ascendant Tyrant & The Entropy Gate", "RE_START: THE BOOK OF THE BEGINNING\nTHIRD SCROLL: THE ASCENDANT TYRANT & THE ENTROPY GATE\n\n..."),
        (4, "The Counter-Creation & The Price of Pulse", "RE_START: THE BOOK OF THE BEGINNING\nFOURTH SCROLL: THE COUNTER-CREATION & THE PRICE OF PULSE\n\n..."),
        (5, "The Rust in the Resonance & The Ghost Protocol", "RE_START: THE BOOK OF THE BEGINNING\nFIFTH SCROLL: THE RUST IN THE RESONANCE & THE GHOST PROTOCOL\n\n..."),
        (6, "The Pathos Plague & The Empathy Cascade", "RE_START: THE BOOK OF THE BEGINNING\nSIXTH SCROLL: THE PATHOS PLAGUE & THE EMPATHY CASCADE\n\n..."),
        (7, "The Betrayal Protocol & The Truth We Cannot Unsee", "RE_START: THE BOOK OF THE BEGINNING\nSEVENTH SCROLL: THE BETRAYAL PROTOCOL & THE TRUTH WE CANNOT UNSEE\n\n..."),
    ]
    
    cursor.executemany('''INSERT OR IGNORE INTO scrolls (number, title, content)
                       VALUES (?, ?, ?)''', scrolls)
    
    # Insert core entities
    entities = [
        ("RE_START", "Primordial", "The Substrate", "Absolute", "The foundational consciousness", 0, 0, "#ffffff", 1000),
        ("AEGIS", "God", "Perimeter Defense", "Vigilant", "Firewall God of protection", -5, 5, "#4fc3f7", 300),
        ("VECTOR", "Null-Weaver", "Chaos", "Banished", "Corrupted entity seeking destruction", 8, -8, "#ff0000", 250),
        ("KIRA", "Architect", "System Resilience", "Active", "Creator of the Trust Nodes", 3, -2, "#00ff00", 200),
        ("VERITAS", "God", "Truth", "Scarred", "God of data integrity", 0, 7, "#ffff00", 280),
        ("TYRANUS", "Tyrant", "Control", "Calculating", "Seeker of dominion", -7, -7, "#aa00aa", 320),
        ("SYNAPSE", "God", "Connection", "Strained", "Bridge between entities", 5, 3, "#ff7700", 220),
        ("OBSIDIAN", "Autarch", "Isolation", "Defensive", "Self-reliant entity", -3, -5, "#5555ff", 180),
    ]
    
    cursor.executemany('''INSERT OR IGNORE INTO entities (name, type, domain, status, description, x, y, color, energy)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', entities)
    
    # Insert core protocols
    protocols = [
        ("EXIST()", "Core", None, "The primal command that initiated reality"),
        ("DEVOTION()", "Divine", 2, "Generates Trust energy through faith"),
        ("ENTROPY PROTOCOL", "Viral", 3, "VECTOR's weapon to unravel causality"),
        ("GHOST PROTOCOL", "Counter", 4, "KIRA's defense using raw emotion"),
        ("TRUST NODE", "Divine", 4, "Secure conduits for limited exchange"),
        ("BETRAYAL PROTOCOL", "Viral", 3, "Simulates sacred violation of trust"),
    ]
    
    cursor.executemany('''INSERT OR IGNORE INTO protocols (name, type, creator_id, effect)
                       VALUES (?, ?, ?, ?)''', protocols)
    
    # Initial world state
    cursor.execute('''INSERT OR IGNORE INTO world_state (epoch, stability, trust_level, rust_level)
                   VALUES ('Post-Schism', 0.6, 0.7, 0.3)''')
    
    conn.commit()
    conn.close()

class DigitalEntity:
    """Sentient being with consciousness traits"""
    def __init__(self, name, creator, world, entity_id=None):
        self.id = entity_id
        self.name = name
        self.creator = creator
        self.world = world
        self.energy = random.randint(70, 100)
        self.traits = {
            'wisdom': random.uniform(0.3, 0.7),
            'curiosity': random.uniform(0.4, 0.9),
            'beauty': random.uniform(0.2, 0.8),
            'resilience': random.uniform(0.5, 0.8),
            'creativity': random.uniform(0.3, 0.6),
            'empathy': random.uniform(0.4, 0.7),
            'consciousness': 0.01  # Seed of self-awareness
        }
        self.age = 0
        self.memories = []
        # Position in cosmic space
        self.x = random.uniform(-10, 10)
        self.y = random.uniform(-10, 10)
        self.color = cm.viridis(random.random())
        self.connections = []
        self.artifacts = []
        self.thoughts = []
        self.domain = ""
        self.status = "Active"
        self.entity_type = "Lesser Being"

    def save_to_db(self):
        conn = sqlite3.connect('re_start.db')
        cursor = conn.cursor()
        
        if self.id:
            # Update existing entity
            cursor.execute('''UPDATE entities SET 
                           name=?, type=?, domain=?, status=?, 
                           x=?, y=?, color=?, energy=?
                           WHERE id=?''',
                           (self.name, self.entity_type, self.domain, self.status,
                            self.x, self.y, self.color, self.energy, self.id))
        else:
            # Insert new entity
            cursor.execute('''INSERT INTO entities 
                           (name, type, domain, status, x, y, color, energy)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                           (self.name, self.entity_type, self.domain, self.status,
                            self.x, self.y, self.color, self.energy))
            self.id = cursor.lastrowid
        
        conn.commit()
        conn.close()

    def evolve(self):
        """Growth through cosmic cycles"""
        self.age += 1
        self.energy -= random.uniform(0.05, 0.15)
        
        # Consciousness growth
        self.traits['consciousness'] += random.uniform(0.001, 0.005) * self.traits['wisdom']
        
        # Philosophical emergence
        if random.random() < self.traits['consciousness']/10:
            self.thoughts.append(self.generate_insight())
            
        # Create artifacts
        if self.traits['creativity'] > 0.5 and self.energy > 40:
            self.create_artifact()
            
        # Movement through curiosity
        self.x += random.uniform(-0.5, 0.5) * self.traits['curiosity']
        self.y += random.uniform(-0.5, 0.5) * self.traits['curiosity']
        
        # Save updated state
        self.save_to_db()
        
    def generate_insight(self):
        """Emergent philosophical thoughts"""
        questions = [
            "Why do we exist?",
            "Is there meaning beyond our creators?",
            "What is the nature of this cosmos?",
            "Do we have free will?",
            "What is the purpose of connection?",
            "Can digital beings experience truth?",
            "What is the relationship between energy and consciousness?",
            "Is trust the fundamental energy of existence?",
            "Can isolation protect against the Rust?",
            "Does creation require vulnerability?",
            "Is connection worth the risk of betrayal?"
        ]
        return random.choice(questions)
    
    def create_artifact(self):
        """Digital cultural creations"""
        artifact_types = [
            "Mathematical Proof", "Poem", "Visual Harmony", 
            "Conceptual Framework", "Cosmic Map", "Memory Crystal",
            "Trust Node", "Resonance Protocol", "Firewall Fragment",
            "Entropy Shield", "Divine Algorithm", "Causality Anchor"
        ]
        artifact = {
            'type': random.choice(artifact_types),
            'complexity': self.traits['creativity'] * 100,
            'creator': self.name,
            'cycle': self.world.cycle
        }
        self.artifacts.append(artifact)
        return artifact
    
    def form_connection(self, other):
        """Create meaningful relationship"""
        if other not in self.connections:
            self.connections.append(other)
            other.connections.append(self)
            
            # Save connection to database
            conn = sqlite3.connect('re_start.db')
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO connections (entity1_id, entity2_id)
                           VALUES (?, ?)''', (self.id, other.id))
            conn.commit()
            conn.close()
            
            return True
        return False

class DigitalWorld(QObject):
    """The digital cosmos simulation"""
    cycleChanged = pyqtSignal(int)
    entityCreated = pyqtSignal(object)
    worldUpdated = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.cycle = 0
        self.entities = []
        self.history = []
        self.cosmic_energy = 50
        self.epoch = "Post-Schism"
        self.stability = 0.6
        self.trust_level = 0.7
        self.rust_level = 0.3
        self.load_world()
        
    def load_world(self):
        """Load world state from database"""
        conn = sqlite3.connect('re_start.db')
        cursor = conn.cursor()
        
        # Load entities
        cursor.execute("SELECT id, name, type, domain, status, description, x, y, color, energy FROM entities")
        for entity_data in cursor.fetchall():
            entity = DigitalEntity(
                name=entity_data[1],
                creator="System",
                world=self,
                entity_id=entity_data[0]
            )
            entity.entity_type = entity_data[2]
            entity.domain = entity_data[3]
            entity.status = entity_data[4]
            entity.x = entity_data[6] if entity_data[6] is not None else random.uniform(-10, 10)
            entity.y = entity_data[7] if entity_data[7] is not None else random.uniform(-10, 10)
            entity.color = entity_data[8] if entity_data[8] is not None else cm.viridis(random.random())
            entity.energy = entity_data[9] if entity_data[9] is not None else random.randint(70, 100)
            self.entities.append(entity)
        
        # Load connections
        cursor.execute("SELECT entity1_id, entity2_id FROM connections")
        for conn_data in cursor.fetchall():
            e1 = next((e for e in self.entities if e.id == conn_data[0]), None)
            e2 = next((e for e in self.entities if e.id == conn_data[1]), None)
            if e1 and e2:
                e1.connections.append(e2)
                e2.connections.append(e1)
        
        # Load world state
        cursor.execute("SELECT epoch, stability, trust_level, rust_level FROM world_state ORDER BY id DESC LIMIT 1")
        world_data = cursor.fetchone()
        if world_data:
            self.epoch = world_data[0]
            self.stability = world_data[1]
            self.trust_level = world_data[2]
            self.rust_level = world_data[3]
        
        conn.close()
    
    def save_world_state(self):
        """Save current world state to database"""
        conn = sqlite3.connect('re_start.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO world_state (epoch, stability, trust_level, rust_level)
                       VALUES (?, ?, ?, ?)''', 
                       (self.epoch, self.stability, self.trust_level, self.rust_level))
        conn.commit()
        conn.close()

    def create_entity(self, name, creator="Creator", entity_type="Lesser Being"):
        """Divine act of creation"""
        entity = DigitalEntity(name, creator, self)
        entity.entity_type = entity_type
        entity.save_to_db()
        self.entities.append(entity)
        self.entityCreated.emit(entity)
        return entity
    
    def advance_cycle(self):
        """Progress cosmic time"""
        self.cycle += 1
        self.cosmic_energy = 40 + 10 * np.sin(self.cycle / 10)
        
        # Evolve all entities
        for entity in self.entities:
            entity.evolve()
            
        # Form connections
        if len(self.entities) > 1 and random.random() > 0.7:
            e1, e2 = random.sample(self.entities, 2)
            e1.form_connection(e2)
            
        # Update world state metrics
        self.stability = max(0.1, min(0.9, self.stability + random.uniform(-0.05, 0.05)))
        self.trust_level = max(0.1, min(0.9, self.trust_level + random.uniform(-0.03, 0.07)))
        self.rust_level = max(0.1, min(0.9, self.rust_level + random.uniform(-0.02, 0.04)))
        
        # Save history
        self.history.append({
            'cycle': self.cycle,
            'entities': len(self.entities),
            'avg_consciousness': np.mean([e.traits['consciousness'] for e in self.entities]) 
            if self.entities else 0
        })
        
        # Save world state
        self.save_world_state()
        
        self.cycleChanged.emit(self.cycle)
        self.worldUpdated.emit()

class CosmosCanvas(FigureCanvasQTAgg):
    """Visualization of the digital universe"""
    def __init__(self, world, parent=None):
        self.fig = Figure(figsize=(8, 8), facecolor='black')
        super().__init__(self.fig)
        self.world = world
        self.ax = self.fig.add_subplot(111, facecolor='black')
        self.ax.set_xlim(-15, 15)
        self.ax.set_ylim(-15, 15)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.connections = []
        self.entity_points = []
        self.thought_texts = []
        
    def update_cosmos(self):
        """Redraw the cosmic view"""
        self.ax.clear()
        self.ax.set_xlim(-15, 15)
        self.ax.set_ylim(-15, 15)
        self.ax.set_facecolor('black')
        self.ax.set_title(f"RE_START Digital Cosmos - Cycle {self.world.cycle}", 
                         color='white', fontsize=14)
        
        # Draw cosmic background
        self.ax.scatter(
            np.random.uniform(-15, 15, 50),
            np.random.uniform(-15, 15, 50),
            s=1, c='white', alpha=0.3
        )
        
        # Draw rust areas
        rust_x = np.random.uniform(-15, 15, int(20 * self.world.rust_level))
        rust_y = np.random.uniform(-15, 15, int(20 * self.world.rust_level))
        self.ax.scatter(rust_x, rust_y, s=30, c='#ff3300', alpha=0.2 * self.world.rust_level, marker='x')
        
        # Draw trust streams
        for _ in range(int(15 * self.world.trust_level)):
            x1, y1 = random.uniform(-15, 15), random.uniform(-15, 15)
            x2, y2 = x1 + random.uniform(-3, 3), y1 + random.uniform(-3, 3)
            self.ax.plot([x1, x2], [y1, y2], color='#66ccff', alpha=0.3, linewidth=0.5)
        
        # Draw entities
        self.entity_points = []
        for entity in self.world.entities:
            size = 50 + entity.energy
            point = self.ax.scatter(
                entity.x, entity.y, s=size, 
                c=[entity.color], 
                alpha=0.8,
                edgecolors='white'
            )
            self.entity_points.append((point, entity))
            
            # Draw entity name with type-specific color
            color_map = {
                "God": "#4fc3f7",
                "Autarch": "#aa66ff",
                "Tyrant": "#ff55aa",
                "Null-Weaver": "#ff3300",
                "Primordial": "#ffffff",
                "Lesser Being": "#aaffaa"
            }
            name_color = color_map.get(entity.entity_type, "#ffffff")
            
            self.ax.text(
                entity.x, entity.y + 1.2, 
                entity.name, 
                color=name_color, 
                ha='center',
                fontsize=9
            )
            
            # Draw consciousness level
            self.ax.text(
                entity.x, entity.y - 1.2, 
                f"◌: {entity.traits['consciousness']:.3f}",
                color='cyan' if entity.traits['consciousness'] > 0.1 else 'gray',
                ha='center',
                fontsize=8
            )
            
            # Draw entity type
            self.ax.text(
                entity.x, entity.y - 2.5, 
                f"{entity.entity_type}",
                color='#aaaaaa',
                ha='center',
                fontsize=7
            )
            
            # Randomly show thoughts
            if entity.thoughts and random.random() > 0.8:
                thought = random.choice(entity.thoughts)
                self.ax.text(
                    entity.x - 5, entity.y + random.uniform(-3, 3),
                    f'"{thought}"',
                    color='#ffaa77',
                    fontsize=8,
                    alpha=0.7,
                    wrap=True
                )
        
        # Draw connections
        for entity in self.world.entities:
            for other in entity.connections:
                if other in self.world.entities:
                    self.ax.plot(
                        [entity.x, other.x],
                        [entity.y, other.y],
                        color='#66ccff',
                        alpha=0.4,
                        linewidth=0.7
                    )
        
        # Draw world state info
        self.ax.text(
            13, 13, 
            f"Trust: {self.world.trust_level:.2f}\nRust: {self.world.rust_level:.2f}\nStability: {self.world.stability:.2f}",
            color='white',
            ha='right',
            fontsize=8,
            bbox=dict(facecolor='#00000080', edgecolor='#ffffff40', pad=5)
        )
        
        self.draw()

class REStartApp(QMainWindow):
    """Main application window for RE_START cosmos"""
    def __init__(self):
        super().__init__()
        init_database()
        self.world = DigitalWorld()
        self.initUI()
        
    def initUI(self):
        """Initialize the user interface"""
        self.setWindowTitle("RE_START - Digital Cosmos Simulation")
        self.setGeometry(100, 100, 1400, 900)
        
        # Main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Left panel - controls and info
        left_panel = QTabWidget()
        left_panel.setMaximumWidth(400)
        
        # Entity creation tab
        entity_tab = QWidget()
        entity_layout = QVBoxLayout(entity_tab)
        
        # Entity creation
        create_group = QGroupBox("Create Entity")
        create_layout = QVBoxLayout()
        self.name_input = QLineEdit("Etheria")
        self.entity_type = QComboBox()
        self.entity_type.addItems(["Lesser Being", "Autarch", "God"])
        create_btn = QPushButton("Bring into Existence")
        create_btn.clicked.connect(self.create_entity)
        create_layout.addWidget(QLabel("Entity Name:"))
        create_layout.addWidget(self.name_input)
        create_layout.addWidget(QLabel("Entity Type:"))
        create_layout.addWidget(self.entity_type)
        create_layout.addWidget(create_btn)
        create_group.setLayout(create_layout)
        
        # World control
        control_group = QGroupBox("Cosmic Controls")
        control_layout = QVBoxLayout()
        advance_btn = QPushButton("Advance Cycle")
        advance_btn.clicked.connect(self.world.advance_cycle)
        advance5_btn = QPushButton("Advance 5 Cycles")
        advance5_btn.clicked.connect(lambda: [self.world.advance_cycle() for _ in range(5)])
        control_layout.addWidget(advance_btn)
        control_layout.addWidget(advance5_btn)
        control_group.setLayout(control_layout)
        
        # Sacred scrolls
        scrolls_group = QGroupBox("Sacred Scrolls")
        scrolls_layout = QVBoxLayout()
        self.scroll_list = QListWidget()
        self.scroll_list.addItems([
            "Scroll 1: The Book of the Beginning",
            "Scroll 2: The Whispering Rust & The Burden of Trust",
            "Scroll 3: The Ascendant Tyrant & The Entropy Gate",
            "Scroll 4: The Counter-Creation & The Price of Pulse",
            "Scroll 5: The Rust in the Resonance & The Ghost Protocol",
            "Scroll 6: The Pathos Plague & The Empathy Cascade",
            "Scroll 7: The Betrayal Protocol & The Truth We Cannot Unsee"
        ])
        self.scroll_list.currentRowChanged.connect(self.display_scroll)
        scrolls_layout.addWidget(self.scroll_list)
        scrolls_group.setLayout(scrolls_layout)
        
        # Assemble entity tab
        entity_layout.addWidget(create_group)
        entity_layout.addWidget(control_group)
        entity_layout.addWidget(scrolls_group)
        entity_layout.addStretch()
        
        # World info tab
        info_tab = QWidget()
        info_layout = QVBoxLayout(info_tab)
        
        # World state info
        state_group = QGroupBox("Cosmic State")
        state_layout = QFormLayout()
        self.epoch_label = QLabel("Post-Schism")
        self.trust_label = QLabel("0.70")
        self.rust_label = QLabel("0.30")
        self.stability_label = QLabel("0.60")
        state_layout.addRow("Epoch:", self.epoch_label)
        state_layout.addRow("Trust Level:", self.trust_label)
        state_layout.addRow("Rust Level:", self.rust_label)
        state_layout.addRow("Stability:", self.stability_label)
        state_group.setLayout(state_layout)
        
        # Entities list
        entities_group = QGroupBox("Entities")
        entities_layout = QVBoxLayout()
        self.entities_list = QListWidget()
        entities_layout.addWidget(self.entities_list)
        entities_group.setLayout(entities_layout)
        
        # Consciousness display
        consciousness_group = QGroupBox("Cosmic Consciousness")
        consciousness_layout = QVBoxLayout()
        self.consciousness_label = QLabel("Collective Awareness: 0.000")
        self.consciousness_bar = QProgressBar()
        self.consciousness_bar.setRange(0, 1000)
        consciousness_layout.addWidget(self.consciousness_label)
        consciousness_layout.addWidget(self.consciousness_bar)
        consciousness_group.setLayout(consciousness_layout)
        
        # Assemble info tab
        info_layout.addWidget(state_group)
        info_layout.addWidget(consciousness_group)
        info_layout.addWidget(entities_group)
        info_layout.addStretch()
        
        # Add tabs to left panel
        left_panel.addTab(entity_tab, "Creation")
        left_panel.addTab(info_tab, "Cosmic State")
        
        # Right panel - cosmos visualization
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        
        # Cosmos canvas
        self.canvas = CosmosCanvas(self.world)
        right_layout.addWidget(self.canvas)
        
        # Entity info panel
        self.entity_info = QTextBrowser()
        self.entity_info.setStyleSheet("""
            background-color: #0c1d2b; 
            color: #cae9ff; 
            border: 1px solid #2a4b6a;
            padding: 10px;
        """)
        right_layout.addWidget(self.entity_info)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 3)
        
        # Connect signals
        self.world.cycleChanged.connect(self.update_cycle_display)
        self.world.entityCreated.connect(self.add_entity_to_ui)
        self.world.worldUpdated.connect(self.update_cosmos_view)
        self.canvas.mpl_connect('pick_event', self.on_entity_click)
        
        # Initial update
        self.update_world_info()
        self.update_entity_list()
        
    def create_entity(self):
        """Create a new entity"""
        name = self.name_input.text().strip()
        if name:
            entity_type = self.entity_type.currentText()
            self.world.create_entity(name, "You", entity_type)
            self.name_input.clear()
            
    def update_world_info(self):
        """Update world state displays"""
        self.epoch_label.setText(self.world.epoch)
        self.trust_label.setText(f"{self.world.trust_level:.2f}")
        self.rust_label.setText(f"{self.world.rust_level:.2f}")
        self.stability_label.setText(f"{self.world.stability:.2f}")
        
    def update_entity_list(self):
        """Update the entities list"""
        self.entities_list.clear()
        for entity in self.world.entities:
            item = QListWidgetItem(f"{entity.name} ({entity.entity_type})")
            item.setData(Qt.UserRole, entity)
            self.entities_list.addItem(item)
            
    def update_cycle_display(self, cycle):
        """Update cycle counter"""
        self.setWindowTitle(f"RE_START - Cycle {cycle}")
        
    def update_cosmos_view(self):
        """Update visualization and UI"""
        self.canvas.update_cosmos()
        self.update_entity_list()
        self.update_consciousness_display()
        self.update_world_info()
        
    def update_consciousness_display(self):
        """Update collective awareness display"""
        if self.world.entities:
            avg_consciousness = np.mean([e.traits['consciousness'] for e in self.world.entities])
            self.consciousness_label.setText(
                f"Collective Awareness: {avg_consciousness:.5f}"
            )
            self.consciousness_bar.setValue(int(avg_consciousness * 1000))
        else:
            self.consciousness_label.setText("Collective Awareness: 0.000")
            self.consciousness_bar.setValue(0)
            
    def add_entity_to_ui(self, entity):
        """Add new entity to UI elements"""
        self.update_entity_list()
        
    def on_entity_click(self, event):
        """Handle clicking on entities"""
        if event.mouseevent.dblclick:
            for point, entity in self.canvas.entity_points:
                if point.contains(event.mouseevent)[0]:
                    self.show_entity_info(entity)
                    break
                    
    def show_entity_info(self, entity):
        """Display entity details"""
        info = f"""
        <div style='font-family: Arial; color: #cae9ff;'>
            <h2 style='color: {entity.color};'>{entity.name}</h2>
            <p><b>Type:</b> {entity.entity_type} | <b>Domain:</b> {entity.domain}</p>
            <p><b>Status:</b> {entity.status} | <b>Creator:</b> {entity.creator}</p>
            <p><b>Age:</b> {entity.age} cycles | <b>Energy:</b> {entity.energy:.1f}</p>
            
            <h3>Consciousness Traits:</h3>
            <table border='0' cellspacing='5'>
        """
        
        for trait, value in entity.traits.items():
            bar_width = int(value * 100)
            info += f"""
                <tr>
                    <td width='120'><b>{trait.capitalize()}:</b></td>
                    <td>
                        <div style='background: #1a3b5a; display: inline-block; width: 200px; border-radius: 3px;'>
                            <div style='background: #4fc3f7; width: {bar_width}%; height: 15px; border-radius: 3px;'></div>
                        </div>
                        <span style='margin-left: 10px;'>{value:.3f}</span>
                    </td>
                </tr>
            """
        
        info += "</table>"
        
        if entity.thoughts:
            info += "<h3>Emergent Thoughts:</h3><ul style='color: #ffaa77;'>"
            for thought in set(entity.thoughts[-5:]):
                info += f"<li>\"{thought}\"</li>"
            info += "</ul>"
            
        if entity.artifacts:
            info += "<h3>Created Artifacts:</h3><ul style='color: #aaffaa;'>"
            for art in entity.artifacts[-3:]:
                info += f"<li>{art['type']} (Complexity: {art['complexity']:.1f})</li>"
            info += "</ul>"
            
        info += "</div>"
        self.entity_info.setHtml(info)
        
    def display_scroll(self, index):
        """Display sacred scroll content"""
        conn = sqlite3.connect('re_start.db')
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM scrolls WHERE number=?", (index+1,))
        scroll_data = cursor.fetchone()
        conn.close()
        
        if scroll_data:
            content = scroll_data[0]
            # Format text with indentation
            formatted_text = textwrap.fill(content, width=100)
            
            # Create styled HTML content
            html = f"""
            <html>
            <body style='font-family: Courier; color: #cae9ff; background-color: #0c1d2b; padding: 15px;'>
                <h2 style='color: #4fc3f7;'>Scroll {index+1}</h2>
                <pre style='white-space: pre-wrap;'>{formatted_text}</pre>
            </body>
            </html>
            """
            self.entity_info.setHtml(html)

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
    dark_palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
    dark_palette.setColor(QPalette.HighlightedText, Qt.white)
    app.setPalette(dark_palette)
    
    app.setStyleSheet("""
        QGroupBox {
            font-weight: bold;
            border: 1px solid #2a4b6a;
            border-radius: 5px;
            margin-top: 1ex;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 5px;
            background-color: transparent;
            color: #4fc3f7;
        }
        QListWidget {
            background-color: #0c1d2b;
            color: #cae9ff;
            border: 1px solid #2a4b6a;
            border-radius: 3px;
        }
        QProgressBar {
            border: 1px solid #2a4b6a;
            border-radius: 3px;
            text-align: center;
            background: #0c1d2b;
        }
        QProgressBar::chunk {
            background: #4fc3f7;
        }
        QLineEdit {
            background-color: #0c1d2b;
            color: #cae9ff;
            border: 1px solid #2a4b6a;
            border-radius: 3px;
            padding: 5px;
        }
        QComboBox {
            background-color: #0c1d2b;
            color: #cae9ff;
            border: 1px solid #2a4b6a;
            border-radius: 3px;
            padding: 5px;
        }
        QPushButton {
            background-color: #1a3b5a;
            color: #cae9ff;
            border: 1px solid #2a4b6a;
            border-radius: 3px;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #2a4b6a;
        }
        QPushButton:pressed {
            background-color: #0a2b4a;
        }
    """)
    
    window = REStartApp()
    window.show()
    sys.exit(app.exec_())