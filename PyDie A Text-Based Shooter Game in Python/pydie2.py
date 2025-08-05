import pygame
import pyglet
from pyglet.gl import *
import sys
import os
import math
import random
import shutil
import subprocess
from pygame.locals import *
from zipfile import ZipFile
from io import BytesIO
import base64

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
GAME_TITLE = "PyDie: Tactical Warfare"
VERSION = "1.0"

# Asset paths (will be created during installation)
TEXTURES_PATH = "textures"
MODELS_PATH = "models"
SOUNDS_PATH = "sounds"
SETTINGS_PATH = "settings.cfg"

class PyDieInstaller:
    """Handles the installation of game assets and dependencies"""
    def __init__(self):
        self.assets_installed = False
        self.check_assets()
        
    def check_assets(self):
        """Check if game assets are installed"""
        if os.path.exists(TEXTURES_PATH) and os.path.exists(MODELS_PATH) and os.path.exists(SOUNDS_PATH):
            self.assets_installed = True
            
    def install_assets(self):
        """Install game assets from embedded data"""
        try:
            # Create directories
            os.makedirs(TEXTURES_PATH, exist_ok=True)
            os.makedirs(MODELS_PATH, exist_ok=True)
            os.makedirs(SOUNDS_PATH, exist_ok=True)
            
            # Extract textures
            texture_files = [
                "ground_texture", "wall_texture", "sky_texture", 
                "metal_texture", "weapon_texture", "character_diffuse"
            ]
            
            for tex in texture_files:
                with open(os.path.join(TEXTURES_PATH, f"{tex}.png"), "wb") as f:
                    f.write(base64.b64decode(self.get_base64_texture(tex)))
            
            # Extract models
            model_files = ["rifle_model", "character_model", "ammo_model"]
            for model in model_files:
                with open(os.path.join(MODELS_PATH, f"{model}.obj"), "w") as f:
                    f.write(self.get_model_data(model))
            
            # Extract sounds
            sound_files = [
                "gunshot", "reload", "explosion", "footstep", 
                "ambient", "hurt", "death", "victory"
            ]
            for sound in sound_files:
                with open(os.path.join(SOUNDS_PATH, f"{sound}.wav"), "wb") as f:
                    f.write(base64.b64decode(self.get_base64_sound(sound)))
            
            # Create default settings
            with open(SETTINGS_PATH, "w") as f:
                f.write("[Settings]\n")
                f.write("resolution=1200x800\n")
                f.write("fullscreen=0\n")
                f.write("volume=80\n")
                f.write("sensitivity=50\n")
            
            self.assets_installed = True
            return True
        except Exception as e:
            print(f"Installation failed: {e}")
            return False
            
    def get_base64_texture(self, name):
        """Return base64 encoded texture (placeholder implementation)"""
        # In a real implementation, this would return actual texture data
        return b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    
    def get_model_data(self, name):
        """Return model data (placeholder implementation)"""
        # In a real implementation, this would return actual model data
        return f"# {name} placeholder\nv 0.0 0.0 0.0\n"
    
    def get_base64_sound(self, name):
        """Return base64 encoded sound (placeholder implementation)"""
        # In a real implementation, this would return actual sound data
        return b"UklGRigAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQQAAAA="

class SettingsManager:
    """Manages game settings and configuration"""
    def __init__(self):
        self.settings = {
            "resolution": (1200, 800),
            "fullscreen": False,
            "volume": 80,
            "sensitivity": 50,
            "texture_quality": "high",
            "shadows": True,
            "vsync": True
        }
        self.load_settings()
        
    def load_settings(self):
        """Load settings from file"""
        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, "r") as f:
                    for line in f:
                        if line.strip() and not line.startswith("["):
                            key, value = line.strip().split("=")
                            if key == "resolution":
                                w, h = value.split("x")
                                self.settings["resolution"] = (int(w), int(h))
                            elif key == "fullscreen":
                                self.settings["fullscreen"] = bool(int(value))
                            elif key == "volume":
                                self.settings["volume"] = int(value)
                            elif key == "sensitivity":
                                self.settings["sensitivity"] = int(value)
            except:
                print("Error loading settings, using defaults")
    
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(SETTINGS_PATH, "w") as f:
                f.write("[Settings]\n")
                f.write(f"resolution={self.settings['resolution'][0]}x{self.settings['resolution'][1]}\n")
                f.write(f"fullscreen={1 if self.settings['fullscreen'] else 0}\n")
                f.write(f"volume={self.settings['volume']}\n")
                f.write(f"sensitivity={self.settings['sensitivity']}\n")
                f.write(f"texture_quality={self.settings['texture_quality']}\n")
                f.write(f"shadows={1 if self.settings['shadows'] else 0}\n")
                f.write(f"vsync={1 if self.settings['vsync'] else 0}\n")
            return True
        except:
            return False

