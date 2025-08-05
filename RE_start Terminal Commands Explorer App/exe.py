import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import random
import time
import os
import sys
import threading

class DesignExplorerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Design Explorer 2025")
        self.root.geometry("1200x800")
        self.root.configure(bg="#121212")
        
        # Modern color scheme
        self.colors = {
            "bg": "#121212",
            "card_bg": "#1e1e1e",
            "accent": "#7e57c2",  # Deep purple
            "text": "#e0e0e0",
            "success": "#66bb6a",
            "warning": "#ffca28",
            "error": "#ef5350",
            "matrix_green": "#00ff41"
        }
        
        # Design styles
        self.design_styles = {
            "Neo-Immersive": {
                "description": "3D elements with real-world AR integration and tactile micro-interactions",
                "colors": ["#7e57c2", "#5e35b1", "#4527a0"],
                "features": ["Spatial interfaces", "Gesture controls", "Dynamic environments"]
            },
            "Soft Neubrutalism": {
                "description": "Bold shadows with subtle gradients for 3D depth and rounded edges",
                "colors": ["#ff7043", "#ff5722", "#e64a19"],
                "features": ["Asymmetric layouts", "Structured grids", "Rounded UI"]
            },
            "Adaptive Theming": {
                "description": "Auto-shifting color schemes based on context and environment",
                "colors": ["#29b6f6", "#039be5", "#0288d1"],
                "features": ["Contextual dark/light modes", "Palette matching", "Sophisticated transitions"]
            },
            "Inclusive Architecture": {
                "description": "Accessibility-first design with voice control and multi-modal inputs",
                "colors": ["#66bb6a", "#43a047", "#388e3c"],
                "features": ["Voice control", "Eye-tracking", "Multi-modal inputs"]
            }
        }
        
        # Matrix animation properties
        self.matrix_chars = "アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズブヅプエェケセテネヘメレヱゲゼデベペオォコソトノホモヨョロヲゴゾドボポヴッン0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.matrix_streams = []
        self.matrix_running = False
        
        self.create_widgets()
        self.setup_matrix_animation()
        
    def create_widgets(self):
        # Create notebook for different sections
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create frames
        self.style_frame = self.create_frame("Design Styles")
        self.upload_frame = self.create_frame("Python File Upload")
        self.matrix_frame = self.create_frame("Matrix Animation")
        self.about_frame = self.create_frame("About")
        
        # Add frames to notebook
        self.notebook.add(self.style_frame, text="Design Styles")
        self.notebook.add(self.upload_frame, text="File Upload")
        self.notebook.add(self.matrix_frame, text="Matrix Animation")
        self.notebook.add(self.about_frame, text="About")
        
        # Build sections
        self.build_design_styles_section()
        self.build_upload_section()
        self.build_matrix_section()
        self.build_about_section()
        
        # Create status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                                   relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var.set("Ready")
    
    def create_frame(self, name):
        frame = ttk.Frame(self.notebook, style="Card.TFrame")
        return frame
    
    def build_design_styles_section(self):
        # Header
        header = ttk.Label(self.style_frame, text="Modern Design Styles", 
                          font=("Segoe UI", 24, "bold"), style="Header.TLabel")
        header.pack(pady=20)
        
        # Description
        desc = ttk.Label(self.style_frame, 
                        text="Explore cutting-edge design styles for Python applications in 2025",
                        font=("Segoe UI", 12), style="Text.TLabel")
        desc.pack(pady=(0, 30))
        
        # Style cards
        card_frame = ttk.Frame(self.style_frame)
        card_frame.pack(fill="both", expand=True, padx=20)
        
        for i, (style_name, style_data) in enumerate(self.design_styles.items()):
            card = self.create_style_card(card_frame, style_name, style_data)
            card.grid(row=i//2, column=i%2, padx=15, pady=15, sticky="nsew")
        
        # Configure grid
        card_frame.columnconfigure(0, weight=1)
        card_frame.columnconfigure(1, weight=1)
        card_frame.rowconfigure(0, weight=1)
        card_frame.rowconfigure(1, weight=1)
    
    def create_style_card(self, parent, style_name, style_data):
        card = ttk.Frame(parent, style="Card.TFrame", padding=15)
        
        # Style name
        name_label = ttk.Label(card, text=style_name, 
                              font=("Segoe UI", 16, "bold"), style="Header.TLabel")
        name_label.pack(anchor="w", pady=(0, 10))
        
        # Color palette
        color_frame = ttk.Frame(card)
        color_frame.pack(fill="x", pady=5)
        
        for color in style_data["colors"]:
            color_label = ttk.Label(color_frame, background=color, width=3, relief="solid")
            color_label.pack(side="left", padx=2)
        
        # Description
        desc_label = ttk.Label(card, text=style_data["description"], 
                              style="Text.TLabel", wraplength=350)
        desc_label.pack(anchor="w", pady=5)
        
        # Features
        features_label = ttk.Label(card, text="Key Features:", 
                                  font=("Segoe UI", 10, "bold"), style="Text.TLabel")
        features_label.pack(anchor="w", pady=(10, 5))
        
        for feature in style_data["features"]:
            feature_frame = ttk.Frame(card)
            feature_frame.pack(fill="x", pady=2)
            
            ttk.Label(feature_frame, text="•", style="Text.TLabel").pack(side="left", padx=(0, 5))
            ttk.Label(feature_frame, text=feature, style="Text.TLabel").pack(side="left", anchor="w")
        
        # Apply button
        apply_btn = ttk.Button(card, text="Apply Style", 
                              command=lambda s=style_name: self.apply_design_style(s),
                              style="Accent.TButton")
        apply_btn.pack(pady=10, anchor="e")
        
        return card
    
    def build_upload_section(self):
        # Header
        header = ttk.Label(self.upload_frame, text="Python File Design Transformation", 
                          font=("Segoe UI", 24, "bold"), style="Header.TLabel")
        header.pack(pady=20)
        
        # Description
        desc = ttk.Label(self.upload_frame, 
                        text="Upload a Python file to apply modern design transformations",
                        font=("Segoe UI", 12), style="Text.TLabel")
        desc.pack(pady=(0, 30))
        
        # Upload area
        upload_frame = ttk.Frame(self.upload_frame, style="Card.TFrame", padding=20)
        upload_frame.pack(fill="x", padx=50, pady=10)
        
        # File selection
        file_frame = ttk.Frame(upload_frame)
        file_frame.pack(fill="x", pady=10)
        
        self.file_path = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path, state="readonly")
        file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_file)
        browse_btn.pack(side="left")
        
        # Design selection
        style_frame = ttk.Frame(upload_frame)
        style_frame.pack(fill="x", pady=10)
        
        ttk.Label(style_frame, text="Select Design Style:", style="Text.TLabel").pack(side="left", padx=(0, 10))
        
        self.style_var = tk.StringVar()
        style_combo = ttk.Combobox(style_frame, textvariable=self.style_var, state="readonly")
        style_combo["values"] = list(self.design_styles.keys())
        style_combo.current(0)
        style_combo.pack(side="left", fill="x", expand=True)
        
        # Options
        options_frame = ttk.Frame(upload_frame)
        options_frame.pack(fill="x", pady=10)
        
        self.dark_mode = tk.BooleanVar(value=True)
        dark_chk = ttk.Checkbutton(options_frame, text="Dark Mode", 
                                  variable=self.dark_mode, style="Toggle.TCheckbutton")
        dark_chk.pack(side="left", padx=10)
        
        self.animations = tk.BooleanVar(value=True)
        anim_chk = ttk.Checkbutton(options_frame, text="Animations", 
                                  variable=self.animations, style="Toggle.TCheckbutton")
        anim_chk.pack(side="left", padx=10)
        
        self.accessibility = tk.BooleanVar(value=True)
        acc_chk = ttk.Checkbutton(options_frame, text="Accessibility Features", 
                                 variable=self.accessibility, style="Toggle.TCheckbutton")
        acc_chk.pack(side="left", padx=10)
        
        # Transform button
        transform_btn = ttk.Button(upload_frame, text="Transform Design", 
                                  command=self.transform_design, style="Accent.TButton")
        transform_btn.pack(pady=20)
        
        # Preview area
        preview_frame = ttk.LabelFrame(self.upload_frame, text="Design Preview", style="Card.TFrame")
        preview_frame.pack(fill="both", expand=True, padx=50, pady=20)
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, wrap=tk.WORD, 
                                                    bg="#1e1e1e", fg="#e0e0e0", 
                                                    insertbackground="white",
                                                    font=("Consolas", 10))
        self.preview_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.preview_text.insert(tk.END, "Design preview will appear here...")
        self.preview_text.config(state="disabled")
    
    def build_matrix_section(self):
        # Header
        header = ttk.Label(self.matrix_frame, text="Matrix Animation Generator", 
                          font=("Segoe UI", 24, "bold"), style="Header.TLabel")
        header.pack(pady=20)
        
        # Description
        desc = ttk.Label(self.matrix_frame, 
                        text="Customize and generate dynamic Matrix-style header animations",
                        font=("Segoe UI", 12), style="Text.TLabel")
        desc.pack(pady=(0, 30))
        
        # Control panel
        control_frame = ttk.Frame(self.matrix_frame, style="Card.TFrame", padding=20)
        control_frame.pack(fill="x", padx=50, pady=10)
        
        # Animation controls
        ttk.Label(control_frame, text="Animation Speed:", style="Text.TLabel").grid(row=0, column=0, sticky="w", pady=5)
        self.speed_var = tk.IntVar(value=50)
        speed_scale = ttk.Scale(control_frame, from_=10, to=200, variable=self.speed_var,
                               command=lambda e: self.update_matrix_speed())
        speed_scale.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        ttk.Label(control_frame, text="Character Density:", style="Text.TLabel").grid(row=1, column=0, sticky="w", pady=5)
        self.density_var = tk.IntVar(value=30)
        density_scale = ttk.Scale(control_frame, from_=10, to=100, variable=self.density_var,
                                 command=lambda e: self.update_matrix_density())
        density_scale.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        
        # Color controls
        color_frame = ttk.Frame(control_frame)
        color_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="w")
        
        ttk.Label(color_frame, text="Text Color:", style="Text.TLabel").pack(side="left", padx=(0, 10))
        self.color_var = tk.StringVar(value="green")
        colors = ["green", "blue", "red", "purple", "cyan", "yellow"]
        for color in colors:
            rb = ttk.Radiobutton(color_frame, text=color.capitalize(), 
                                variable=self.color_var, value=color,
                                style="Toggle.TRadiobutton")
            rb.pack(side="left", padx=5)
        
        # Start/Stop buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.start_btn = ttk.Button(btn_frame, text="Start Animation", 
                                   command=self.start_matrix_animation,
                                   style="Accent.TButton")
        self.start_btn.pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Stop Animation", 
                  command=self.stop_matrix_animation).pack(side="left", padx=5)
        
        # Canvas for animation
        self.matrix_canvas = tk.Canvas(self.matrix_frame, bg="black", highlightthickness=0)
        self.matrix_canvas.pack(fill="both", expand=True, padx=50, pady=20)
    
    def build_about_section(self):
        # Header
        header = ttk.Label(self.about_frame, text="Python Design Explorer 2025", 
                          font=("Segoe UI", 24, "bold"), style="Header.TLabel")
        header.pack(pady=20)
        
        # Description
        desc_text = (
            "This application showcases modern design trends for Python applications, "
            "combining Neo-Immersive interfaces, Adaptive Theming, and Inclusive Architecture.\n\n"
            "Key features include:\n"
            "• Design style exploration with real-time previews\n"
            "• Python file design transformation\n"
            "• Customizable Matrix-style animations\n"
            "• Dark mode and accessibility-focused design\n\n"
            "Built with Tkinter and inspired by 2025 design trends."
        )
        
        desc = ttk.Label(self.about_frame, text=desc_text, 
                        style="Text.TLabel", wraplength=700, justify="left")
        desc.pack(pady=10, padx=50)
        
        # Features
        features_frame = ttk.Frame(self.about_frame)
        features_frame.pack(pady=20, padx=50, fill="x")
        
        features = [
            ("Neo-Immersive", "3D spatial interfaces with AR integration"),
            ("Soft Neubrutalism", "Bold shadows with subtle gradients for depth"),
            ("Adaptive Theming", "Auto-shifting color schemes based on context"),
            ("Inclusive Design", "Accessibility-first with voice/eye controls")
        ]
        
        for i, (title, text) in enumerate(features):
            card = ttk.Frame(features_frame, style="Card.TFrame", padding=10)
            card.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            
            ttk.Label(card, text=title, font=("Segoe UI", 12, "bold"), 
                     style="Header.TLabel").pack(anchor="w")
            ttk.Label(card, text=text, style="Text.TLabel").pack(anchor="w")
        
        features_frame.columnconfigure(0, weight=1)
        features_frame.columnconfigure(1, weight=1)
        
        # Footer
        footer = ttk.Label(self.about_frame, 
                          text="© 2025 Python Design Explorer | Inspired by modern UI/UX trends",
                          style="Text.TLabel")
        footer.pack(side="bottom", pady=20)
    
    def setup_styles(self):
        # Configure styles
        style = ttk.Style(self.root)
        
        # Theme
        style.theme_use("clam")
        
        # Backgrounds
        style.configure(".", background=self.colors["bg"], foreground=self.colors["text"])
        style.configure("TFrame", background=self.colors["bg"])
        style.configure("TNotebook", background=self.colors["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", 
                        background=self.colors["card_bg"], 
                        foreground=self.colors["text"],
                        padding=[15, 5],
                        font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", 
                 background=[("selected", self.colors["accent"])],
                 foreground=[("selected", "white")])
        
        # Cards
        style.configure("Card.TFrame", background=self.colors["card_bg"], 
                       relief="solid", borderwidth=1, 
                       bordercolor="#333333", padding=10)
        
        # Labels
        style.configure("Header.TLabel", background=self.colors["card_bg"], 
                       foreground=self.colors["text"], font=("Segoe UI", 14))
        style.configure("Text.TLabel", background=self.colors["card_bg"], 
                       foreground=self.colors["text"])
        
        # Buttons
        style.configure("TButton", background=self.colors["card_bg"], 
                       foreground=self.colors["text"], bordercolor="#333333")
        style.map("TButton", 
                 background=[("active", "#333333")],
                 bordercolor=[("active", "#444444")])
        
        style.configure("Accent.TButton", background=self.colors["accent"], 
                       foreground="white", font=("Segoe UI", 10, "bold"))
        style.map("Accent.TButton", 
                 background=[("active", "#9575cd")])
        
        # Checkbuttons and Radiobuttons
        style.configure("Toggle.TCheckbutton", background=self.colors["card_bg"], 
                       foreground=self.colors["text"])
        style.configure("Toggle.TRadiobutton", background=self.colors["card_bg"], 
                       foreground=self.colors["text"])
        
        # Entry and Combobox
        style.configure("TEntry", fieldbackground="#2d2d2d", 
                       foreground=self.colors["text"], insertcolor="white")
        style.configure("TCombobox", fieldbackground="#2d2d2d", 
                       foreground=self.colors["text"])
    
    def apply_design_style(self, style_name):
        self.status_var.set(f"Applied '{style_name}' design style")
        messagebox.showinfo("Style Applied", 
                          f"The '{style_name}' design style has been applied to your workspace.")
        
        # In a real application, this would modify the UI based on the selected style
        colors = self.design_styles[style_name]["colors"]
        self.colors["accent"] = colors[0]
        self.setup_styles()
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if file_path:
            self.file_path.set(file_path)
            self.preview_file(file_path)
    
    def preview_file(self, file_path):
        try:
            with open(file_path, "r") as file:
                content = file.read()
                
            self.preview_text.config(state="normal")
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, content)
            self.preview_text.config(state="disabled")
            
            self.status_var.set(f"Loaded file: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file: {str(e)}")
    
    def transform_design(self):
        if not self.file_path.get():
            messagebox.showwarning("No File", "Please select a Python file first")
            return
        
        style = self.style_var.get()
        dark_mode = "enabled" if self.dark_mode.get() else "disabled"
        animations = "enabled" if self.animations.get() else "disabled"
        accessibility = "enabled" if self.accessibility.get() else "disabled"
        
        # In a real application, this would transform the design of the uploaded file
        # Here we just show a message
        message = (
            f"Design transformation applied!\n\n"
            f"File: {os.path.basename(self.file_path.get())}\n"
            f"Style: {style}\n"
            f"Dark Mode: {dark_mode}\n"
            f"Animations: {animations}\n"
            f"Accessibility: {accessibility}\n\n"
            "The file has been updated with modern design patterns."
        )
        
        messagebox.showinfo("Design Transformed", message)
        self.status_var.set(f"Applied {style} design to file")
    
    def setup_matrix_animation(self):
        self.matrix_width = 800
        self.matrix_height = 400
        self.matrix_font = ("Consolas", 12)
        self.matrix_speed = 50
        self.matrix_density = 30
        self.matrix_color = self.colors["matrix_green"]
    
    def start_matrix_animation(self):
        if self.matrix_running:
            return
            
        self.matrix_running = True
        self.start_btn.config(state="disabled")
        self.status_var.set("Matrix animation started")
        
        # Clear canvas
        self.matrix_canvas.delete("all")
        
        # Create matrix streams
        self.matrix_streams = []
        font_size = 14
        char_width = 10
        char_height = 20
        
        # Calculate number of columns
        num_columns = self.matrix_width // char_width
        
        for _ in range(self.matrix_density):
            x = random.randint(0, num_columns - 1) * char_width
            y = random.randint(-self.matrix_height, 0)
            length = random.randint(5, 30)
            speed = random.uniform(1, 5)
            self.matrix_streams.append({
                "x": x,
                "y": y,
                "length": length,
                "speed": speed,
                "chars": [],
                "brightness": [random.randint(100, 255) for _ in range(length)]
            })
        
        # Start animation thread
        threading.Thread(target=self.animate_matrix, daemon=True).start()
    
    def stop_matrix_animation(self):
        self.matrix_running = False
        self.start_btn.config(state="normal")
        self.status_var.set("Matrix animation stopped")
    
    def update_matrix_speed(self):
        self.matrix_speed = 110 - self.speed_var.get()
    
    def update_matrix_density(self):
        self.matrix_density = self.density_var.get()
    
    def animate_matrix(self):
        while self.matrix_running:
            self.matrix_canvas.delete("matrix_char")
            
            color = self.color_var.get()
            if color == "green": color = "#00ff41"
            elif color == "blue": color = "#00bfff"
            elif color == "red": color = "#ff5555"
            elif color == "purple": color = "#b967ff"
            elif color == "cyan": color = "#00ffff"
            elif color == "yellow": color = "#ffff00"
            
            for stream in self.matrix_streams:
                stream["y"] += stream["speed"]
                
                # If stream is off screen, reset it
                if stream["y"] - stream["length"] * 20 > self.matrix_height:
                    stream["y"] = random.randint(-self.matrix_height, 0)
                    stream["chars"] = []
                    stream["brightness"] = [random.randint(100, 255) for _ in range(stream["length"])]
                
                # Update characters
                if random.random() < 0.05:
                    stream["chars"] = [random.choice(self.matrix_chars) for _ in range(stream["length"])]
                
                # Draw characters
                for i, char in enumerate(stream["chars"]):
                    y_pos = stream["y"] - i * 20
                    
                    if 0 <= y_pos < self.matrix_height:
                        # Calculate brightness gradient
                        brightness = stream["brightness"][i]
                        char_color = self.adjust_color_brightness(color, brightness)
                        
                        self.matrix_canvas.create_text(
                            stream["x"], y_pos,
                            text=char,
                            fill=char_color,
                            font=self.matrix_font,
                            tags="matrix_char"
                        )
            
            self.root.update()
            time.sleep(self.matrix_speed / 1000)
    
    def adjust_color_brightness(self, hex_color, brightness):
        """Adjust color brightness (0-255 scale)"""
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        r = min(255, max(0, int(r * brightness / 255)))
        g = min(255, max(0, int(g * brightness / 255)))
        b = min(255, max(0, int(b * brightness / 255)))
        
        return f"#{r:02x}{g:02x}{b:02x}"

if __name__ == "__main__":
    root = tk.Tk()
    app = DesignExplorerApp(root)
    app.setup_styles()
    root.mainloop()