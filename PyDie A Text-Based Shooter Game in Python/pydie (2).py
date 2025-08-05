import pygame
import pyglet
from pyglet.gl import *
from OpenGL.GLU import * # Import GLU functions
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
# Changed to be more flexible for responsive design,
# but still provide initial values.
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


# --- OpenGL Text Rendering ---
# Function to render text using Pygame's font module and then converting it to an OpenGL texture
# This is a common approach when mixing Pygame and OpenGL, as direct blitting won't work with OpenGL context.
def render_text_opengl(text, font_name, font_size, text_color):
    font = pygame.font.SysFont(font_name, font_size)
    text_surface = font.render(text, True, text_color)
    text_data = pygame.image.tostring(text_surface, "RGBA", True)

    width, height = text_surface.get_width(), text_surface.get_height()

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    return texture_id, width, height

# Function to draw the OpenGL texture
def draw_text_opengl(texture_id, width, height, x, y):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glPushMatrix()
    glTranslatef(x, y, 0)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(0, 0)
    glTexCoord2f(1, 0); glVertex2f(width, 0)
    glTexCoord2f(1, 1); glVertex2f(width, height)
    glTexCoord2f(0, 1); glVertex2f(0, height)
    glEnd()
    glPopMatrix()
    glDisable(GL_TEXTURE_2D)
    glDeleteTextures(1, [texture_id]) # Delete the texture after use to free up memory


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

            print("Assets installed successfully!")
            self.assets_installed = True
        except Exception as e:
            print(f"Error installing assets: {e}")