class Weapon:
    """Represents a weapon in the game"""
    def __init__(self, name, damage, fire_rate, ammo_capacity, reload_time, model_path, texture_path):
        self.name = name
        self.damage = damage
        self.fire_rate = fire_rate  # shots per second
        self.ammo_capacity = ammo_capacity
        self.reload_time = reload_time  # in seconds
        self.current_ammo = ammo_capacity
        self.last_shot_time = 0
        self.is_reloading = False
        self.reload_start_time = 0
        
        # Load 3D model
        self.model = self.load_model(model_path)
        self.texture = self.load_texture(texture_path)
    
    def load_model(self, path):
        """Load a 3D model from file (simplified)"""
        # In a real implementation, this would load an actual model
        return {"vertices": [], "normals": [], "texcoords": []}
    
    def load_texture(self, path):
        """Load a texture from file"""
        # In a real implementation, this would load an actual texture
        return pyglet.image.load(path).get_texture()
    
    def fire(self, current_time):
        """Attempt to fire the weapon"""
        if self.is_reloading:
            return False
            
        if current_time - self.last_shot_time > 1.0 / self.fire_rate:
            if self.current_ammo > 0:
                self.current_ammo -= 1
                self.last_shot_time = current_time
                return True
        return False
    
    def start_reload(self, current_time):
        """Start reloading the weapon"""
        if not self.is_reloading and self.current_ammo < self.ammo_capacity:
            self.is_reloading = True
            self.reload_start_time = current_time
            return True
        return False
    
    def update(self, current_time):
        """Update weapon state"""
        if self.is_reloading and current_time - self.reload_start_time > self.reload_time:
            self.current_ammo = self.ammo_capacity
            self.is_reloading = False

class Player:
    """Represents the player character"""
    def __init__(self, position=(0, 0, 0)):
        self.position = list(position)
        self.rotation = [0, 0]  # yaw, pitch
        self.velocity = [0, 0, 0]
        self.health = 100
        self.max_health = 100
        self.armor = 0
        self.max_armor = 100
        self.is_moving = False
        self.is_crouching = False
        self.is_sprinting = False
        self.is_aiming = False
        self.weapons = []
        self.current_weapon_index = 0
        self.score = 0
        self.kills = 0
        self.deaths = 0
        
        # Load character model
        self.model = self.load_model(os.path.join(MODELS_PATH, "character_model.obj"))
        self.texture = self.load_texture(os.path.join(TEXTURES_PATH, "character_diffuse.png"))
    
    @property
    def current_weapon(self):
        """Get the currently equipped weapon"""
        if self.weapons:
            return self.weapons[self.current_weapon_index]
        return None
    
    def load_model(self, path):
        """Load a 3D model from file (simplified)"""
        # In a real implementation, this would load an actual model
        return {"vertices": [], "normals": [], "texcoords": []}
    
    def load_texture(self, path):
        """Load a texture from file"""
        # In a real implementation, this would load an actual texture
        return pyglet.image.load(path).get_texture()
    
    def move(self, direction, dt):
        """Move the player in the specified direction"""
        speed = 5.0 * dt
        if self.is_sprinting:
            speed *= 1.8
        elif self.is_crouching:
            speed *= 0.5
            
        # Calculate movement vector based on rotation
        rad_yaw = math.radians(self.rotation[0])
        dx = math.sin(rad_yaw) * direction[0] + math.cos(rad_yaw) * direction[1]
        dz = math.cos(rad_yaw) * direction[0] - math.sin(rad_yaw) * direction[1]
        
        self.position[0] += dx * speed
        self.position[2] += dz * speed
        self.is_moving = True
    
    def rotate(self, dx, dy, sensitivity):
        """Rotate the player's view"""
        self.rotation[0] += dx * sensitivity
        self.rotation[1] += dy * sensitivity
        
        # Clamp pitch to avoid flipping
        self.rotation[1] = max(-90, min(90, self.rotation[1]))
    
    def take_damage(self, amount):
        """Apply damage to the player"""
        if self.armor > 0:
            armor_damage = min(self.armor, amount * 0.7)
            self.armor -= armor_damage
            amount -= armor_damage
            
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            return True  # Player died
        return False
    
    def add_weapon(self, weapon):
        """Add a weapon to the player's arsenal"""
        self.weapons.append(weapon)
    
    def switch_weapon(self, index):
        """Switch to a different weapon"""
        if 0 <= index < len(self.weapons):
            self.current_weapon_index = index
    
    def update(self, dt):
        """Update player state"""
        # Apply gravity
        self.velocity[1] -= 9.8 * dt
        
        # Update position based on velocity
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt
        self.position[2] += self.velocity[2] * dt
        
        # Reset movement flag
        self.is_moving = False
        
        # Update current weapon
        if self.current_weapon:
            self.current_weapon.update(pyglet.clock.get_default().time())

