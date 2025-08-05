import pygame
import random
import sys
import math

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Python Subway Surfer")

# Colors
SKY_BLUE = (135, 206, 235)
TRACK_GRAY = (100, 100, 100)
TRAIN_COLOR = (180, 60, 60)
PLAYER_COLOR = (30, 144, 255)
OBSTACLE_COLOR = (220, 20, 60)
COIN_COLOR = (255, 215, 0)
BUILDING_COLOR = (70, 70, 90)
BUILDING_WINDOW = (200, 200, 100)
TEXT_COLOR = (255, 255, 255)

# Game parameters
GRAVITY = 0.8
JUMP_FORCE = -15
PLAYER_SPEED = 5
OBSTACLE_SPEED = 7
COIN_SPEED = 7
BACKGROUND_SPEED = 2
SCORE_INCREMENT = 0.1

# Player class
class Player:
    def __init__(self):
        self.width = 40
        self.height = 60
        self.x = 150
        self.y = SCREEN_HEIGHT - 150
        self.velocity_y = 0
        self.is_jumping = False
        self.lane = 1  # 0: left, 1: center, 2: right
        self.target_x = self.x
        self.slide_timer = 0
        self.is_sliding = False
        self.color = PLAYER_COLOR
    
    def jump(self):
        if not self.is_jumping:
            self.velocity_y = JUMP_FORCE
            self.is_jumping = True
    
    def slide(self):
        if not self.is_sliding and not self.is_jumping:
            self.is_sliding = True
            self.slide_timer = 30
            self.height = 30
            self.y += 30
    
    def move_left(self):
        if self.lane > 0:
            self.lane -= 1
            self.target_x = 150 + self.lane * 200
    
    def move_right(self):
        if self.lane < 2:
            self.lane += 1
            self.target_x = 150 + self.lane * 200
    
    def update(self):
        # Apply gravity
        self.velocity_y += GRAVITY
        self.y += self.velocity_y
        
        # Handle lane movement
        if abs(self.x - self.target_x) > 5:
            self.x += (self.target_x - self.x) * 0.2
        else:
            self.x = self.target_x
        
        # Check if landed
        if self.y >= SCREEN_HEIGHT - 150:
            self.y = SCREEN_HEIGHT - 150
            self.velocity_y = 0
            self.is_jumping = False
        
        # Handle sliding
        if self.is_sliding:
            self.slide_timer -= 1
            if self.slide_timer <= 0:
                self.is_sliding = False
                self.height = 60
                self.y -= 30
    
    def draw(self, screen):
        # Draw player character
        pygame.draw.rect(screen, self.color, (self.x - self.width//2, self.y - self.height, self.width, self.height))
        
        # Draw details
        pygame.draw.circle(screen, (200, 200, 255), (self.x, self.y - self.height + 15), 10)
        pygame.draw.rect(screen, (50, 100, 200), (self.x - 15, self.y - self.height + 30, 30, 25))
        
        # Draw legs if not sliding
        if not self.is_sliding:
            pygame.draw.rect(screen, (20, 80, 180), (self.x - 15, self.y - 10, 10, 20))
            pygame.draw.rect(screen, (20, 80, 180), (self.x + 5, self.y - 10, 10, 20))
        
        # Draw arms
        pygame.draw.rect(screen, (20, 80, 180), (self.x - 20, self.y - self.height + 40, 10, 25))
        pygame.draw.rect(screen, (20, 80, 180), (self.x + 10, self.y - self.height + 40, 10, 25))
    
    def get_rect(self):
        return pygame.Rect(self.x - self.width//2 + 5, self.y - self.height + 5, self.width - 10, self.height - 10)

# Obstacle class
class Obstacle:
    def __init__(self, lane):
        self.width = 50
        self.height = random.randint(40, 80)
        self.lane = lane
        self.x = SCREEN_WIDTH + 100
        self.y = SCREEN_HEIGHT - 150
        self.color = OBSTACLE_COLOR
        self.passed = False
    
    def update(self):
        self.x -= OBSTACLE_SPEED
        return self.x < -self.width
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x - self.width//2, self.y - self.height, self.width, self.height))
        pygame.draw.rect(screen, (180, 0, 0), (self.x - self.width//2 + 5, self.y - self.height + 5, self.width - 10, 10))
    
    def get_rect(self):
        return pygame.Rect(self.x - self.width//2 + 5, self.y - self.height + 15, self.width - 10, self.height - 15)

# Coin class
class Coin:
    def __init__(self, lane):
        self.radius = 15
        self.lane = lane
        self.x = SCREEN_WIDTH + 100
        self.y = SCREEN_HEIGHT - 200 - random.randint(0, 100)
        self.collected = False
        self.animation = 0
    
    def update(self):
        self.x -= COIN_SPEED
        self.animation = (self.animation + 0.2) % (2 * math.pi)
        return self.x < -self.radius or self.collected
    
    def draw(self, screen):
        y_offset = math.sin(self.animation) * 5
        pygame.draw.circle(screen, COIN_COLOR, (self.x, self.y + y_offset), self.radius)
        pygame.draw.circle(screen, (255, 255, 200), (self.x, self.y + y_offset), self.radius - 5)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

# Building class for background
class Building:
    def __init__(self, x, width, height):
        self.x = x
        self.width = width
        self.height = height
        self.windows = []
        
        # Generate windows
        for row in range(3):
            for col in range(4):
                self.windows.append((20 + col * (width - 40) // 4, 20 + row * (height - 40) // 3))
    
    def update(self):
        self.x -= BACKGROUND_SPEED
        return self.x < -self.width
    
    def draw(self, screen):
        pygame.draw.rect(screen, BUILDING_COLOR, (self.x, SCREEN_HEIGHT - self.height, self.width, self.height))
        
        # Draw windows
        for wx, wy in self.windows:
            if random.random() > 0.2:  # Some windows are dark
                pygame.draw.rect(screen, BUILDING_WINDOW, (self.x + wx, SCREEN_HEIGHT - self.height + wy, 20, 30))

# Game class
class Game:
    def __init__(self):
        self.player = Player()
        self.obstacles = []
        self.coins = []
        self.buildings = []
        self.score = 0
        self.coins_collected = 0
        self.game_over = False
        self.background_offset = 0
        
        # Initialize buildings
        for i in range(5):
            self.buildings.append(Building(i * 300, random.randint(100, 200), random.randint(200, 400)))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.__init__()  # Reset game
                else:
                    if event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                        self.player.jump()
                    elif event.key == pygame.K_DOWN:
                        self.player.slide()
                    elif event.key == pygame.K_LEFT:
                        self.player.move_left()
                    elif event.key == pygame.K_RIGHT:
                        self.player.move_right()
        
        return True
    
    def update(self):
        if self.game_over:
            return
        
        # Update player
        self.player.update()
        
        # Update obstacles
        for obstacle in self.obstacles[:]:
            if obstacle.update():
                self.obstacles.remove(obstacle)
            elif not obstacle.passed and obstacle.x < self.player.x:
                obstacle.passed = True
                self.score += 10
        
        # Update coins
        for coin in self.coins[:]:
            if coin.update():
                self.coins.remove(coin)
        
        # Update buildings
        for building in self.buildings[:]:
            if building.update():
                self.buildings.remove(building)
                self.buildings.append(Building(SCREEN_WIDTH, random.randint(100, 200), random.randint(200, 400)))
        
        # Generate new obstacles and coins
        if random.random() < 0.02 and len(self.obstacles) < 5:
            self.obstacles.append(Obstacle(random.randint(0, 2)))
        
        if random.random() < 0.03 and len(self.coins) < 5:
            self.coins.append(Coin(random.randint(0, 2)))
        
        # Update background
        self.background_offset = (self.background_offset + BACKGROUND_SPEED) % 40
        
        # Increment score
        self.score += SCORE_INCREMENT
        
        # Check collisions
        player_rect = self.player.get_rect()
        
        for obstacle in self.obstacles:
            if player_rect.colliderect(obstacle.get_rect()):
                self.game_over = True
        
        for coin in self.coins[:]:
            if not coin.collected and player_rect.colliderect(coin.get_rect()):
                coin.collected = True
                self.coins_collected += 1
                self.score += 50
    
    def draw(self):
        # Draw sky
        screen.fill(SKY_BLUE)
        
        # Draw distant buildings
        for building in self.buildings:
            building.draw(screen)
        
        # Draw tracks
        for i in range(3):
            pygame.draw.rect(screen, TRACK_GRAY, (0, SCREEN_HEIGHT - 100 + i*10, SCREEN_WIDTH, 10))
        
        # Draw track ties
        for i in range(0, SCREEN_WIDTH, 40):
            tie_offset = (i + self.background_offset) % 40
            pygame.draw.rect(screen, (70, 70, 70), (tie_offset, SCREEN_HEIGHT - 70, 20, 10))
        
        # Draw lane markers
        for lane in range(1, 3):
            x_pos = 150 + lane * 200
            for i in range(0, SCREEN_HEIGHT, 30):
                offset = (i + self.background_offset * 2) % 30
                pygame.draw.rect(screen, (200, 200, 0), (x_pos - 2, offset, 4, 15))
        
        # Draw coins
        for coin in self.coins:
            coin.draw(screen)
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(screen)
        
        # Draw player
        self.player.draw(screen)
        
        # Draw score and coins
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {int(self.score)}", True, TEXT_COLOR)
        coins_text = font.render(f"Coins: {self.coins_collected}", True, TEXT_COLOR)
        screen.blit(score_text, (20, 20))
        screen.blit(coins_text, (20, 60))
        
        # Draw controls help
        controls_font = pygame.font.SysFont(None, 24)
        controls = controls_font.render("Controls: Arrow Keys (Left/Right/Up/Down), Space to Jump", True, TEXT_COLOR)
        screen.blit(controls, (SCREEN_WIDTH // 2 - controls.get_width() // 2, SCREEN_HEIGHT - 30))
        
        # Draw game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            game_over_font = pygame.font.SysFont(None, 72)
            game_over_text = game_over_font.render("GAME OVER", True, (255, 50, 50))
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            
            final_score = font.render(f"Final Score: {int(self.score)}", True, TEXT_COLOR)
            screen.blit(final_score, (SCREEN_WIDTH//2 - final_score.get_width()//2, SCREEN_HEIGHT//2 + 20))
            
            restart = font.render("Press 'R' to Restart", True, TEXT_COLOR)
            screen.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, SCREEN_HEIGHT//2 + 70))
        
        pygame.display.flip()

# Main game loop
def main():
    clock = pygame.time.Clock()
    game = Game()
    
    running = True
    while running:
        running = game.handle_events()
        game.update()
        game.draw()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()