import sys
import webbrowser
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import random

class ArimedoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arimedo - Bio-Digital Innovation")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon(self.style().standardIcon(QStyle.SP_ComputerIcon)))
        
        # Set dark theme palette
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(10, 25, 47))
        dark_palette.setColor(QPalette.WindowText, QColor(204, 214, 246))
        dark_palette.setColor(QPalette.Base, QColor(17, 34, 64))
        dark_palette.setColor(QPalette.AlternateBase, QColor(10, 25, 47))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(204, 214, 246))
        dark_palette.setColor(QPalette.ToolTipText, QColor(204, 214, 246))
        dark_palette.setColor(QPalette.Text, QColor(204, 214, 246))
        dark_palette.setColor(QPalette.Button, QColor(17, 34, 64))
        dark_palette.setColor(QPalette.ButtonText, QColor(204, 214, 246))
        dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        dark_palette.setColor(QPalette.Highlight, QColor(100, 255, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        self.setPalette(dark_palette)
        
        # Create main tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.West)
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(False)
        
        # Create tabs
        self.home_tab = QWidget()
        self.roles_tab = QWidget()
        self.projects_tab = QWidget()
        self.visualization_tab = QWidget()
        
        # Add tabs
        self.tabs.addTab(self.home_tab, "Home")
        self.tabs.addTab(self.roles_tab, "Roles")
        self.tabs.addTab(self.projects_tab, "Projects")
        self.tabs.addTab(self.visualization_tab, "Bio-Visualizer")
        
        # Setup tabs
        self.setup_home_tab()
        self.setup_roles_tab()
        self.setup_projects_tab()
        self.setup_visualization_tab()
        
        # Set central widget
        self.setCentralWidget(self.tabs)
        
        # Create status bar
        self.statusBar().showMessage("Arimedo Bio-Digital Innovation Platform | RE_start.org 2025")
        
        # Add menu
        self.create_menu()
    
    def create_menu(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def show_about(self):
        QMessageBox.information(self, "About Arimedo", 
            "Arimedo Bio-Digital Innovation Platform\n\n"
            "Fusing Art, Technology, and Biomedical Engineering\n"
            "Version 1.0\n\n"
            "© RE_start.org 2025")
    
    def setup_home_tab(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Title
        title = QLabel("ARIMEDO")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(48)
        title_font.setBold(True)
        title.setFont(title_font)
        
        gradient = QLinearGradient(0, 0, 400, 0)
        gradient.setColorAt(0, QColor(100, 255, 218))
        gradient.setColorAt(1, QColor(198, 120, 221))
        palette = title.palette()
        palette.setBrush(QPalette.WindowText, gradient)
        title.setPalette(palette)
        
        # Subtitle
        subtitle = QLabel("Bio-Digital Innovation Platform")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(24)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #a8b2d1;")
        
        # Description
        description = QLabel(
            "Arimedo represents the fusion of artistic vision, software engineering, game development, "
            "and biomedical expertise. This platform showcases the multidisciplinary innovation at the "
            "intersection of technology and biology.\n\n"
            "Explore your roles as a Creative Neurotech Alchemist, Medical XR Developer, and Biomedical AI Engineer. "
            "Discover projects that blend art, technology, and life sciences to create revolutionary solutions."
        )
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        description.setStyleSheet("color: #a8b2d1; font-size: 16px;")
        description.setContentsMargins(50, 20, 50, 20)
        
        # Logo
        logo = QLabel()
        logo_pixmap = QPixmap(400, 400)
        logo_pixmap.fill(Qt.transparent)
        
        painter = QPainter(logo_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw DNA-like structure
        painter.setPen(QPen(QColor(100, 255, 218), 2))
        for i in range(20):
            angle = i * 18 * 3.14159 / 180
            x = 200 + 150 * np.cos(angle)
            y = 200 + 150 * np.sin(angle)
            painter.drawEllipse(int(x), int(y), 10, 10)
            
            # Connect with lines
            if i > 0:
                prev_angle = (i-1) * 18 * 3.14159 / 180
                prev_x = 200 + 150 * np.cos(prev_angle)
                prev_y = 200 + 150 * np.sin(prev_angle)
                painter.drawLine(int(prev_x), int(prev_y), int(x), int(y))
                
                # Draw connecting lines between strands
                mid_x = (prev_x + x) / 2
                mid_y = (prev_y + y) / 2
                painter.drawLine(int(prev_x), int(prev_y), int(200), int(200))
        
        # Draw central brain-like structure
        painter.setPen(QPen(QColor(198, 120, 221), 3))
        path = QPainterPath()
        path.moveTo(200, 150)
        path.cubicTo(250, 100, 300, 150, 300, 200)
        path.cubicTo(300, 250, 250, 300, 200, 250)
        path.cubicTo(150, 300, 100, 250, 100, 200)
        path.cubicTo(100, 150, 150, 100, 200, 150)
        painter.drawPath(path)
        
        painter.end()
        
        logo.setPixmap(logo_pixmap)
        logo.setAlignment(Qt.AlignCenter)
        
        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(logo)
        layout.addWidget(description)
        
        self.home_tab.setLayout(layout)
    
    def setup_roles_tab(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Your Multidisciplinary Roles")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #64ffda; margin-bottom: 30px;")
        
        layout.addWidget(title)
        
        # Roles grid
        grid = QGridLayout()
        grid.setSpacing(20)
        
        # Roles data
        roles = [
            {
                "title": "Creative Neurotech Alchemist",
                "icon": "brain",
                "description": "Merging artistic vision with neuroscience to create revolutionary brain-computer interfaces and neural art installations.",
                "color": "#c678dd"
            },
            {
                "title": "Medical XR Developer",
                "icon": "vr-cardboard",
                "description": "Building immersive VR/AR experiences for surgical training, patient therapy, and medical education using game development techniques.",
                "color": "#61afef"
            },
            {
                "title": "Biomedical AI Engineer",
                "description": "Developing intelligent systems that predict diseases, analyze medical imaging, and accelerate drug discovery using machine learning.",
                "icon": "dna",
                "color": "#e06c75"
            },
            {
                "title": "Bio-Art Technologist",
                "description": "Transforming biological concepts into stunning visual experiences through generative art and scientific visualization.",
                "icon": "paint-brush",
                "color": "#e5c07b"
            }
        ]
        
        for i, role in enumerate(roles):
            role_widget = self.create_role_card(role)
            grid.addWidget(role_widget, i // 2, i % 2)
        
        layout.addLayout(grid)
        layout.addStretch()
        self.roles_tab.setLayout(layout)
    
    def create_role_card(self, role):
        widget = QWidget()
        widget.setStyleSheet(f"""
            background-color: #112240;
            border-radius: 10px;
            border-left: 5px solid {role['color']};
            padding: 20px;
        """)
        
        layout = QVBoxLayout()
        
        # Icon and title
        icon_title_layout = QHBoxLayout()
        
        icon_label = QLabel()
        icon_label.setPixmap(self.style().standardIcon(getattr(QStyle, f"SP_{role['icon'].upper()}")).pixmap(48, 48))
        
        title = QLabel(role['title'])
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {role['color']};")
        
        icon_title_layout.addWidget(icon_label)
        icon_title_layout.addWidget(title)
        icon_title_layout.addStretch()
        
        # Description
        description = QLabel(role['description'])
        description.setStyleSheet("color: #a8b2d1; font-size: 14px;")
        description.setWordWrap(True)
        
        layout.addLayout(icon_title_layout)
        layout.addWidget(description)
        
        widget.setLayout(layout)
        return widget
    
    def setup_projects_tab(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Innovation Projects")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #64ffda; margin-bottom: 30px;")
        
        layout.addWidget(title)
        
        # Projects list
        projects = [
            {
                "name": "NeuroArt BCI Gallery",
                "description": "Interactive exhibition where brainwaves generate digital artworks through EEG headsets and generative AI",
                "technologies": ["Unity", "OpenBCI", "Python", "TensorFlow"]
            },
            {
                "name": "BioSync Wearables",
                "description": "Smart wearables that monitor biomarkers and translate health data into therapeutic art experiences",
                "technologies": ["IoT Sensors", "Python", "React Native", "AWS"]
            },
            {
                "name": "Organ Digital Twins",
                "description": "Interactive 3D models of human organs for surgical planning and medical education",
                "technologies": ["Blender", "DICOM", "Unity", "Python"]
            },
            {
                "name": "Surgical VR Trainer",
                "description": "Immersive surgical training simulator with haptic feedback and real-time performance analytics",
                "technologies": ["Unreal Engine", "Haptic Gloves", "C++", "ML"]
            }
        ]
        
        for project in projects:
            project_widget = self.create_project_card(project)
            layout.addWidget(project_widget)
        
        layout.addStretch()
        self.projects_tab.setLayout(layout)
    
    def create_project_card(self, project):
        widget = QWidget()
        widget.setStyleSheet("""
            background-color: #112240;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
        """)
        
        layout = QVBoxLayout()
        
        # Project name
        name = QLabel(project["name"])
        name_font = QFont()
        name_font.setPointSize(16)
        name_font.setBold(True)
        name.setFont(name_font)
        name.setStyleSheet("color: #64ffda;")
        
        # Description
        description = QLabel(project["description"])
        description.setStyleSheet("color: #a8b2d1; font-size: 14px;")
        description.setWordWrap(True)
        
        # Technologies
        tech_layout = QHBoxLayout()
        tech_layout.addWidget(QLabel("Technologies:"))
        
        for tech in project["technologies"]:
            tech_label = QLabel(tech)
            tech_label.setStyleSheet("""
                background-color: #0a192f;
                color: #61afef;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 12px;
            """)
            tech_layout.addWidget(tech_label)
        
        tech_layout.addStretch()
        
        layout.addWidget(name)
        layout.addWidget(description)
        layout.addLayout(tech_layout)
        
        widget.setLayout(layout)
        return widget
    
    def setup_visualization_tab(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Bio-Digital Visualization")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #64ffda; margin-bottom: 30px;")
        
        layout.addWidget(title)
        
        # Visualization area
        self.figure = plt.figure(facecolor='#0a192f')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: #0a192f;")
        layout.addWidget(self.canvas)
        
        # Controls
        controls = QHBoxLayout()
        
        brain_btn = QPushButton("Neural Network")
        brain_btn.setStyleSheet("background-color: #c678dd; color: black; font-weight: bold;")
        brain_btn.clicked.connect(self.plot_neural_network)
        
        dna_btn = QPushButton("DNA Sequence")
        dna_btn.setStyleSheet("background-color: #61afef; color: black; font-weight: bold;")
        dna_btn.clicked.connect(self.plot_dna)
        
        cell_btn = QPushButton("Cell Structure")
        cell_btn.setStyleSheet("background-color: #e5c07b; color: black; font-weight: bold;")
        cell_btn.clicked.connect(self.plot_cell)
        
        controls.addWidget(brain_btn)
        controls.addWidget(dna_btn)
        controls.addWidget(cell_btn)
        
        layout.addLayout(controls)
        
        self.visualization_tab.setLayout(layout)
        
        # Plot initial visualization
        self.plot_neural_network()
    
    def plot_neural_network(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111, facecolor='#0a192f')
        
        # Draw neural network
        layer_sizes = [4, 6, 5, 3]
        v_spacing = 1.0 / float(max(layer_sizes))
        h_spacing = 1.0 / float(len(layer_sizes) - 1)
        
        # Colors
        colors = ['#c678dd', '#61afef', '#e5c07b', '#e06c75', '#98c379']
        
        for i, layer_size in enumerate(layer_sizes):
            layer_top = v_spacing * (layer_size - 1) / 2. + 0.5
            for j in range(layer_size):
                circle = plt.Circle((i * h_spacing, layer_top - j * v_spacing), 
                                    v_spacing / 4.0,
                                    color=colors[i % len(colors)],
                                    ec='w', zorder=4)
                ax.add_artist(circle)
                
                # Draw connections
                if i > 0:
                    prev_layer_size = layer_sizes[i - 1]
                    prev_layer_top = v_spacing * (prev_layer_size - 1) / 2. + 0.5
                    for k in range(prev_layer_size):
                        line = plt.Line2D(
                            [(i - 1) * h_spacing, i * h_spacing],
                            [prev_layer_top - k * v_spacing, layer_top - j * v_spacing],
                            c=random.choice(colors),
                            alpha=0.6,
                            linewidth=0.7 + random.random() * 1.3
                        )
                        ax.add_artist(line)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        ax.set_title('Neural Network Visualization', color='#64ffda', fontsize=14)
        
        self.canvas.draw()
    
    def plot_dna(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111, facecolor='#0a192f')
        
        # Draw DNA strand
        n = 100
        t = np.linspace(0, 4 * np.pi, n)
        x = np.sin(t)
        y = np.cos(t)
        z = t / 10
        
        # Main strand
        ax.plot(z, x, color='#61afef', linewidth=2, label='Strand 1')
        ax.plot(z, y, color='#c678dd', linewidth=2, label='Strand 2')
        
        # Connections
        for i in range(0, n, 5):
            ax.plot([z[i], z[i]], [x[i], y[i]], color='#98c379', linewidth=0.8, alpha=0.7)
        
        # Nucleotides
        for i in range(0, n, 10):
            ax.scatter(z[i], x[i], s=30, color='#61afef', edgecolor='w', zorder=3)
            ax.scatter(z[i], y[i], s=30, color='#c678dd', edgecolor='w', zorder=3)
        
        ax.set_xlim(min(z), max(z))
        ax.set_ylim(-1.5, 1.5)
        ax.axis('off')
        ax.set_title('DNA Structure Visualization', color='#64ffda', fontsize=14)
        
        self.canvas.draw()
    
    def plot_cell(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111, facecolor='#0a192f')
        
        # Draw cell membrane
        circle = plt.Circle((0.5, 0.5), 0.4, color='#61afef', alpha=0.2, ec='#61afef', linewidth=2)
        ax.add_artist(circle)
        
        # Draw nucleus
        nucleus = plt.Circle((0.5, 0.5), 0.15, color='#c678dd', alpha=0.5, ec='w')
        ax.add_artist(nucleus)
        
        # Draw nucleolus
        nucleolus = plt.Circle((0.5, 0.5), 0.05, color='#e06c75', alpha=0.8, ec='w')
        ax.add_artist(nucleolus)
        
        # Draw mitochondria
        mitochondria_x = [0.3, 0.7, 0.4, 0.6, 0.35]
        mitochondria_y = [0.3, 0.7, 0.6, 0.4, 0.7]
        for x, y in zip(mitochondria_x, mitochondria_y):
            ellipse = plt.Ellipse((x, y), 0.1, 0.05, angle=45, color='#98c379', alpha=0.7)
            ax.add_artist(ellipse)
            # Inner lines
            ax.plot([x-0.04, x+0.04], [y, y], color='w', linewidth=1)
            ax.plot([x-0.02, x+0.02], [y-0.02, y+0.02], color='w', linewidth=1)
            ax.plot([x-0.02, x+0.02], [y+0.02, y-0.02], color='w', linewidth=1)
        
        # Draw vesicles
        for i in range(8):
            angle = i * 45 * np.pi / 180
            r = 0.3 + random.random() * 0.1
            x = 0.5 + r * np.cos(angle)
            y = 0.5 + r * np.sin(angle)
            size = 0.02 + random.random() * 0.03
            vesicle = plt.Circle((x, y), size, color='#e5c07b', alpha=0.8)
            ax.add_artist(vesicle)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        ax.set_title('Cell Structure Visualization', color='#64ffda', fontsize=14)
        
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Set application font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Create and show main window
    window = ArimedoApp()
    window.show()
    
    sys.exit(app.exec_())