class Enemy:
    """Represents an enemy character"""
    def __init__(self, position, enemy_type="soldier"):
        self.position = list(position)
        self.rotation = [0, 0]  # yaw, pitch
        self.health = 100
        self.max_health = 100
        self.speed = 2.0
        self.detection_range = 20.0
        self.attack_range = 15.0
        self.attack_damage = 10
        self.attack_cooldown = 1.0
        self.last_attack_time = 0
        self.is_alive = True
        self.type = enemy_type
        
        # Load enemy model
        self.model = self.load_model(os.path.join(MODELS_PATH, "character_model.obj"))
        self.texture = self.load_texture(os.path.join(TEXTURES_PATH, "enemy_diffuse.png"))
    
    def load_model(self, path):
        """Load a 3D model from file (simplified)"""
        # In a real implementation, this would load an actual model
        return {"vertices": [], "normals": [], "texcoords": []}
    
    def load_texture(self, path):
        """Load a texture from file"""
        # In a real implementation, this would load an actual texture
        return pyglet.image.load(path).get_texture()
    
    def take_damage(self, amount):
        """Apply damage to the enemy"""
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            return True  # Enemy died
        return False
    
    def update(self, dt, player_position):
        """Update enemy state and AI"""
        if not self.is_alive:
            return
            
        # Calculate distance to player
        dx = player_position[0] - self.position[0]
        dz = player_position[2] - self.position[2]
        distance = math.sqrt(dx*dx + dz*dz)
        
        # Rotate toward player
        self.rotation[0] = math.degrees(math.atan2(dx, dz))
        
        if distance < self.detection_range:
            if distance > self.attack_range:
                # Move toward player
                direction_x = dx / distance
                direction_z = dz / distance
                self.position[0] += direction_x * self.speed * dt
                self.position[2] += direction_z * self.speed * dt
            else:
                # Attack player if cooldown is over
                current_time = pyglet.clock.get_default().time()
                if current_time - self.last_attack_time > self.attack_cooldown:
                    self.last_attack_time = current_time
                    return self.attack_damage  # Return damage amount
        return 0

