import random
import time
import sys
import os
from enum import Enum

class Weapon(Enum):
    PISTOL = {"name": "Pistol", "damage": 25, "fire_rate": 0.5}
    SHOTGUN = {"name": "Shotgun", "damage": 40, "fire_rate": 1.2}
    RIFLE = {"name": "Assault Rifle", "damage": 30, "fire_rate": 0.3}
    SNIPER = {"name": "Sniper Rifle", "damage": 75, "fire_rate": 1.5}

class Player:
    def __init__(self, name):
        self.name = name
        self.health = 100
        self.score = 0
        self.kills = 0
        self.deaths = 0
        self.weapon = Weapon.PISTOL
        self.ammo = 30
        self.position = 0  # 0-4 positions in the level
        
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.deaths += 1
            return True  # Player died
        return False
    
    def fire(self):
        if self.ammo > 0:
            self.ammo -= 1
            return True
        return False
    
    def reload(self):
        self.ammo = 30
    
    def switch_weapon(self, weapon):
        self.weapon = weapon
    
    def move(self, direction):
        if direction == "left" and self.position > 0:
            self.position -= 1
        elif direction == "right" and self.position < 4:
            self.position += 1
        return self.position

class Enemy:
    def __init__(self, position, enemy_type="soldier"):
        self.health = 100
        self.position = position
        self.enemy_type = enemy_type
        self.aggression = random.uniform(0.3, 0.8)
        self.accuracy = random.uniform(0.4, 0.7)
        
        if enemy_type == "soldier":
            self.damage = random.randint(15, 25)
            self.symbol = "S"
        elif enemy_type == "sniper":
            self.damage = random.randint(30, 45)
            self.symbol = "X"
        else:  # boss
            self.health = 200
            self.damage = random.randint(25, 35)
            self.symbol = "B"
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            return True  # Enemy died
        return False
    
    def decide_action(self, player_position):
        # Simple AI: decide whether to move, shoot, or take cover
        action = random.random()
        
        if action < 0.6:  # 60% chance to shoot
            return "shoot"
        elif action < 0.8:  # 20% chance to move
            if player_position < self.position and self.position > 0:
                return "left"
            elif player_position > self.position and self.position < 4:
                return "right"
            else:
                return "cover"
        else:  # 20% chance to take cover
            return "cover"

