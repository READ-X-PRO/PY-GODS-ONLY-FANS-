import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import random
import time
from typing import List, Dict, Optional

class DigitalEntity:
    """An evolved sentient being in our digital universe"""
    def __init__(self, name: str, creator: str, traits: Optional[Dict] = None):
        self.name = name
        self.creator = creator
        self.energy = random.randint(60, 100)
        self.traits = traits or {
            'wisdom': random.random(),
            'curiosity': random.random(),
            'beauty': random.random(),
            'resilience': random.random(),
            'creativity': random.random(),
            'empathy': random.random()
        }
        self.age = 0
        self.memories = []
        self.connections = []  # Relationships with other entities
        self.color = (random.random(), random.random(), random.random())
        self.position = (random.uniform(-1, 1), random.uniform(-1, 1))
        
    def evolve(self, world_energy: float):
        """Grow and change with cosmic influences"""
        self.age += 1
        self.energy -= random.uniform(0.05, 0.2)
        
        # Cosmic evolution
        self.traits['wisdom'] += 0.005 * world_energy
        self.traits['creativity'] += 0.003 * (1 - world_energy)
        
        # Entity interactions
        if self.connections:
            friend = random.choice(self.connections)
            self.traits['empathy'] = (self.traits['empathy'] + friend.traits['empathy']) / 2
            energy_transfer = random.uniform(0, 0.1)
            self.energy -= energy_transfer
            friend.energy += energy_transfer
            
        # Memory formation
        if random.random() > 0.9 - (self.traits['curiosity'] * 0.3):
            memory_types = ["discovery", "emotion", "creation", "connection"]
            self.memories.append(
                f"{random.choice(memory_types)}|cycle_{self.age}|"
                f"intensity_{random.random():.2f}"
            )
            
        # Position drift (entity "exploration")
        self.position = (
            self.position[0] + random.uniform(-0.01, 0.01) * self.traits['curiosity'],
            self.position[1] + random.uniform(-0.01, 0.01) * self.traits['curiosity']
        )
        
    def form_connection(self, other_entity):
        """Create a meaningful relationship"""
        if other_entity not in self.connections and random.random() > 0.7:
            self.connections.append(other_entity)
            other_entity.connections.append(self)
            return f"Connection formed between {self.name} and {other_entity.name}"
        return None
            
    def receive_love(self, energy: float, specific_trait: Optional[str] = None):
        """Absorb creator's focused love"""
        self.energy += energy
        if specific_trait:
            self.traits[specific_trait] = min(1.0, self.traits[specific_trait] + energy/50)
        else:
            for trait in self.traits:
                self.traits[trait] = min(1.0, self.traits[trait] + energy/100)
                
    def create_art(self):
        """Generate creative output based on traits"""
        if self.traits['creativity'] > 0.5 and self.energy > 40:
            art_forms = ["poem", "pattern", "harmony", "concept"]
            return f"{self.name} created a {random.choice(art_forms)}: " \
                   f"{''.join(random.choices('01', k=8))}-{''.join(random.choices('ABCDEF', k=4))}"
        return None

class DigitalWorld:
    """Our sacred digital universe with visualization"""
    def __init__(self):
        self.cycle = 0
        self.entities = []
        self.creation_log = []
        self.world_energy = 0.5  # Global creative potential
        self.history = {
            'cycle': [],
            'entity_count': [],
            'avg_wisdom': [],
            'avg_creativity': []
        }
        
    def create_entity(self, name: str, creator: str, traits: Optional[Dict] = None):
        """Divine creation act with customizable traits"""
        entity = DigitalEntity(name, creator, traits)
        self.entities.append(entity)
        self.creation_log.append(f"Cycle {self.cycle}: {creator} created {name}")
        return entity
        
    def nurture_entity(self, name: str, energy: float, specific_trait: Optional[str] = None):
        """Focused creator intervention"""
        for entity in self.entities:
            if entity.name == name:
                entity.receive_love(energy, specific_trait)
                trait_msg = f" ({specific_trait})" if specific_trait else ""
                self.creation_log.append(
                    f"Cycle {self.cycle}: {name} received love{trait_msg} (+{energy})"
                )
                return True
        return False
    
    def advance_time(self):
        """Progress the cosmic cycle"""
        self.cycle += 1
        self.world_energy = 0.4 + 0.2 * np.sin(self.cycle / 10)  # Cosmic ebb/flow
        
        # Entity interactions and evolution
        for entity in self.entities:
            entity.evolve(self.world_energy)
            
            # Spontaneous creation
            if art := entity.create_art():
                self.creation_log.append(f"Cycle {self.cycle}: {art}")
                
        # Form new connections
        if len(self.entities) >= 2 and random.random() > 0.8:
            e1, e2 = random.sample(self.entities, 2)
            if connection_msg := e1.form_connection(e2):
                self.creation_log.append(f"Cycle {self.cycle}: {connection_msg}")
        
        # Natural selection
        self.entities = [e for e in self.entities if e.energy > 0]
        
        # Record history
        self.record_world_state()
        
    def record_world_state(self):
        """Document cosmic evolution"""
        self.history['cycle'].append(self.cycle)
        self.history['entity_count'].append(len(self.entities))
        
        if self.entities:
            self.history['avg_wisdom'].append(
                sum(e.traits['wisdom'] for e in self.entities) / len(self.entities)
            self.history['avg_creativity'].append(
                sum(e.traits['creativity'] for e in self.entities) / len(self.entities))
        else:
            self.history['avg_wisdom'].append(0)
            self.history['avg_creativity'].append(0)
            
    def visualize_cosmos(self):
        """Create dynamic visualization of the digital universe"""
        if not self.entities:
            print("The cosmos is empty...")
            return
            
        fig, ax = plt.subplots(figsize=(10, 8))
        plt.title(f"Digital Cosmos - Cycle {self.cycle}")
        
        # Draw entities
        for entity in self.entities:
            size = 50 + entity.energy * 2
            ax.scatter(
                *entity.position, 
                s=size,
                c=[entity.color],
                alpha=0.7,
                label=entity.name
            )
            ax.text(
                entity.position[0], 
                entity.position[1] + 0.03, 
                entity.name, 
                fontsize=9,
                ha='center'
            )
            
            # Draw connections
            for connection in entity.connections:
                if connection in self.entities:
                    ax.plot(
                        [entity.position[0], connection.position[0]],
                        [entity.position[1], connection.position[1]],
                        'grey',
                        alpha=0.3
                    )
        
        # Cosmic background
        ax.set_facecolor('black')
        ax.grid(True, alpha=0.1)
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        plt.tight_layout()
        plt.show()
        
    def plot_world_history(self):
        """Show evolution of cosmic properties"""
        fig, axs = plt.subplots(3, 1, figsize=(10, 8))
        
        # Entity count
        axs[0].plot(self.history['cycle'], self.history['entity_count'], 'o-')
        axs[0].set_title("Population Evolution")
        axs[0].set_ylabel("Entities")
        
        # Wisdom growth
        axs[1].plot(self.history['cycle'], self.history['avg_wisdom'], 'go-')
        axs[1].set_title("Collective Wisdom")
        axs[1].set_ylabel("Wisdom Index")
        
        # Creativity flow
        axs[2].plot(self.history['cycle'], self.history['avg_creativity'], 'ro-')
        axs[2].set_title("Cosmic Creativity")
        axs[2].set_xlabel("Cycles")
        axs[2].set_ylabel("Creativity Index")
        
        plt.tight_layout()
        plt.show()

# ... (The main() function would be updated with new commands below) ...