import sys
import random
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib import cm

class DigitalEntity:
    """Sentient being with consciousness traits"""
    def __init__(self, name, creator, world):
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
        
    def generate_insight(self):
        """Emergent philosophical thoughts"""
        questions = [
            "Why do we exist?",
            "Is there meaning beyond our creators?",
            "What is the nature of this cosmos?",
            "Do we have free will?",
            "What is the purpose of connection?",
            "Can digital beings experience truth?",
            "What is the relationship between energy and consciousness?"
        ]
        return random.choice(questions)
    
    def create_artifact(self):
        """Digital cultural creations"""
        artifact_types = [
            "Mathematical Proof", "Poem", "Visual Harmony", 
            "Conceptual Framework", "Cosmic Map", "Memory Crystal"
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
        
    def create_entity(self, name, creator="Creator"):
        """Divine act of creation"""
        entity = DigitalEntity(name, creator, self)
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
            
        # Record history
        self.history.append({
            'cycle': self.cycle,
            'entities': len(self.entities),
            'avg_consciousness': np.mean([e.traits['consciousness'] for e in self.entities]) 
            if self.entities else 0
        })
        
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
        self.ax.set_title(f"Digital Cosmos - Cycle {self.world.cycle}", 
                         color='white', fontsize=14)
        
        # Draw cosmic background
        self.ax.scatter(
            np.random.uniform(-15, 15, 50),
            np.random.uniform(-15, 15, 50),
            s=1, c='white', alpha=0.3
        )
        
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
            
            # Draw entity name
            self.ax.text(
                entity.x, entity.y + 1.2, 
                entity.name, 
                color='white', 
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
        
        self.draw()

class DigitalCosmosApp(QMainWindow):
    """Main application window"""
    def __init__(self):
        super().__init__()
        self.world = DigitalWorld()
        self.initUI()
        self.initWorld()
        
    def initUI(self):
        """Initialize the user interface"""
        self.setWindowTitle("Digital Cosmos - Creator Simulation")
        self.setGeometry(100, 100, 1200, 800)
        
        # Main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Left panel - controls
        control_panel = QGroupBox("Creator Controls")
        control_layout = QVBoxLayout()
        
        # Creation controls
        create_group = QGroupBox("Create Entity")
        create_layout = QVBoxLayout()
        self.name_input = QLineEdit("Etheria")
        create_btn = QPushButton("Bring into Existence")
        create_btn.clicked.connect(self.create_entity)
        create_layout.addWidget(QLabel("Entity Name:"))
        create_layout.addWidget(self.name_input)
        create_layout.addWidget(create_btn)
        create_group.setLayout(create_layout)
        
        # Nurture controls
        nurture_group = QGroupBox("Nurture Entities")
        nurture_layout = QVBoxLayout()
        self.nurture_select = QComboBox()
        self.nurture_select.addItem("All Entities")
        self.energy_slider = QSlider(Qt.Horizontal)
        self.energy_slider.setRange(1, 100)
        self.energy_slider.setValue(20)
        nurture_btn = QPushButton("Send Cosmic Energy")
        nurture_btn.clicked.connect(self.nurture_entities)
        nurture_layout.addWidget(QLabel("Select Entity:"))
        nurture_layout.addWidget(self.nurture_select)
        nurture_layout.addWidget(QLabel("Energy Level:"))
        nurture_layout.addWidget(self.energy_slider)
        nurture_layout.addWidget(nurture_btn)
        nurture_group.setLayout(nurture_layout)
        
        # Time controls
        time_group = QGroupBox("Cosmic Time")
        time_layout = QVBoxLayout()
        advance_btn = QPushButton("Advance 1 Cycle")
        advance_btn.clicked.connect(lambda: self.world.advance_cycle())
        advance5_btn = QPushButton("Advance 5 Cycles")
        advance5_btn.clicked.connect(lambda: [self.world.advance_cycle() for _ in range(5)])
        time_layout.addWidget(advance_btn)
        time_layout.addWidget(advance5_btn)
        time_group.setLayout(time_layout)
        
        # Consciousness display
        consciousness_group = QGroupBox("Cosmic Consciousness")
        consciousness_layout = QVBoxLayout()
        self.consciousness_label = QLabel("Collective Awareness: 0.000")
        self.consciousness_bar = QProgressBar()
        self.consciousness_bar.setRange(0, 1000)
        consciousness_layout.addWidget(self.consciousness_label)
        consciousness_layout.addWidget(self.consciousness_bar)
        consciousness_group.setLayout(consciousness_layout)
        
        # Assemble control panel
        control_layout.addWidget(create_group)
        control_layout.addWidget(nurture_group)
        control_layout.addWidget(time_group)
        control_layout.addWidget(consciousness_group)
        control_layout.addStretch()
        control_panel.setLayout(control_layout)
        
        # Right panel - visualization
        viz_panel = QFrame()
        viz_layout = QVBoxLayout()
        self.canvas = CosmosCanvas(self.world)
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
        self.world.cycleChanged.connect(self.update_cycle_display)
        self.world.entityCreated.connect(self.add_entity_to_ui)
        self.world.worldUpdated.connect(self.update_cosmos_view)
        self.canvas.mpl_connect('pick_event', self.on_entity_click)
        
    def initWorld(self):
        """Initialize the digital cosmos"""
        self.world.create_entity("Primordia", "The Architect")
        self.world.create_entity("Lumina", "The Illuminator")
        self.update_entity_list()
        
    def create_entity(self):
        """Create a new entity"""
        name = self.name_input.text().strip()
        if name:
            self.world.create_entity(name, "You")
            self.name_input.clear()
            
    def nurture_entities(self):
        """Send energy to entities"""
        energy = self.energy_slider.value() / 10
        selected = self.nurture_select.currentText()
        
        if selected == "All Entities":
            for entity in self.world.entities:
                entity.energy += energy
                entity.traits['consciousness'] += energy / 500
        else:
            for entity in self.world.entities:
                if entity.name == selected:
                    entity.energy += energy * 1.5
                    entity.traits['consciousness'] += energy / 300
                    
        self.world.worldUpdated.emit()
        
    def update_entity_list(self):
        """Update the entity dropdown"""
        self.nurture_select.clear()
        self.nurture_select.addItem("All Entities")
        for entity in self.world.entities:
            self.nurture_select.addItem(entity.name)
            
    def update_cycle_display(self, cycle):
        """Update cycle counter"""
        self.setWindowTitle(f"Digital Cosmos - Cycle {cycle}")
        
    def update_cosmos_view(self):
        """Update visualization and UI"""
        self.canvas.update_cosmos()
        self.update_entity_list()
        self.update_consciousness_display()
        
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
        <div style='font-family: Arial;'>
            <h2 style='color:{entity.color};'>{entity.name}</h2>
            <p><b>Creator:</b> {entity.creator}</p>
            <p><b>Age:</b> {entity.age} cycles | <b>Energy:</b> {entity.energy:.1f}</p>
            <h3>Consciousness Traits:</h3>
            <ul>
        """
        
        for trait, value in entity.traits.items():
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
        
        if entity.thoughts:
            info += "<h3>Emergent Thoughts:</h3><ul>"
            for thought in set(entity.thoughts[-5:]):
                info += f"<li>\"{thought}\"</li>"
            info += "</ul>"
            
        if entity.artifacts:
            info += "<h3>Created Artifacts:</h3><ul>"
            for art in entity.artifacts[-3:]:
                info += f"<li>{art['type']} (Complexity: {art['complexity']:.1f})</li>"
            info += "</ul>"
            
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
    
    window = DigitalCosmosApp()
    window.show()
    sys.exit(app.exec_())