class Player:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.rotation_y = 0  # Horizontal rotation
        self.rotation_x = 0  # Vertical rotation (for looking up/down)
        self.health = 100
        self.ammo = 30
        self.speed = 0.1
        self.mouse_sensitivity = 0.1
        self.is_sprinting = False


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(GAME_TITLE)

        # Initialize screen with RESIZABLE flag for responsive design
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL | RESIZABLE)
        self.set_perspective(SCREEN_WIDTH, SCREEN_HEIGHT)

        self.clock = pygame.time.Clock()
        self.player = Player()
        self.installer = PyDieInstaller()
        self.running = True

        # Ensure relative mouse motion for FPS control
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)

        # Colors for HUD
        self.white = (255, 255, 255)
        self.red = (255, 0, 0)

    def set_perspective(self, width, height):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(70, (width / height), 0.1, 100.0) # Adjust FOV for aspect ratio
        glMatrixMode(GL_MODELVIEW)
        glViewport(0, 0, width, height) # Adjust viewport to new window size

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resizing for responsive design
                self.set_perspective(event.w, event.h)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_LSHIFT:
                    self.player.is_sprinting = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT:
                    self.player.is_sprinting = False
            elif event.type == pygame.MOUSEMOTION:
                # Get relative mouse movement for camera control
                mouse_dx, mouse_dy = pygame.mouse.get_rel()
                self.player.rotation_y += mouse_dx * self.player.mouse_sensitivity
                self.player.rotation_x += mouse_dy * self.player.mouse_sensitivity
                # Clamp vertical rotation to prevent flipping
                self.player.rotation_x = max(-90, min(90, self.player.rotation_x))

        keys = pygame.key.get_pressed()
        current_speed = self.player.speed * (1.5 if self.player.is_sprinting else 1) # Sprinting

        if keys[K_w]:
            self.player.x -= math.sin(math.radians(self.player.rotation_y)) * current_speed
            self.player.z += math.cos(math.radians(self.player.rotation_y)) * current_speed
        if keys[K_s]:
            self.player.x += math.sin(math.radians(self.player.rotation_y)) * current_speed
            self.player.z -= math.cos(math.radians(self.player.rotation_y)) * current_speed
        if keys[K_a]:
            self.player.x += math.sin(math.radians(self.player.rotation_y - 90)) * current_speed
            self.player.z -= math.cos(math.radians(self.player.rotation_y - 90)) * current_speed
        if keys[K_d]:
            self.player.x += math.sin(math.radians(self.player.rotation_y + 90)) * current_speed
            self.player.z -= math.cos(math.radians(self.player.rotation_y + 90)) * current_speed

    def update(self):
        pass # Game logic updates will go here

    def draw_hud(self):
        # Setup for 2D rendering (orthographic projection for HUD)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        # Use current screen dimensions for orthographic projection for responsive HUD
        current_width, current_height = self.screen.get_size()
        gluOrtho2D(0, current_width, 0, current_height)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST) # Disable depth test for HUD to always draw on top

        # Draw crosshair
        crosshair_size = 20
        crosshair_thickness = 2
        center_x, center_y = current_width / 2, current_height / 2

        glColor3f(1.0, 1.0, 1.0) # White color for crosshair
        glBegin(GL_LINES)
        # Horizontal line
        glVertex2f(center_x - crosshair_size / 2, center_y)
        glVertex2f(center_x + crosshair_size / 2, center_y)
        # Vertical line
        glVertex2f(center_x, center_y - crosshair_size / 2)
        glVertex2f(center_x, center_y + crosshair_size / 2)
        glEnd()

        # Draw Health and Ammo text using OpenGL-compatible rendering
        # Position the text relative to the screen dimensions for responsive design
        health_text = f"Health: {self.player.health}"
        ammo_text = f"Ammo: {self.player.ammo}"

        # Render health text
        health_texture, health_width, health_height = render_text_opengl(health_text, "Arial", 30, self.white)
        draw_text_opengl(health_texture, health_width, health_height, 10, current_height - health_height - 10)

        # Render ammo text
        ammo_texture, ammo_width, ammo_height = render_text_opengl(ammo_text, "Arial", 30, self.white)
        draw_text_opengl(ammo_texture, ammo_width, ammo_height, current_width - ammo_width - 10, current_height - ammo_height - 10)


        glEnable(GL_DEPTH_TEST) # Re-enable depth test for 3D scene
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW) # Return to modelview matrix for 3D rendering


    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Apply camera transformations
        glRotatef(self.player.rotation_x, 1, 0, 0) # Apply vertical rotation
        glRotatef(self.player.rotation_y, 0, 1, 0) # Apply horizontal rotation
        glTranslatef(-self.player.x, -self.player.y, -self.player.z)

        # Draw a simple ground plane (for testing)
        glBegin(GL_QUADS)
        glColor3f(0.2, 0.8, 0.2) # Green color
        glVertex3f(-5.0, -1.0, -5.0)
        glVertex3f( 5.0, -1.0, -5.0)
        glVertex3f( 5.0, -1.0,  5.0)
        glVertex3f(-5.0, -1.0,  5.0)
        glEnd()

        # Draw a simple cube (for testing)
        glBegin(GL_QUADS)
        glColor3f(1.0, 0.0, 0.0) # Red
        glVertex3f( 0.5, 0.5, -0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f( 0.5, -0.5, -0.5)

        glColor3f(0.0, 1.0, 0.0) # Green
        glVertex3f( 0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f( 0.5, -0.5, 0.5)

        glColor3f(0.0, 0.0, 1.0) # Blue
        glVertex3f( 0.5, 0.5, -0.5)
        glVertex3f( 0.5, 0.5, 0.5)
        glVertex3f( 0.5, -0.5, 0.5)
        glVertex3f( 0.5, -0.5, -0.5)

        glColor3f(1.0, 1.0, 0.0) # Yellow
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(-0.5, -0.5, -0.5)

        glColor3f(0.0, 1.0, 1.0) # Cyan
        glVertex3f( 0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f( 0.5, 0.5, -0.5)

        glColor3f(1.0, 0.0, 1.0) # Magenta
        glVertex3f( 0.5, -0.5, 0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f( 0.5, -0.5, -0.5)
        glEnd()

        self.draw_hud() # Draw HUD after 3D scene

        pygame.display.flip()

    def run(self):
        # Removed pyglet.clock.get_default().time() which is not needed with pygame.time.Clock()
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS) # Control frame rate


if __name__ == '__main__':
    game = Game()
    game.run()