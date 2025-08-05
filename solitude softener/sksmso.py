import pygame
import sys
import math
import random
from datetime import datetime
import json
from pygame import gfxdraw
import os

# Initialize pygame
pygame.init()

# Screen dimensions (initial reduced size)
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Solitude Softener Digital World")

# Colors
DEEP_PURPLE = (26, 6, 54)
DRAGON_VIOLET = (77, 26, 127)
MOON_GLOW = (224, 214, 240)
DRAGON_BLOOD = (138, 3, 3)
SOFT_CYAN = (135, 197, 196)
STONE_GRAY = (138, 141, 147)
BACKGROUND = (10, 3, 26)
UI_PANEL_COLOR = (30, 10, 60) # A darker shade for UI panels

# Fonts (will be dynamically sized)
def get_responsive_font_size(base_size, height):
    return int(base_size * (height / 600)) # Base on new HEIGHT

title_font = None
header_font = None
body_font = None
small_font = None
tiny_font = None # New smaller font for journal details

def update_fonts(height):
    global title_font, header_font, body_font, small_font, tiny_font
    title_font = pygame.font.Font(None, get_responsive_font_size(48, height))
    header_font = pygame.font.Font(None, get_responsive_font_size(36, height))
    body_font = pygame.font.Font(None, get_responsive_font_size(24, height))
    small_font = pygame.font.Font(None, get_responsive_font_size(18, height))
    tiny_font = pygame.font.Font(None, get_responsive_font_size(14, height))

update_fonts(HEIGHT) # Initialize fonts

# Fragment database (initial load, more can be discovered)
initial_fragments = [
    {
        "id": 1042,
        "source": "User @Ghost_1042 (2016)",
        "content": "'Left a sonnet in a payphone receiver. Verse 3 was hope. The rest was salt. — May it dissolve someone's rust.'",
        "footnote": "This fragment now lives in 3 places: 1. Your stone 2. A café wall in Marrakesh 3. The dreams of whoever hung up that phone."
    },
    {
        "id": 1984,
        "source": "Geocaching forum thread from 2013",
        "content": "'Stumbled upon this bus stop behind the old textile mill. Bench is cracked, timetable faded to ghosts. Felt like if I sat down, I'd be waiting for a bus that comes once every decade. Left a blue pebble under the third plank — a ticket for the next dreamer.'",
        "footnote": "• Last detected location: Kyoto train station printer (2024-05-22) • ⊙ 12,447 fragments archived"
    },
    {
        "id": 711,
        "source": "User @Ghost_711 (2009)",
        "content": "'Left my fear in a hotel Bible. Room 407. May it bless the next liar.'",
        "footnote": "• Fragment delivered to 3 keepers • Dragon's blood sedum planted in Oslo and Lisbon"
    },
    {
        "id": 22,
        "source": "User @Ghost_22 (2010)",
        "content": "'Left maple seeds on a cemetery wall. Note: For the buried hearts still learning to fly.'",
        "footnote": "• Last detected location: Seattle Public Library • ⊙ Currently blooming in 7 Crest gardens"
    }
]

# Dream fragment pool (for discovery)
dream_fragment_pool = [
    {
        "type": "dream",
        "title": "Whispers of the Deep",
        "content": "A melody, unheard yet felt, drifts from the forgotten well. It hums of ancient stones and the patience of the earth.",
        "date": "" # Date added dynamically
    },
    {
        "type": "dream",
        "title": "Echoes in the Stone",
        "content": "The Crest hummed with a low vibration, revealing a brief, shimmering vision of a shadow dragon stretching its wings across a desolate plain. A sense of weary pride lingered.",
        "date": ""
    },
    {
        "type": "dream",
        "title": "Moonlit Revelation",
        "content": "Under the silver gaze of a crescent moon, a hidden path unwound in the mind's eye. It led to a garden where fear bloomed into resilience.",
        "date": ""
    },
    {
        "type": "dream",
        "title": "Scent of Bloom",
        "content": "A faint, sweet fragrance of sedum, carried on a phantom breeze, filled the space. A reminder that even in barren lands, life finds a way.",
        "date": ""
    },
    {
        "type": "dream",
        "title": "The Weaver's Hand",
        "content": "A fleeting image: countless threads, some dark, some shimmering, being woven into an intricate tapestry. Every fragment, a single knot.",
        "date": ""
    },
    {
        "type": "dream",
        "title": "A Silent Promise",
        "content": "The silence spoke of promises kept, of burdens eased, and of the quiet strength found in knowing you are connected to something larger.",
        "date": ""
    }
]

# Helper function to wrap text
def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = []
    current_line_width = 0
    space_width = font.size(' ')[0]

    for word in words:
        word_width = font.size(word)[0]
        if current_line_width + word_width + (space_width if current_line else 0) <= max_width:
            current_line.append(word)
            current_line_width += word_width + (space_width if current_line else 0)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_line_width = word_width
    if current_line:
        lines.append(' '.join(current_line))
    return lines