class Environment:
    """Manages the game environment and level"""
    def __init__(self):
        self.terrain = []
        self.buildings = []
        self.skybox = None
        self.ambient_light = (0.3, 0.3, 0.3, 1.0)
        self.directional_light = (-0.5, -1.0, -0.5)
        self.fog_color = (0.5, 0.6, 0.7, 1.0)
        self.fog_density = 0.002
        self.load_environment()
    
    def load_environment(self):
        """Load environment assets"""
        # Load terrain textures
        self.ground_texture = self.load_texture(os.path.join(TEXTURES_PATH, "ground_texture.png"))
        self.wall_texture = self.load_texture(os.path.join(TEXTURES_PATH, "wall_texture.png"))
        self.sky_texture = self.load_texture(os.path.join(TEXTURES_PATH, "sky_texture.png"))
        
        # Generate a simple level
        self.generate_level()
    
    def load_texture(self, path):
        """Load a texture from file"""
        # In a real implementation, this would load an actual texture
        return pyglet.image.load(path).get_texture()
    
    def generate_level(self):
        """Generate a simple level layout"""
        # Ground plane
        self.terrain.append({
            "type": "plane",
            "position": (0, 0, 0),
            "size": (100, 100),
            "texture": self.ground_texture
        })
        
        # Buildings and walls
        for i in range(5):
            x = random.uniform(-40, 40)
            z = random.uniform(-40, 40)
            width = random.uniform(5, 15)
            depth = random.uniform(5, 15)
            height = random.uniform(3, 8)
            
            self.buildings.append({
                "type": "cube",
                "position": (x, height/2, z),
                "size": (width, height, depth),
                "texture": self.wall_texture
            })
    
    def render(self):
        """Render the environment (simplified)"""
        # In a real implementation, this would render the 3D environment
        pass

class AudioManager:
    """Manages game audio and sound effects"""
    def __init__(self, settings):
        self.settings = settings
        self.sounds = {}
        self.music_player = None
        self.load_sounds()
    
    def load_sounds(self):
        """Load all game sounds"""
        sound_files = {
            "gunshot": "gunshot.wav",
            "reload": "reload.wav",
            "explosion": "explosion.wav",
            "footstep": "footstep.wav",
            "ambient": "ambient.wav",
            "hurt": "hurt.wav",
            "death": "death.wav",
            "victory": "victory.wav"
        }
        
        for name, filename in sound_files.items():
            try:
                self.sounds[name] = pygame.mixer.Sound(os.path.join(SOUNDS_PATH, filename))
            except:
                print(f"Failed to load sound: {filename}")
    
    def play_sound(self, name, volume=1.0):
        """Play a sound effect"""
        if name in self.sounds:
            sound = self.sounds[name]
            sound.set_volume(volume * self.settings["volume"] / 100.0)
            sound.play()
    
    def play_music(self, name, loop=True):
        """Play background music"""
        try:
            pygame.mixer.music.load(os.path.join(SOUNDS_PATH, f"{name}.wav"))
            pygame.mixer.music.set_volume(self.settings["volume"] / 100.0)
            pygame.mixer.music.play(-1 if loop else 0)
        except:
            print(f"Failed to load music: {name}")

