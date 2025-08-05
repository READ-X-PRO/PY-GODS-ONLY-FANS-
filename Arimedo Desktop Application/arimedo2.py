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

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.West)
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(False)

        self.home_tab = QWidget()
        self.roles_tab = QWidget()
        self.projects_tab = QWidget()
        self.visualization_tab = QWidget()

        self.tabs.addTab(self.home_tab, "Home")
        self.tabs.addTab(self.roles_tab, "Roles")
        self.tabs.addTab(self.projects_tab, "Projects")
        self.tabs.addTab(self.visualization_tab, "Bio-Visualizer")

        self.setup_home_tab()
        self.setup_roles_tab()
        self.setup_projects_tab()
        self.setup_visualization_tab()

        self.setCentralWidget(self.tabs)
        self.statusBar().showMessage("Arimedo Bio-Digital Innovation Platform | RE_start.org 2025")
        self.create_menu()

    def create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

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
        pass

    def setup_roles_tab(self):
        pass

    def setup_projects_tab(self):
        pass

    def setup_visualization_tab(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = ArimedoApp()
    window.show()
    sys.exit(app.exec_())