# Particle system for ethereal effects
class Particle:
    def __init__(self, x, y, color, size, velocity, lifespan, type="default"):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.velocity = velocity # (vx, vy)
        self.lifespan = lifespan
        self.current_life = lifespan
        self.type = type # "default", "wisp", "ember", "essence"

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.current_life -= 1
        return self.current_life <= 0

    def draw(self, surface):
        alpha = int(255 * (self.current_life / self.lifespan))
        if alpha < 0: alpha = 0
        draw_color = self.color[:3] + (alpha,)

        if self.type == "wisp":
            # Draw as a blurred circle or elongated shape
            gfxdraw.aacircle(surface, int(self.x), int(self.y), int(self.size), draw_color)
            gfxdraw.filled_circle(surface, int(self.x), int(self.y), int(self.size), draw_color)
        elif self.type == "ember":
            # Draw as a small, square-ish spark
            pygame.draw.rect(surface, draw_color, (int(self.x - self.size/2), int(self.y - self.size/2), self.size, self.size))
        elif self.type == "essence":
            # Draw as a soft, slightly larger circle
            gfxdraw.aacircle(surface, int(self.x), int(self.y), int(self.size), draw_color)
            gfxdraw.filled_circle(surface, int(self.x), int(self.y), int(self.size), draw_color)
        else: # Default
            pygame.draw.circle(surface, draw_color, (int(self.x), int(self.y)), int(self.size))

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, count, color, min_size, max_size, min_speed, max_speed, min_lifespan, max_lifespan, angle_range=(-math.pi, math.pi), type="default"):
        for _ in range(count):
            size = random.uniform(min_size, max_size)
            speed = random.uniform(min_speed, max_speed)
            angle = random.uniform(angle_range[0], angle_range[1])
            velocity = (speed * math.cos(angle), speed * math.sin(angle))
            lifespan = random.randint(min_lifespan, max_lifespan)
            self.particles.append(Particle(x, y, color, size, velocity, lifespan, type))

    def update(self):
        self.particles = [p for p in self.particles if not p.update()]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