class Game:
    """Main game class"""
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        pygame.mixer.init()
        
        # Check and install assets if needed
        self.installer = PyDieInstaller()
        if not self.installer.assets_installed:
            if not self.installer.install_assets():
                print("Asset installation failed. Exiting.")
                sys.exit(1)
        
        # Load settings
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.settings
        
        # Set up display
        flags = pygame.DOUBLEBUF | pygame.OPENGL
        if self.settings["fullscreen"]:
            flags |= pygame.FULLSCREEN
            
        pygame.display.set_mode(self.settings["resolution"], flags)
        pygame.display.set_caption(f"{GAME_TITLE} v{VERSION}")
        
        # Set up OpenGL
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_CULL_FACE)
        glShadeModel(GL_SMOOTH)
        
        # Set up perspective
        glViewport(0, 0, self.settings["resolution"][0], self.settings["resolution"][1])
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60.0, self.settings["resolution"][0]/self.settings["resolution"][1], 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        
        # Initialize game systems
        self.audio = AudioManager(self.settings)
        self.player = Player()
        self.environment = Environment()
        self.enemies = []
        self.bullets = []
        self.game_state = "menu"  # menu, playing, paused, game_over
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        
        # Create weapons
        assault_rifle = Weapon(
            name="Assault Rifle",
            damage=25,
            fire_rate=10,
            ammo_capacity=30,
            reload_time=2.5,
            model_path=os.path.join(MODELS_PATH, "rifle_model.obj"),
            texture_path=os.path.join(TEXTURES_PATH, "weapon_texture.png")
        )
        
        shotgun = Weapon(
            name="Shotgun",
            damage=60,
            fire_rate=1.2,
            ammo_capacity=8,
            reload_time=3.0,
            model_path=os.path.join(MODELS_PATH, "shotgun_model.obj"),
            texture_path=os.path.join(TEXTURES_PATH, "weapon_texture.png")
        )
        
        self.player.add_weapon(assault_rifle)
        self.player.add_weapon(shotgun)
        
        # Spawn enemies
        for _ in range(8):
            x = random.uniform(-30, 30)
            z = random.uniform(-30, 30)
            self.enemies.append(Enemy(position=(x, 0, z)))
        
        # Start background music
        self.audio.play_music("ambient")
    
    def handle_events(self):
        """Handle game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == "playing":
                        self.game_state = "paused"
                    elif self.game_state == "paused":
                        self.game_state = "playing"
                    elif self.game_state == "game_over":
                        self.game_state = "menu"
                
                elif event.key == pygame.K_r and self.game_state == "playing":
                    if self.player.current_weapon:
                        self.player.current_weapon.start_reload(pyglet.clock.get_default().time())
                        self.audio.play_sound("reload")
                
                elif event.key == pygame.K_1 and self.game_state == "playing":
                    self.player.switch_weapon(0)
                
                elif event.key == pygame.K_2 and self.game_state == "playing":
                    self.player.switch_weapon(1)
                
                elif event.key == pygame.K_RETURN and self.game_state == "menu":
                    self.start_game()
            
            elif event.type == pygame.MOUSEBUTTONDOWN and self.game_state == "playing":
                if event.button == 1:  # Left mouse button
                    self.fire_weapon()
        
        return True
    
    def fire_weapon(self):
        """Fire the current weapon"""
        if self.player.current_weapon and self.player.current_weapon.fire(pyglet.clock.get_default().time()):
            self.audio.play_sound("gunshot")
            
            # Create a bullet
            self.bullets.append({
                "position": self.player.position[:],
                "direction": [
                    math.sin(math.radians(self.player.rotation[0]) * math.cos(math.radians(self.player.rotation[1])),
                    math.sin(math.radians(self.player.rotation[1])),
                    math.cos(math.radians(self.player.rotation[0])) * math.cos(math.radians(self.player.rotation[1]))
                ],
                "speed": 100.0,
                "damage": self.player.current_weapon.damage,
                "lifetime": 2.0,
                "start_time": pyglet.clock.get_default().time()
            })
    
    def start_game(self):
        """Start a new game"""
        self.player = Player()
        self.enemies = []
        self.bullets = []
        
        # Create weapons
        assault_rifle = Weapon(
            name="Assault Rifle",
            damage=25,
            fire_rate=10,
            ammo_capacity=30,
            reload_time=2.5,
            model_path=os.path.join(MODELS_PATH, "rifle_model.obj"),
            texture_path=os.path.join(TEXTURES_PATH, "weapon_texture.png")
        )
        
        shotgun = Weapon(
            name="Shotgun",
            damage=60,
            fire_rate=1.2,
            ammo_capacity=8,
            reload_time=3.0,
            model_path=os.path.join(MODELS_PATH, "shotgun_model.obj"),
            texture_path=os.path.join(TEXTURES_PATH, "weapon_texture.png")
        )
        
        self.player.add_weapon(assault_rifle)
        self.player.add_weapon(shotgun)
        
        # Spawn enemies
        for _ in range(8):
            x = random.uniform(-30, 30)
            z = random.uniform(-30, 30)
            self.enemies.append(Enemy(position=(x, 0, z)))
        
        self.game_state = "playing"
    
    def update(self, dt):
        """Update game state"""
        if self.game_state != "playing":
            return
            
        # Get keyboard state
        keys = pygame.key.get_pressed()
        
        # Player movement
        direction = [0, 0]
        if keys[pygame.K_w]:
            direction[0] += 1
        if keys[pygame.K_s]:
            direction[0] -= 1
        if keys[pygame.K_a]:
            direction[1] -= 1
        if keys[pygame.K_d]:
            direction[1] += 1
            
        if keys[pygame.K_LSHIFT]:
            self.player.is_sprinting = True
        else:
            self.player.is_sprinting = False
            
        if keys[pygame.K_LCTRL]:
            self.player.is_crouching = True
        else:
            self.player.is_crouching = False
            
        if direction[0] != 0 or direction[1] != 0:
            self.player.move(direction, dt)
            # Play footstep sound occasionally
            if random.random() < 0.1:
                self.audio.play_sound("footstep", volume=0.5)
        
        # Player rotation from mouse
        rel_x, rel_y = pygame.mouse.get_rel()
        sensitivity = self.settings["sensitivity"] / 100.0 * 0.2
        self.player.rotate(rel_x * sensitivity, -rel_y * sensitivity, sensitivity)
        
        # Update player
        self.player.update(dt)
        
        # Update bullets
        current_time = pyglet.clock.get_default().time()
        for bullet in self.bullets[:]:
            # Move bullet
            bullet["position"][0] += bullet["direction"][0] * bullet["speed"] * dt
            bullet["position"][1] += bullet["direction"][1] * bullet["speed"] * dt
            bullet["position"][2] += bullet["direction"][2] * bullet["speed"] * dt
            
            # Check lifetime
            if current_time - bullet["start_time"] > bullet["lifetime"]:
                self.bullets.remove(bullet)
                continue
                
            # Check collision with enemies
            for enemy in self.enemies[:]:
                if enemy.is_alive:
                    dx = bullet["position"][0] - enemy.position[0]
                    dy = bullet["position"][1] - enemy.position[1]
                    dz = bullet["position"][2] - enemy.position[2]
                    distance = math.sqrt(dx*dx + dy*dy + dz*dz)
                    
                    if distance < 1.5:  # Collision radius
                        if enemy.take_damage(bullet["damage"]):
                            self.player.kills += 1
                            self.player.score += 100
                            self.audio.play_sound("death")
                        else:
                            self.audio.play_sound("hurt")
                        self.bullets.remove(bullet)
                        break
        
        # Update enemies
        for enemy in self.enemies[:]:
            if enemy.is_alive:
                damage = enemy.update(dt, self.player.position)
                if damage:
                    if self.player.take_damage(damage):
                        self.audio.play_sound("death")
                        self.player.deaths += 1
                        self.game_state = "game_over"
                    else:
                        self.audio.play_sound("hurt")
        
        # Check win condition
        if all(not enemy.is_alive for enemy in self.enemies):
            self.audio.play_sound("victory")
            self.game_state = "game_over"
    
    def render(self):
        """Render the game scene"""
        # Clear screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        if self.game_state == "playing":
            # Set up camera based on player position and rotation
            glRotatef(self.player.rotation[1], 1, 0, 0)  # Pitch
            glRotatef(self.player.rotation[0], 0, 1, 0)  # Yaw
            glTranslatef(-self.player.position[0], -self.player.position[1], -self.player.position[2])
            
            # Render environment
            self.environment.render()
            
            # Render enemies
            for enemy in self.enemies:
                if enemy.is_alive:
                    glPushMatrix()
                    glTranslatef(enemy.position[0], enemy.position[1], enemy.position[2])
                    glRotatef(enemy.rotation[0], 0, 1, 0)
                    # Render enemy model (simplified)
                    glPopMatrix()
            
            # Render bullets
            for bullet in self.bullets:
                glPushMatrix()
                glTranslatef(bullet["position"][0], bullet["position"][1], bullet["position"][2])
                # Render bullet (simplified)
                glPopMatrix()
            
            # Render HUD
            self.render_hud()
        
        elif self.game_state == "menu":
            self.render_menu()
        
        elif self.game_state == "paused":
            self.render_hud()
            self.render_pause_menu()
        
        elif self.game_state == "game_over":
            self.render_game_over()
        
        pygame.display.flip()
    
    def render_hud(self):
        """Render the heads-up display"""
        # Switch to 2D orthographic projection for HUD
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Disable depth test for HUD
        glDisable(GL_DEPTH_TEST)
        
        # Health bar
        health_width = 200
        health_height = 30
        health_x = 20
        health_y = SCREEN_HEIGHT - 50
        
        # Background
        pygame.draw.rect(pygame.display.get_surface(), (50, 50, 50), 
                         (health_x, health_y, health_width, health_height))
        
        # Health fill
        health_percent = self.player.health / self.player.max_health
        health_fill_width = int(health_width * health_percent)
        health_color = (0, 255, 0) if health_percent > 0.5 else (255, 165, 0) if health_percent > 0.25 else (255, 0, 0)
        pygame.draw.rect(pygame.display.get_surface(), health_color, 
                         (health_x, health_y, health_fill_width, health_height))
        
        # Health text
        health_text = self.font.render(f"Health: {self.player.health}/{self.player.max_health}", True, (255, 255, 255))
        pygame.display.get_surface().blit(health_text, (health_x + 10, health_y + 5))
        
        # Armor bar
        if self.player.armor > 0:
            armor_width = 150
            armor_height = 20
            armor_x = 20
            armor_y = SCREEN_HEIGHT - 80
            
            pygame.draw.rect(pygame.display.get_surface(), (50, 50, 50), 
                             (armor_x, armor_y, armor_width, armor_height))
            
            armor_percent = self.player.armor / self.player.max_armor
            armor_fill_width = int(armor_width * armor_percent)
            pygame.draw.rect(pygame.display.get_surface(), (100, 100, 255), 
                             (armor_x, armor_y, armor_fill_width, armor_height))
            
            armor_text = self.font.render(f"Armor: {self.player.armor}/{self.player.max_armor}", True, (255, 255, 255))
            pygame.display.get_surface().blit(armor_text, (armor_x + 10, armor_y + 2))
        
        # Weapon info
        if self.player.current_weapon:
            weapon_x = SCREEN_WIDTH - 200
            weapon_y = SCREEN_HEIGHT - 50
            
            weapon_text = self.font.render(
                f"{self.player.current_weapon.name}: {self.player.current_weapon.current_ammo}/{self.player.current_weapon.ammo_capacity}", 
                True, (255, 255, 255))
            pygame.display.get_surface().blit(weapon_text, (weapon_x, weapon_y))
            
            if self.player.current_weapon.is_reloading:
                reload_text = self.font.render("RELOADING...", True, (255, 255, 0))
                pygame.display.get_surface().blit(reload_text, (weapon_x, weapon_y - 30))
        
        # Score and kills
        score_text = self.font.render(f"Score: {self.player.score} | Kills: {self.player.kills}", True, (255, 255, 255))
        pygame.display.get_surface().blit(score_text, (20, 20))
        
        # Restore OpenGL state
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
    
    def render_menu(self):
        """Render the main menu"""
        surface = pygame.display.get_surface()
        surface.fill((30, 30, 50))
        
        # Title
        title_font = pygame.font.SysFont("Arial", 72, bold=True)
        title = title_font.render("PYDIE", True, (200, 30, 30))
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
        
        subtitle_font = pygame.font.SysFont("Arial", 36)
        subtitle = subtitle_font.render("Tactical Warfare", True, (200, 200, 200))
        surface.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 230))
        
        # Menu options
        menu_font = pygame.font.SysFont("Arial", 48)
        play_text = menu_font.render("PLAY GAME", True, (255, 255, 255))
        settings_text = menu_font.render("SETTINGS", True, (200, 200, 200))
        quit_text = menu_font.render("QUIT", True, (200, 200, 200))
        
        surface.blit(play_text, (SCREEN_WIDTH//2 - play_text.get_width()//2, 350))
        surface.blit(settings_text, (SCREEN_WIDTH//2 - settings_text.get_width()//2, 420))
        surface.blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2, 490))
        
        # Version info
        version_text = self.font.render(f"Version {VERSION}", True, (150, 150, 150))
        surface.blit(version_text, (SCREEN_WIDTH - version_text.get_width() - 20, SCREEN_HEIGHT - 30))
    
    def render_pause_menu(self):
        """Render the pause menu overlay"""
        # Darken the game view
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        pygame.display.get_surface().blit(overlay, (0, 0))
        
        # Pause text
        pause_font = pygame.font.SysFont("Arial", 72, bold=True)
        pause_text = pause_font.render("PAUSED", True, (255, 255, 255))
        pygame.display.get_surface().blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, 200))
        
        # Menu options
        menu_font = pygame.font.SysFont("Arial", 48)
        resume_text = menu_font.render("RESUME (ESC)", True, (255, 255, 255))
        settings_text = menu_font.render("SETTINGS", True, (200, 200, 200))
        quit_text = menu_font.render("QUIT TO MENU", True, (200, 200, 200))
        
        pygame.display.get_surface().blit(resume_text, (SCREEN_WIDTH//2 - resume_text.get_width()//2, 350))
        pygame.display.get_surface().blit(settings_text, (SCREEN_WIDTH//2 - settings_text.get_width()//2, 420))
        pygame.display.get_surface().blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2, 490))
    
    def render_game_over(self):
        """Render the game over screen"""
        surface = pygame.display.get_surface()
        surface.fill((20, 20, 30))
        
        # Game over text
        title_font = pygame.font.SysFont("Arial", 72, bold=True)
        if all(not enemy.is_alive for enemy in self.enemies):
            title = title_font.render("VICTORY!", True, (50, 200, 50))
        else:
            title = title_font.render("MISSION FAILED", True, (200, 50, 50))
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
        
        # Stats
        stats_font = pygame.font.SysFont("Arial", 36)
        score_text = stats_font.render(f"Score: {self.player.score}", True, (255, 255, 255))
        kills_text = stats_font.render(f"Kills: {self.player.kills}", True, (255, 255, 255))
        deaths_text = stats_font.render(f"Deaths: {self.player.deaths}", True, (255, 255, 255))
        
        surface.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 250))
        surface.blit(kills_text, (SCREEN_WIDTH//2 - kills_text.get_width()//2, 300))
        surface.blit(deaths_text, (SCREEN_WIDTH//2 - deaths_text.get_width()//2, 350))
        
        # Menu options
        menu_font = pygame.font.SysFont("Arial", 48)
        retry_text = menu_font.render("RETRY MISSION", True, (255, 255, 255))
        menu_text = menu_font.render("MAIN MENU (ESC)", True, (200, 200, 200))
        quit_text = menu_font.render("QUIT", True, (200, 200, 200))
        
        surface.blit(retry_text, (SCREEN_WIDTH//2 - retry_text.get_width()//2, 450))
        surface.blit(menu_text, (SCREEN_WIDTH//2 - menu_text.get_width()//2, 520))
        surface.blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2, 590))
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0  # Convert to seconds
            
            # Handle events
            running = self.handle_events()
            
            # Update game state
            self.update(dt)
            
            # Render game
            self.render()
            
        pygame.quit()
        sys.exit()

def create_installer():
    """Create an installer for the game (simplified)"""
    print("Creating PyDie installer...")
    
    # Create directories
    os.makedirs("dist", exist_ok=True)
    os.makedirs("installer", exist_ok=True)
    
    # Create setup script (simplified)
    with open("installer/setup.py", "w") as f:
        f.write("import os\n")
        f.write("import sys\n")
        f.write("import subprocess\n")
        f.write("from PyInstaller.__main__ import run\n\n")
        f.write("def main():\n")
        f.write("    # Package the game\n")
        f.write("    args = [\n")
        f.write("        '--name=PyDie',\n")
        f.write("        '--onefile',\n")
        f.write("        '--windowed',\n")
        f.write("        '--add-data=textures;textures',\n")
        f.write("        '--add-data=models;models',\n")
        f.write("        '--add-data=sounds;sounds',\n")
        f.write("        '--icon=icon.ico',\n")
        f.write("        'pydie_game.py'\n")
        f.write("    ]\n")
        f.write("    run(args)\n\n")
        f.write("if __name__ == '__main__':\n")
        f.write("    main()\n")
    
    print("Installer script created. Run 'python installer/setup.py' to create the executable.")
    print("Note: You'll need PyInstaller installed to create the executable.")

if __name__ == "__main__":
    # Check if we're creating an installer or running the game
    if len(sys.argv) > 1 and sys.argv[1] == "--create-installer":
        create_installer()
    else:
        game = Game()
        game.run()