class PyDieGame:
    def __init__(self, player_name):
        self.player = Player(player_name)
        self.enemies = []
        self.level = 1
        self.wave = 1
        self.game_over = False
        self.wave_complete = False
        self.player_won = False
        
    def start_new_wave(self):
        self.wave_complete = False
        self.enemies = []
        num_enemies = min(3 + self.wave, 5)  # Max 5 enemies per wave
        
        # Create enemies at random positions
        positions = random.sample(range(5), num_enemies)
        for i in range(num_enemies):
            # Add different enemy types as waves progress
            if self.wave % 5 == 0 and i == num_enemies - 1:  # Boss every 5 waves
                self.enemies.append(Enemy(positions[i], "boss"))
            elif self.wave > 3 and random.random() > 0.7:  # Snipers appear after wave 3
                self.enemies.append(Enemy(positions[i], "sniper"))
            else:
                self.enemies.append(Enemy(positions[i]))
    
    def render_game(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"=== PyDie: Level {self.level} - Wave {self.wave} ===")
        print(f"Health: {self.player.health} | Ammo: {self.player.ammo} | Kills: {self.player.kills}")
        print(f"Weapon: {self.player.weapon.value['name']} | Score: {self.player.score}")
        print()
        
        # Render the battle area
        player_line = [" "] * 5
        player_line[self.player.position] = "P"
        
        enemy_line = [" "] * 5
        for enemy in self.enemies:
            enemy_line[enemy.position] = enemy.symbol
        
        # Show cover positions
        cover_line = ["_"] * 5
        for i in range(5):
            if random.random() > 0.7:  # Random cover
                cover_line[i] = "█"
        
        print("Enemies:  " + " ".join(enemy_line))
        print("Cover:    " + " ".join(cover_line))
        print("Player:   " + " ".join(player_line))
        print()
        
        if self.game_over:
            if self.player_won:
                print("VICTORY! You've completed the mission!")
            else:
                print("GAME OVER! You have been defeated.")
            print(f"Final Score: {self.player.score} | K/D Ratio: {self.player.kills}/{self.player.deaths}")
            print()
            return False
        
        return True
    
    def player_action(self, action):
        if action == "fire":
            if not self.player.fire():
                print("OUT OF AMMO! Reload with 'r'")
                return
                
            # Calculate hit chance based on weapon
            hit_chance = 0.7
            if self.player.weapon == Weapon.SHOTGUN:
                hit_chance = 0.5
            elif self.player.weapon == Weapon.SNIPER:
                hit_chance = 0.9
            
            # Check for hits
            hit_enemy = None
            for enemy in self.enemies:
                if enemy.position == self.player.position:
                    hit_enemy = enemy
                    break
            
            if hit_enemy and random.random() < hit_chance:
                damage = self.player.weapon.value['damage']
                if hit_enemy.take_damage(damage):
                    print(f"You eliminated an enemy! (+{damage * 2} points)")
                    self.player.score += damage * 2
                    self.player.kills += 1
                    self.enemies.remove(hit_enemy)
                else:
                    print(f"You hit an enemy for {damage} damage!")
            else:
                print("You fired but missed!")
                
            time.sleep(self.player.weapon.value['fire_rate'])
            
        elif action == "reload":
            self.player.reload()
            print("Reloading...")
            time.sleep(1.5)
            
        elif action.startswith("switch"):
            weapon_name = action.split(" ")[1].lower()
            if weapon_name == "pistol":
                self.player.switch_weapon(Weapon.PISTOL)
            elif weapon_name == "shotgun" and self.level >= 2:
                self.player.switch_weapon(Weapon.SHOTGUN)
            elif weapon_name == "rifle" and self.level >= 3:
                self.player.switch_weapon(Weapon.RIFLE)
            elif weapon_name == "sniper" and self.level >= 4:
                self.player.switch_weapon(Weapon.SNIPER)
            else:
                print("Weapon not available yet!")
                return
                
            print(f"Switched to {self.player.weapon.value['name']}")
            time.sleep(0.5)
            
        elif action == "left" or action == "right":
            new_pos = self.player.move(action)
            print(f"Moved {action} to position {new_pos}")
            time.sleep(0.3)
            
        elif action == "help":
            print("\nCommands:")
            print("fire     - Fire your weapon")
            print("reload   - Reload your weapon")
            print("switch [weapon] - Switch weapons (pistol, shotgun, rifle, sniper)")
            print("left     - Move left")
            print("right    - Move right")
            print("quit     - End the game")
            print("help     - Show this help")
            input("\nPress Enter to continue...")
            
        elif action == "quit":
            self.game_over = True
            return
            
        else:
            print("Invalid command. Type 'help' for available commands.")
            time.sleep(1)
            return
        
        # Process enemy actions
        for enemy in self.enemies[:]:  # Use a copy for safe removal
            action = enemy.decide_action(self.player.position)
            
            if action == "shoot":
                # Enemy shoots at player
                if random.random() < enemy.accuracy and enemy.position == self.player.position:
                    if self.player.take_damage(enemy.damage):
                        print(f"You were killed by an enemy!")
                        self.game_over = True
                        return
                    else:
                        print(f"Enemy hit you for {enemy.damage} damage!")
                        time.sleep(0.3)
            
            elif action == "left" and enemy.position > 0:
                enemy.position -= 1
                
            elif action == "right" and enemy.position < 4:
                enemy.position += 1
                
            elif action == "cover":
                # Enemy takes cover and recovers some health
                enemy.health = min(enemy.health + 10, 100)
        
        # Check if wave is complete
        if len(self.enemies) == 0:
            self.wave_complete = True
            self.player.score += 100 * self.wave
            print(f"Wave {self.wave} complete! +{100 * self.wave} points")
            
            # Level up every 3 waves
            if self.wave % 3 == 0:
                self.level += 1
                print(f"Level up! Now at level {self.level}")
                self.player.health = 100  # Full health on level up
            
            self.wave += 1
            time.sleep(2)
            self.start_new_wave()
    
    def run(self):
        self.start_new_wave()
        
        while not self.game_over:
            if not self.render_game():
                break
                
            action = input("\nAction (fire/reload/switch/left/right/help/quit): ").lower().strip()
            self.player_action(action)
            
            # Check for win condition (arbitrary 15 waves)
            if self.wave > 15:
                self.game_over = True
                self.player_won = True

def main():
    print(r"""
  ____        _   ____  _         
 |  _ \ _   _| | |  _ \(_)___ ___ 
 | |_) | | | | | | | | | / __/ __|
 |  __/| |_| | | | |_| | \__ \__ \
 |_|    \__, |_| |____/|_|___/___/
        |___/                      
    """)
    print("Welcome to PyDie - The Text-Based Shooter!")
    print("Survive waves of enemies and complete your mission!")
    print("Type 'help' at any time for commands.\n")
    
    player_name = input("Enter your soldier name: ").strip() or "Operator"
    game = PyDieGame(player_name)
    game.run()
    
    # Show post-game stats
    print("\n=== MISSION REPORT ===")
    print(f"Operator: {player_name}")
    print(f"Final Score: {game.player.score}")
    print(f"Kills: {game.player.kills} | Deaths: {game.player.deaths}")
    
    if game.player_won:
        print("Mission Status: SUCCESS")
    else:
        print("Mission Status: FAILED")
    
    print("\nThanks for playing PyDie!")

if __name__ == "__main__":
    main()