# Moon phase simulation
class MoonPhase:
    def __init__(self):
        self.phase = 0  # 0-1 representing moon phase
        self.speed = 0.001
        self.illumination = 0.18
        self.phase_name = "Waxing Crescent"
        self.last_update = pygame.time.get_ticks()
        
    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > 100:  # Update every 100ms
            self.phase = (self.phase + self.speed) % 1
            self.last_update = current_time
            
            # Update illumination and phase name based on phase
            if self.phase < 0.125:
                self.phase_name = "New Moon"
                self.illumination = 0.0
            elif self.phase < 0.25:
                self.phase_name = "Waxing Crescent"
                self.illumination = (self.phase - 0.125) * 8
            elif self.phase < 0.375:
                self.phase_name = "First Quarter"
                self.illumination = 0.5
            elif self.phase < 0.5:
                self.phase_name = "Waxing Gibbous"
                self.illumination = 0.5 + (self.phase - 0.375) * 8
            elif self.phase < 0.625:
                self.phase_name = "Full Moon"
                self.illumination = 1.0
            elif self.phase < 0.75:
                self.phase_name = "Waning Gibbous"
                self.illumination = 1.0 - (self.phase - 0.625) * 8
            elif self.phase < 0.875:
                self.phase_name = "Last Quarter"
                self.illumination = 0.5
            else:
                self.phase_name = "Waning Crescent"
                self.illumination = 0.5 - (self.phase - 0.875) * 8
                
    def is_crescent(self):
        return "Crescent" in self.phase_name
    
    def draw(self, surface, rect):
        x, y, size = rect.center[0], rect.center[1], rect.width // 2

        # Draw moon
        pygame.draw.circle(surface, STONE_GRAY, (x, y), size)
        
        # Draw illuminated part based on phase
        if self.phase < 0.5:  # Waxing phases
            # Draw crescent on the right
            radius = int(size * (1 - self.illumination))
            if radius < size:
                pygame.draw.circle(surface, DEEP_PURPLE, (x - size + radius, y), radius)
        else:  # Waning phases
            # Draw crescent on the left
            radius = int(size * (1 - self.illumination))
            if radius < size:
                pygame.draw.circle(surface, DEEP_PURPLE, (x + size - radius, y), radius)
        
        # Draw glow
        for i in range(1, max(2, int(size // 15))):
            alpha = int(100 - i * 30 * (size/80)) # Scale alpha decay with moon size
            if alpha < 0: alpha = 0
            glow_size = size + i * max(1, int(5 * (size/80)))
            glow_surf = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
            gfxdraw.aacircle(glow_surf, glow_size, glow_size, glow_size - 1, (*MOON_GLOW, alpha))
            gfxdraw.filled_circle(glow_surf, glow_size, glow_size, glow_size - 1, (*MOON_GLOW, alpha // 2))
            surface.blit(glow_surf, (x - glow_size, y - glow_size))

# Shadow Dragons Crest
class DragonsCrest:
    def __init__(self):
        self.keystone_heat = 0.5  # 0-1, how warm the keystone is
        self.sedum_level = 0.3  # 0-1, growth level
        self.last_tended = datetime.now()
        self.fragments_sent = 0
        self.connected_keepers = ["Lisbon", "Oslo", "Kyoto", "Toronto"]
        
    def tend(self):
        self.keystone_heat = min(1.0, self.keystone_heat + 0.1)
        self.sedum_level = min(1.0, self.sedum_level + 0.05)
        self.last_tended = datetime.now()
        
    def update(self):
        # Gradually cool the keystone
        self.keystone_heat = max(0.3, self.keystone_heat - 0.0001)
        
        # Sedum grows slowly
        self.sedum_level = min(1.0, self.sedum_level + 0.00002)
        
    def draw(self, surface, rect):
        x, y, width, height = rect.x, rect.y, rect.width, rect.height

        # Draw brick wall background
        brick_width = max(5, int(width / 15))
        brick_height = max(3, int(height / 12))
        
        for row in range(height // brick_height + 1):
            for col in range(width // brick_width + 1):
                offset = 0 if row % 2 == 0 else brick_width // 2
                brick_rect = pygame.Rect(
                    x + col * brick_width - offset,
                    y + row * brick_height,
                    brick_width - 1, # Smaller gap
                    brick_height - 1  # Smaller gap
                )
                pygame.draw.rect(surface, (80, 30, 50), brick_rect)
                pygame.draw.rect(surface, (60, 20, 40), brick_rect, 1)
        
        # Draw the crest
        crest_width = width * 0.6
        crest_height = height * 0.8
        crest_rect = pygame.Rect(
            x + (width - crest_width) / 2,
            y + (height - crest_height) / 2,
            crest_width,
            crest_height
        )
        
        # Draw crest with gradient based on heat
        heat_color = (
            int(DRAGON_BLOOD[0] * self.keystone_heat),
            int(DRAGON_BLOOD[1] * self.keystone_heat),
            int(DRAGON_BLOOD[2] * self.keystone_heat)
        )
        
        pygame.draw.rect(surface, heat_color, crest_rect, border_radius=int(10 * (width/250))) # Scaled border radius
        
        # Draw dragon scale pattern
        scale_size = max(3, int(10 * (width/250))) # Smaller scales for smaller window
        for row in range(int(crest_height // scale_size)):
            for col in range(int(crest_width // scale_size)):
                scale_x = crest_rect.left + col * scale_size + (row % 2) * scale_size/2
                scale_y = crest_rect.top + row * scale_size
                
                if random.random() > 0.3:  # Draw only some scales
                    pygame.draw.circle(
                        surface, 
                        (int(heat_color[0]*0.8), int(heat_color[1]*0.8), int(heat_color[2]*0.8)),
                        (int(scale_x), int(scale_y)),
                        max(1, scale_size//3)
                    )
        
        # Draw sedum plants
        plant_height = int((15 + self.sedum_level * 25) * (height/200)) # Scaled plant height
        for i in range(5):
            plant_x = crest_rect.left + i * crest_width//4
            plant_y = crest_rect.bottom - plant_height
            
            # Stem
            pygame.draw.line(
                surface, 
                (50, 120, 50),
                (int(plant_x), int(plant_y)),
                (int(plant_x), int(plant_y + plant_height)),
                max(1, int(2 * (width/250))) # Scaled stem thickness
            )
            
            # Flowers
            for j in range(3):
                flower_size = max(2, int((3 + j*2) * (width/250))) # Scaled flower size
                pygame.draw.circle(
                    surface, 
                    DRAGON_BLOOD,
                    (int(plant_x), int(plant_y - j*8 * (height/200))), # Scaled flower vertical spacing
                    flower_size
                )

# Fragment viewer
class FragmentViewer:
    def __init__(self, fragments):
        self.fragments = fragments # This will be updated with discovered fragments
        self.current_fragment = 0
        self.last_change = 0
        self.display_duration = 10000  # 10 seconds per fragment
        self.new_fragment_flash_time = 0
        self.flash_duration = 500 # ms for flash effect

    def add_fragment(self, new_frag):
        self.fragments.append(new_frag)
        self.current_fragment = len(self.fragments) - 1 # Switch to new fragment
        self.last_change = pygame.time.get_ticks()
        self.new_fragment_flash_time = pygame.time.get_ticks()

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_change > self.display_duration:
            self.current_fragment = (self.current_fragment + 1) % len(self.fragments)
            self.last_change = current_time
            
    def draw(self, surface, rect):
        x, y, width, height = rect.x, rect.y, rect.width, rect.height
        
        # Draw container
        pygame.draw.rect(surface, UI_PANEL_COLOR, (x, y, width, height), border_radius=int(10 * (width/550)))
        pygame.draw.rect(surface, SOFT_CYAN, (x, y, width, max(1, int(3 * (height/225)))))
        
        # Flash effect for new fragment
        if pygame.time.get_ticks() - self.new_fragment_flash_time < self.flash_duration:
            flash_alpha = int(255 * (1 - (pygame.time.get_ticks() - self.new_fragment_flash_time) / self.flash_duration))
            flash_surf = pygame.Surface((width, height), pygame.SRCALPHA)
            flash_surf.fill((255, 255, 255, flash_alpha // 2)) # White flash
            surface.blit(flash_surf, (x, y))

        # Draw fragment info
        frag = self.fragments[self.current_fragment]
        
        padding_x = width * 0.04
        padding_y_top = height * 0.07
        content_start_y_ratio = 0.25

        id_text_surf = header_font.render(f"⊚ FRAGMENT #{frag['id']}", True, SOFT_CYAN)
        source_text_surf = small_font.render(f"Source: {frag['source']}", True, MOON_GLOW)
        
        max_source_width = width - id_text_surf.get_width() - 3 * padding_x
        if source_text_surf.get_width() > max_source_width:
            source_text_raw = frag['source']
            while source_text_surf.get_width() > max_source_width and len(source_text_raw) > 5:
                source_text_raw = source_text_raw[:-5] + "..."
                source_text_surf = small_font.render(f"Source: {source_text_raw}", True, MOON_GLOW)
            if len(source_text_raw) <= 5:
                source_text_surf = small_font.render("Source:...", True, MOON_GLOW)

        surface.blit(id_text_surf, (x + padding_x, y + padding_y_top))
        surface.blit(source_text_surf, (x + width - source_text_surf.get_width() - padding_x, y + padding_y_top + (header_font.get_height() - source_text_surf.get_height())/2))
        
        content_lines = wrap_text(frag['content'], body_font, width * 0.92)
        current_content_y = y + height * content_start_y_ratio
        for line in content_lines:
            content_surf = body_font.render(line, True, MOON_GLOW)
            surface.blit(content_surf, (x + padding_x, current_content_y))
            current_content_y += body_font.get_height() + (height * 0.005)
        
        footnote_lines = wrap_text(frag['footnote'], small_font, width * 0.92)
        footnote_start_y = y + height - (len(footnote_lines) * small_font.get_height()) - padding_y_top
        for i, line in enumerate(footnote_lines):
            footnote_surf = small_font.render(line, True, (180, 180, 200))
            surface.blit(footnote_surf, (x + padding_x, footnote_start_y + i * small_font.get_height()))

# Dream Journal
class DreamJournal:
    def __init__(self):
        self.entries = []
        self.scroll_offset = 0 # For scrolling through entries
        self.entry_height_base = 0.15 # % of panel height for each entry
        self.max_scroll_offset = 0

    def add_entry(self, entry):
        entry["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.entries.insert(0, entry) # Add newest entry to top
        self.calculate_max_scroll(HEIGHT) # Recalculate max scroll

    def calculate_max_scroll(self, panel_height):
        # Calculate total height of all entries
        total_content_height = 0
        for entry in self.entries:
            title_height = small_font.get_height()
            content_lines = wrap_text(entry['content'], tiny_font, WIDTH * 0.4) # Approx content width
            content_height = len(content_lines) * tiny_font.get_height()
            total_content_height += title_height + content_height + (HEIGHT * 0.02) # Title + Content + padding

        if total_content_height > panel_height * 0.9: # If content exceeds viewable area
            self.max_scroll_offset = total_content_height - (panel_height * 0.9) # Adjust for padding
        else:
            self.max_scroll_offset = 0
        self.scroll_offset = min(self.scroll_offset, self.max_scroll_offset) # Ensure offset doesn't exceed max
        self.scroll_offset = max(0, self.scroll_offset) # Ensure offset isn't negative

    def scroll(self, amount):
        self.scroll_offset += amount
        self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll_offset))
        
    def draw(self, surface, rect):
        x, y, width, height = rect.x, rect.y, rect.width, rect.height

        # Draw container
        pygame.draw.rect(surface, UI_PANEL_COLOR, (x, y, width, height), border_radius=int(10 * (width/550)))
        pygame.draw.rect(surface, DRAGON_VIOLET, (x, y, width, max(1, int(3 * (height/225)))))

        journal_title = header_font.render("Dream Journal", True, MOON_GLOW)
        surface.blit(journal_title, (x + width * 0.05, y + height * 0.05))

        # Create a sub-surface for scrollable content
        content_area_rect = pygame.Rect(x + width * 0.03, y + height * 0.15, width * 0.94, height * 0.8)
        content_surface = pygame.Surface((content_area_rect.width, int(self.max_scroll_offset + content_area_rect.height)), pygame.SRCALPHA)
        content_surface.fill((0,0,0,0)) # Transparent background

        current_y_in_surface = 0
        for entry in self.entries:
            title_surf = small_font.render(entry['title'], True, SOFT_CYAN)
            date_surf = tiny_font.render(entry['date'], True, (150, 150, 180))
            
            content_lines = wrap_text(entry['content'], tiny_font, content_area_rect.width * 0.95)
            
            # Draw title and date
            content_surface.blit(title_surf, (content_area_rect.width * 0.02, current_y_in_surface))
            content_surface.blit(date_surf, (content_area_rect.width * 0.02, current_y_in_surface + small_font.get_height()))
            current_y_in_surface += small_font.get_height() + tiny_font.get_height() + (height * 0.005)

            # Draw content
            for line in content_lines:
                line_surf = tiny_font.render(line, True, MOON_GLOW)
                content_surface.blit(line_surf, (content_area_rect.width * 0.02, current_y_in_surface))
                current_y_in_surface += tiny_font.get_height() + (height * 0.002)
            
            current_y_in_surface += (height * 0.02) # Spacing between entries
            
        # Blit the scrolled content onto the main screen
        surface.blit(content_surface, content_area_rect.topleft, (0, int(self.scroll_offset), content_area_rect.width, content_area_rect.height))

        # Draw scrollbar
        if self.max_scroll_offset > 0:
            scrollbar_height = content_area_rect.height * (content_area_rect.height / (self.max_scroll_offset + content_area_rect.height))
            scrollbar_y = content_area_rect.y + (self.scroll_offset / self.max_scroll_offset) * (content_area_rect.height - scrollbar_height)
            scrollbar_rect = pygame.Rect(content_area_rect.right + width * 0.01, int(scrollbar_y), max(3, int(width * 0.01)), int(scrollbar_height))
            pygame.draw.rect(surface, STONE_GRAY, scrollbar_rect, border_radius=2)


# Button class for UI
class Button:
    def __init__(self, x_ratio, y_ratio, width_ratio, height_ratio, text, color=MOON_GLOW, hover_color=SOFT_CYAN, active_color=DRAGON_BLOOD):
        self.x_ratio = x_ratio
        self.y_ratio = y_ratio
        self.width_ratio = width_ratio
        self.height_ratio = height_ratio
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.active_color = active_color # New for click feedback
        self.is_hovered = False
        self.is_clicked = False # For visual click feedback
        self.click_time = 0
        self.click_duration = 150 # ms for flash effect
        self.rect = self.get_rect(WIDTH, HEIGHT) # Initial rect
        
    def get_rect(self, current_width, current_height):
        return pygame.Rect(
            current_width * self.x_ratio,
            current_height * self.y_ratio,
            current_width * self.width_ratio,
            current_height * self.height_ratio
        )

    def draw(self, surface, current_width, current_height):
        self.rect = self.get_rect(current_width, current_height)
        
        current_fill_color = DEEP_PURPLE
        current_border_color = self.color

        if self.is_clicked and pygame.time.get_ticks() - self.click_time < self.click_duration:
            current_border_color = self.active_color # Flash active color on click
            pulsate_alpha = int(255 * (1 - (pygame.time.get_ticks() - self.click_time) / self.click_duration))
            # Draw a subtle pulsating glow behind the button
            glow_surf = pygame.Surface((self.rect.width + 10, self.rect.height + 10), pygame.SRCALPHA)
            glow_surf.fill((0,0,0,0)) # Transparent
            gfxdraw.aacircle(glow_surf, glow_surf.get_width()//2, glow_surf.get_height()//2, self.rect.width//2 + 2, (*self.active_color, pulsate_alpha))
            surface.blit(glow_surf, (self.rect.x - 5, self.rect.y - 5))

        elif self.is_hovered:
            current_border_color = self.hover_color
            
        pygame.draw.rect(surface, current_fill_color, self.rect, border_radius=int(5 * (current_width/900)))
        pygame.draw.rect(surface, current_border_color, self.rect, max(1, int(2 * (current_width/900))), border_radius=int(5 * (current_width/900)))
        
        text_surf = body_font.render(self.text, True, current_border_color) # Text color matches border
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def check_click(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                self.is_clicked = True
                self.click_time = pygame.time.get_ticks()
                return True
        return False

# Tooltip class
class Tooltip:
    def __init__(self):
        self.text_lines = []
        self.target_rect = None
        self.is_visible = False
        self.offset_y = 10
        self.last_mouse_pos = (0,0)

    def show(self, text, target_rect, mouse_pos):
        self.text_lines = wrap_text(text, tiny_font, 200) # Max width for tooltip text
        self.target_rect = target_rect
        self.is_visible = True
        self.last_mouse_pos = mouse_pos

    def hide(self):
        self.is_visible = False

    def draw(self, surface):
        if not self.is_visible or not self.text_lines:
            return

        # Calculate tooltip dimensions
        max_line_width = 0
        total_height = 0
        for line in self.text_lines:
            line_w, line_h = tiny_font.size(line)
            max_line_width = max(max_line_width, line_w)
            total_height += line_h

        padding = 5
        tooltip_width = max_line_width + padding * 2
        tooltip_height = total_height + padding * 2

        # Position tooltip above the mouse cursor
        tooltip_x = self.last_mouse_pos[0] - tooltip_width // 2
        tooltip_y = self.last_mouse_pos[1] - tooltip_height - self.offset_y

        # Keep tooltip on screen
        tooltip_x = max(0, min(tooltip_x, WIDTH - tooltip_width))
        tooltip_y = max(0, min(tooltip_y, HEIGHT - tooltip_height))

        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)

        # Draw background with rounded corners
        pygame.draw.rect(surface, (40, 40, 40, 200), tooltip_rect, border_radius=5)
        pygame.draw.rect(surface, (100, 100, 100, 200), tooltip_rect, 1, border_radius=5)

        # Draw text
        current_y = tooltip_rect.y + padding
        for line in self.text_lines:
            line_surf = tiny_font.render(line, True, MOON_GLOW)
            surface.blit(line_surf, (tooltip_rect.x + padding, current_y))
            current_y += line_surf.get_height()

# Game State Saving/Loading
SAVE_FILE = "solitude_softener_save.json"

def save_game(moon, crest, fragments, dream_journal):
    data = {
        "moon_phase": moon.phase,
        "moon_speed": moon.speed,
        "crest_keystone_heat": crest.keystone_heat,
        "crest_sedum_level": crest.sedum_level,
        "crest_last_tended": crest.last_tended.isoformat(),
        "crest_fragments_sent": crest.fragments_sent,
        "fragments_data": fragments,
        "dream_journal_entries": dream_journal.entries
    }
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    print("Game Saved!")

def load_game(moon, crest, fragment_viewer, dream_journal):
    if not os.path.exists(SAVE_FILE):
        print("No save file found. Starting new game.")
        return False
    try:
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
        
        moon.phase = data.get("moon_phase", 0)
        moon.speed = data.get("moon_speed", 0.001)
        crest.keystone_heat = data.get("crest_keystone_heat", 0.5)
        crest.sedum_level = data.get("crest_sedum_level", 0.3)
        crest.last_tended = datetime.fromisoformat(data.get("crest_last_tended", datetime.now().isoformat()))
        crest.fragments_sent = data.get("crest_fragments_sent", 0)
        
        fragment_viewer.fragments = data.get("fragments_data", initial_fragments)
        fragment_viewer.current_fragment = 0
        fragment_viewer.last_change = pygame.time.get_ticks()

        dream_journal.entries = data.get("dream_journal_entries", [])
        dream_journal.calculate_max_scroll(HEIGHT * 0.30) # Recalculate max scroll based on panel height
        
        print("Game Loaded!")
        return True
    except Exception as e:
        print(f"Error loading game: {e}. Starting new game.")
        return False


# Create game objects
moon = MoonPhase()
crest = DragonsCrest()
fragment_viewer = FragmentViewer(initial_fragments) # Initialize with initial fragments
dream_journal = DreamJournal()

moon_particle_system = ParticleSystem()
crest_particle_system = ParticleSystem()
essence_particle_system = ParticleSystem() # For fragment discovery effect

# Star field for background
class Star:
    def __init__(self, x, y, size, brightness, vx, vy):
        self.x = x
        self.y = y
        self.size = size
        self.brightness = brightness
        self.vx = vx
        self.vy = vy
        self.twinkle_offset = random.uniform(0, math.pi * 2)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        # Wrap around
        if self.x < 0: self.x = WIDTH
        if self.x > WIDTH: self.x = 0
        if self.y < 0: self.y = HEIGHT
        if self.y > HEIGHT: self.y = 0

    def draw(self, surface):
        twinkle_factor = (math.sin(pygame.time.get_ticks() / 500.0 + self.twinkle_offset) + 1) / 2
        current_brightness = int(self.brightness * (0.7 + 0.3 * twinkle_factor))
        pygame.draw.circle(surface, (current_brightness, current_brightness, current_brightness), (int(self.x), int(self.y)), int(self.size))

stars = []
for _ in range(150):
    stars.append(Star(
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.uniform(0.5, 2.5),
        random.randint(150, 255),
        random.uniform(-0.05, 0.05),
        random.uniform(-0.05, 0.05)
    ))

# Create UI buttons (using ratios, adjusted for more compact layout)
button_width_ratio = 0.17
button_height_ratio = 0.07
button_y_ratio = 0.90
button_spacing_ratio = 0.02

tend_button = Button(0.04, button_y_ratio, button_width_ratio, button_height_ratio, "Tend Crest")
new_fragment_button = Button(0.04 + button_width_ratio + button_spacing_ratio, button_y_ratio, button_width_ratio, button_height_ratio, "Next Fragment") # Changed text
speed_up_button = Button(1 - button_width_ratio * 2 - button_spacing_ratio * 0.5, button_y_ratio, button_width_ratio, button_height_ratio, "Speed Up")
slow_down_button = Button(1 - button_width_ratio, button_y_ratio, button_width_ratio, button_height_ratio, "Slow Down")

# Tooltip instance
game_tooltip = Tooltip()

# Load game on startup
load_game(moon, crest, fragment_viewer, dream_journal)

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game(moon, crest, fragment_viewer.fragments, dream_journal) # Save on exit
            running = False
        if event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.size
            if WIDTH < 600: WIDTH = 600
            if HEIGHT < 400: HEIGHT = 400
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            update_fonts(HEIGHT) # Update fonts on resize
            dream_journal.calculate_max_scroll(HEIGHT * 0.30) # Recalculate max scroll for journal

        if event.type == pygame.MOUSEWHEEL:
            # Scroll dream journal if mouse is over it
            stats_panel_rect = pygame.Rect(WIDTH * 0.33, HEIGHT * 0.59, WIDTH * 0.63, HEIGHT * 0.30)
            dream_journal_rect = pygame.Rect(stats_panel_rect.x, stats_panel_rect.y, stats_panel_rect.width / 2 - (WIDTH * 0.01), stats_panel_rect.height) # Sub-panel for journal
            
            if dream_journal_rect.collidepoint(mouse_pos):
                dream_journal.scroll(-event.y * 10) # Adjust scroll speed

        # Handle button clicks
        if tend_button.check_click(mouse_pos, event):
            crest.tend()
            moon_particle_system.emit(WIDTH * 0.15, HEIGHT * 0.35, 10, MOON_GLOW, 2, 5, 0.5, 1.5, 60, 120, (-math.pi/2 - 0.5, -math.pi/2 + 0.5), type="wisp")
            crest_particle_system.emit(WIDTH * 0.15, HEIGHT * 0.65, 15, DRAGON_BLOOD, 3, 7, 0.8, 2.0, 80, 150, (math.pi/2 - 0.5, math.pi/2 + 0.5), type="ember")
            
            # Chance to discover a new dream fragment on Tend
            if random.random() < 0.3 and dream_fragment_pool: # 30% chance
                new_dream_frag = random.choice(dream_fragment_pool)
                dream_fragment_pool.remove(new_dream_frag) # Remove once discovered
                dream_journal.add_entry(new_dream_frag)
                # Emit essence particles when a dream fragment is found
                essence_particle_system.emit(stats_panel_rect.x + stats_panel_rect.width * 0.25, stats_panel_rect.center[1],
                                            20, SOFT_CYAN, 4, 8, 1.0, 3.0, 100, 200, type="essence")
            
        if new_fragment_button.check_click(mouse_pos, event):
            fragment_viewer.current_fragment = (fragment_viewer.current_fragment + 1) % len(fragment_viewer.fragments)
            fragment_viewer.last_change = pygame.time.get_ticks()
            
        if speed_up_button.check_click(mouse_pos, event):
            moon.speed = min(0.01, moon.speed * 1.5)
            
        if slow_down_button.check_click(mouse_pos, event):
            moon.speed = max(0.0001, moon.speed / 1.5)
    
    # Update game objects
    moon.update()
    crest.update()
    fragment_viewer.update()
    moon_particle_system.update()
    crest_particle_system.update()
    essence_particle_system.update()
    for star in stars:
        star.update()
    
    # Update button hover states
    tend_button.check_hover(mouse_pos)
    new_fragment_button.check_hover(mouse_pos)
    speed_up_button.check_hover(mouse_pos)
    slow_down_button.check_hover(mouse_pos)

    # Tooltip logic
    game_tooltip.hide() # Hide by default, show if hovered
    # Define main panel rectangles (relative to screen size)
    panel_margin_x = WIDTH * 0.03
    panel_margin_y = HEIGHT * 0.15
    panel_gap_x = WIDTH * 0.02
    panel_gap_y = HEIGHT * 0.02

    left_column_width = WIDTH * 0.28
    right_column_width = WIDTH - left_column_width - 2 * panel_margin_x - panel_gap_x

    moon_section_rect = pygame.Rect(panel_margin_x, panel_margin_y, left_column_width, HEIGHT * 0.35)
    crest_section_rect = pygame.Rect(panel_margin_x, moon_section_rect.bottom + panel_gap_y, left_column_width, HEIGHT * 0.35)
    
    fragment_viewer_rect = pygame.Rect(moon_section_rect.right + panel_gap_x, panel_margin_y, right_column_width, HEIGHT * 0.45)
    stats_panel_rect = pygame.Rect(moon_section_rect.right + panel_gap_x, fragment_viewer_rect.bottom + panel_gap_y, right_column_width, HEIGHT * 0.30)
    
    if moon_section_rect.collidepoint(mouse_pos):
        game_tooltip.show(f"Current Moon Phase: {moon.phase_name}\nIllumination: {int(moon.illumination*100)}%\nClick 'Speed Up/Down' to control time.", moon_section_rect, mouse_pos)
    elif crest_section_rect.collidepoint(mouse_pos):
        game_tooltip.show(f"Shadow Dragons Crest: Keystone Heat {int(crest.keystone_heat*100)}%, Sedum Growth {int(crest.sedum_level*100)}%. Tend to maintain its power.", crest_section_rect, mouse_pos)
    elif fragment_viewer_rect.collidepoint(mouse_pos):
        game_tooltip.show("Current Active Fragment. Cycles automatically.\nClick 'Next Fragment' to advance.", fragment_viewer_rect, mouse_pos)
    elif stats_panel_rect.collidepoint(mouse_pos):
        game_tooltip.show("Track the health of the Crest and connected keepers. Discovered dreams appear here.", stats_panel_rect, mouse_pos)


    # Draw everything
    screen.fill(BACKGROUND)
    
    # Draw starry background
    for star in stars:
        star.draw(screen)
    
    # Draw title
    title = title_font.render("SOLITUDE SOFTENER", True, MOON_GLOW)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT * 0.02))
    
    motto = small_font.render("\"In the kingdom of noise, we harvest silence—yet here we are, young soul.\"", True, SOFT_CYAN)
    screen.blit(motto, (WIDTH//2 - motto.get_width()//2, HEIGHT * 0.08))
    
    # Draw moon section
    pygame.draw.rect(screen, UI_PANEL_COLOR, moon_section_rect, border_radius=int(15 * (WIDTH/900)))
    pygame.draw.rect(screen, DRAGON_VIOLET, moon_section_rect, max(1, int(2 * (WIDTH/900))), border_radius=int(15 * (WIDTH/900)))
    
    moon_title = header_font.render("Moon Phase", True, MOON_GLOW)
    screen.blit(moon_title, (moon_section_rect.centerx - moon_title.get_width()//2, moon_section_rect.y + moon_section_rect.height * 0.05))
    
    moon_draw_size = int(moon_section_rect.width * 0.5)
    moon_draw_rect = pygame.Rect(0,0,moon_draw_size, moon_draw_size)
    moon_draw_rect.center = (moon_section_rect.centerx, moon_section_rect.y + moon_section_rect.height * 0.4)
    moon.draw(screen, moon_draw_rect)
    
    phase_text = body_font.render(moon.phase_name, True, MOON_GLOW)
    illum_text = body_font.render(f"Illumination: {int(moon.illumination * 100)}%", True, MOON_GLOW)
    crescent_text = small_font.render("Crescent Active" if moon.is_crescent() else "Fragment Delivery Paused", 
                                    True, SOFT_CYAN if moon.is_crescent() else (200, 100, 100))
    
    screen.blit(phase_text, (moon_section_rect.centerx - phase_text.get_width()//2, moon_section_rect.y + moon_section_rect.height * 0.72))
    screen.blit(illum_text, (moon_section_rect.centerx - illum_text.get_width()//2, moon_section_rect.y + moon_section_rect.height * 0.8))
    screen.blit(crescent_text, (moon_section_rect.centerx - crescent_text.get_width()//2, moon_section_rect.y + moon_section_rect.height * 0.88))
    
    # Draw crest section
    pygame.draw.rect(screen, UI_PANEL_COLOR, crest_section_rect, border_radius=int(15 * (WIDTH/900)))
    pygame.draw.rect(screen, DRAGON_VIOLET, crest_section_rect, max(1, int(2 * (WIDTH/900))), border_radius=int(15 * (WIDTH/900)))
    
    crest_title = header_font.render("Shadow Dragons Crest", True, MOON_GLOW)
    screen.blit(crest_title, (crest_section_rect.centerx - crest_title.get_width()//2, crest_section_rect.y + crest_section_rect.height * 0.05))
    
    crest_draw_rect = pygame.Rect(crest_section_rect.x + crest_section_rect.width * 0.1, crest_section_rect.y + crest_section_rect.height * 0.2,
                                  crest_section_rect.width * 0.8, crest_section_rect.height * 0.7)
    crest.draw(screen, crest_draw_rect)
    
    # Draw fragment viewer
    fragment_viewer.draw(screen, fragment_viewer_rect)
    
    # Draw stats panel and Dream Journal (split the stats panel rect)
    pygame.draw.rect(screen, UI_PANEL_COLOR, stats_panel_rect, border_radius=int(15 * (WIDTH/900)))
    pygame.draw.rect(screen, SOFT_CYAN, stats_panel_rect, max(1, int(2 * (WIDTH/900))), border_radius=int(15 * (WIDTH/900)))
    
    # Split the stats panel into two sub-panels
    stats_sub_panel_width = stats_panel_rect.width / 2 - (WIDTH * 0.01) # Small gap in middle
    stats_left_rect = pygame.Rect(stats_panel_rect.x, stats_panel_rect.y, stats_sub_panel_width, stats_panel_rect.height)
    stats_right_rect = pygame.Rect(stats_panel_rect.x + stats_panel_rect.width / 2 + (WIDTH * 0.005), stats_panel_rect.y, stats_sub_panel_width, stats_panel_rect.height)

    # Draw Crest Status (left sub-panel)
    stats_title = header_font.render("Crest Status", True, MOON_GLOW)
    screen.blit(stats_title, (stats_left_rect.centerx - stats_title.get_width()//2, stats_left_rect.y + stats_left_rect.height * 0.05))
    
    stat_start_x = stats_left_rect.x + stats_left_rect.width * 0.05
    stat_start_y = stats_left_rect.y + stats_left_rect.height * 0.2
    line_height = body_font.get_height() + (HEIGHT * 0.005)

    heat_text = body_font.render(f"Keystone Heat: {int(crest.keystone_heat * 100)}%", True, MOON_GLOW)
    sedum_text = body_font.render(f"Sedum Growth: {int(crest.sedum_level * 100)}%", True, MOON_GLOW)
    last_tended_text = tiny_font.render(f"Last Tended: {crest.last_tended.strftime('%Y-%m-%d %H:%M')}", True, MOON_GLOW)
    fragments_sent_text = body_font.render(f"Fragments Sent: {crest.fragments_sent}", True, MOON_GLOW)
    
    screen.blit(heat_text, (stat_start_x, stat_start_y))
    screen.blit(sedum_text, (stat_start_x, stat_start_y + line_height))
    screen.blit(last_tended_text, (stat_start_x, stat_start_y + 2 * line_height))
    screen.blit(fragments_sent_text, (stat_start_x, stat_start_y + 3 * line_height))
    
    # Draw connected keepers (right sub-panel, or adjusted for smaller screen)
    keepers_title = body_font.render("Connected Keepers:", True, SOFT_CYAN)
    screen.blit(keepers_title, (stat_start_x, stat_start_y + 4 * line_height))
    
    keeper_col_width = stats_left_rect.width * 0.3
    keeper_row_height = small_font.get_height() + (HEIGHT * 0.002)
    for i, keeper in enumerate(crest.connected_keepers):
        keeper_text = small_font.render(keeper, True, MOON_GLOW)
        screen.blit(keeper_text, (stat_start_x + (i % 2) * keeper_col_width, 
                                 stat_start_y + 4 * line_height + keeper_row_height + (i // 2) * keeper_row_height))
    
    # Draw Dream Journal (right sub-panel)
    dream_journal.draw(screen, stats_right_rect)

    # Draw particle effects
    moon_particle_system.draw(screen)
    crest_particle_system.draw(screen)
    essence_particle_system.draw(screen)

    # Draw buttons
    tend_button.draw(screen, WIDTH, HEIGHT)
    new_fragment_button.draw(screen, WIDTH, HEIGHT)
    speed_up_button.draw(screen, WIDTH, HEIGHT)
    slow_down_button.draw(screen, WIDTH, HEIGHT)
    
    # Draw time scale indicator
    time_scale_text = body_font.render(f"Speed: {moon.speed * 10000:.1f}x", True, MOON_GLOW)
    screen.blit(time_scale_text, (speed_up_button.rect.centerx - time_scale_text.get_width() * 0.6, 
                                 speed_up_button.rect.y + speed_up_button.rect.height * 0.3))
    
    # Draw instructions
    instructions = small_font.render("Tip: Tend the Crest regularly to keep the dragons content and find new dreams!", True, (150, 150, 180))
    screen.blit(instructions, (WIDTH//2 - instructions.get_width()//2, HEIGHT * 0.965))
    
    # Draw Tooltip on top of everything else
    game_tooltip.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()