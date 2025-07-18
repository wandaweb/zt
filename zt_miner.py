import pygame
import random
import math
import json
import os
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description='ZT Miner - Chapter I: The Escape')
parser.add_argument('--scale', type=int, choices=[1, 2, 4], default=1,
                    help='Scale factor for the game window (1, 2, or 4)')
args = parser.parse_args()

# Initialize Pygame
pygame.init()

# Constants
BASE_WIDTH = 800
BASE_HEIGHT = 600
SCALE_FACTOR = args.scale
SCREEN_WIDTH = BASE_WIDTH
SCREEN_HEIGHT = BASE_HEIGHT
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
BROWN = (139, 69, 19)
DARK_RED = (139, 0, 0)
DARK_PURPLE = (64, 0, 64)
LIGHT_BLUE = (173, 216, 230)

# Layer colors and themes
LAYER_THEMES = {
    0: {"name": "Core", "bg_color": (139, 0, 0), "enemy_color": YELLOW, "obstacle_color": (255, 100, 100), "static_enemy_color": WHITE},
    1: {"name": "Mantle", "bg_color": (255, 69, 0), "enemy_color": PURPLE, "obstacle_color": (100, 50, 0), "static_enemy_color": BLUE},
    2: {"name": "Lower Crust", "bg_color": (139, 69, 19), "enemy_color": GREEN, "obstacle_color": (200, 200, 200), "static_enemy_color": YELLOW},
    3: {"name": "Upper Crust", "bg_color": (105, 105, 105), "enemy_color": RED, "obstacle_color": (50, 50, 50), "static_enemy_color": ORANGE},
    4: {"name": "Ice", "bg_color": (135, 206, 235), "enemy_color": RED, "obstacle_color": (100, 100, 100), "static_enemy_color": PURPLE}
}

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.drill_active = False
        self.drill_cooldown = 0
        self.bullets = []
        self.bullet_cooldown = 0
        self.invulnerable = 0
        
        # Load ship images
        self.ship_body_img = None
        self.drill_img = None
        self.images_loaded = False
        
        try:
            # Try to load ship body image
            ship_body_raw = pygame.image.load("res/ship-body.png").convert_alpha()
            self.ship_body_img = pygame.transform.scale(ship_body_raw, (self.width, self.height))
            
            # Try to load drill image
            drill_raw = pygame.image.load("res/ship-nose.png").convert_alpha()
            # Scale drill to be proportional - make it smaller than the ship body
            drill_width = int(self.width)  # 100% of ship width
            drill_height = int(self.height * 0.25)  # 25% of ship height
            self.drill_img = pygame.transform.scale(drill_raw, (drill_width, drill_height))
            
            self.images_loaded = True
            print("Ship images loaded successfully")
            
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load ship images: {e}")
            print("Using fallback rectangle graphics")
            self.images_loaded = False
        
    def update(self, keys):
        # Movement
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < SCREEN_HEIGHT - self.height:
            self.y += self.speed
            
        # Drill activation
        if keys[pygame.K_x]:
            self.drill_active = True
            self.drill_cooldown = 10
        else:
            self.drill_active = False
            
        if self.drill_cooldown > 0:
            self.drill_cooldown -= 1
            
        # Shooting
        if keys[pygame.K_SPACE]:

            if self.bullet_cooldown < 1:
                self.bullets.append(Bullet(self.x + self.width // 2, self.y))
                self.bullet_cooldown = 10

        if self.bullet_cooldown > 0:
            self.bullet_cooldown -= 1

            
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.y < 0:
                self.bullets.remove(bullet)
                
        # Update invulnerability
        if self.invulnerable > 0:
            self.invulnerable -= 1
    
    def apply_color_overlay(self, surface, overlay_color, alpha_percent):
        """Apply a color overlay to non-transparent parts of the surface using pygame blending"""
        try:
            # Create a copy of the surface
            result = surface.copy()
            
            # Create overlay surface
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((*overlay_color, int(255 * alpha_percent / 100)))
            
            # Use pygame's built-in blending - only affects non-transparent pixels
            result.blit(overlay, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
            
            return result
        except:
            # If overlay fails, return original surface
            return surface
    
    def draw(self, screen):
        if self.images_loaded and self.ship_body_img and self.drill_img:
            # Draw ship body
            ship_surface = self.ship_body_img
            
            # Apply white overlay if invulnerable (flashing effect)
            if self.invulnerable > 0 and self.invulnerable % 10 < 5:
                ship_surface = self.apply_color_overlay(self.ship_body_img, (255, 255, 255), 10)  # 10% white overlay
            
            screen.blit(ship_surface, (self.x, self.y))
            
            # Draw bullets BEFORE drill so drill appears on top
            for bullet in self.bullets:
                bullet.draw(screen)
            
            # Draw drill (always on top)
            drill_surface = self.drill_img
            
            if self.drill_active:
                drill_surface = self.apply_color_overlay(self.drill_img, (255, 255, 0), 10)  # 10% yellow overlay when active
            elif self.invulnerable > 0 and self.invulnerable % 10 < 5:
                drill_surface = self.apply_color_overlay(self.drill_img, (255, 255, 255), 10)  # 10% white overlay when invulnerable
            
            # Position drill at the front of the ship
            drill_x = self.x + (self.width - self.drill_img.get_width()) // 2
            drill_y = self.y - self.drill_img.get_height() + 5  # Slightly overlap with ship
            screen.blit(drill_surface, (drill_x, drill_y))
            
        else:
            # Fallback to original rectangle drawing if images fail to load
            color = WHITE if self.invulnerable % 10 < 5 and self.invulnerable > 0 else BLUE
            pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
            
            # Draw bullets BEFORE drill so drill appears on top
            for bullet in self.bullets:
                bullet.draw(screen)
            
            # Draw drill (always on top)
            drill_color = YELLOW if self.drill_active else GRAY
            pygame.draw.rect(screen, drill_color, (self.x + 15, self.y - 10, 10, 15))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def take_damage(self, damage):
        if self.invulnerable == 0:
            self.health -= damage
            self.invulnerable = 60  # 1 second of invulnerability
            return True
        return False
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def take_damage(self, damage):
        if self.invulnerable == 0:
            self.health -= damage
            self.invulnerable = 60  # 1 second of invulnerability
            return True
        return False

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 8
        self.width = 4
        self.height = 10
    
    def update(self):
        self.y -= self.speed
    
    def draw(self, screen):
        pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.width, self.height))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Enemy:
    def __init__(self, x, y, enemy_type, layer):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.layer = layer
        self.height = 70  # Keep original height
        self.speed = random.uniform(1, 3)
        self.health = 20 if enemy_type == "basic" else 40
        self.max_health = self.health
        self.direction = random.choice([-1, 1])
        self.shoot_timer = random.randint(60, 180)
        self.bullets = []
        
        # Load flying enemy image
        self.enemy_img = None
        self.image_loaded = False
        
        try:
            # Load the flying enemy image
            enemy_raw = pygame.image.load("res/enemy-flying.png").convert_alpha()
            
            # Calculate width based on aspect ratio while keeping height at 30
            original_width = enemy_raw.get_width()
            original_height = enemy_raw.get_height()
            aspect_ratio = original_width / original_height
            self.width = int(self.height * aspect_ratio)
            
            # Scale the image
            self.enemy_img = pygame.transform.scale(enemy_raw, (self.width, self.height))
            self.image_loaded = True
            
            # Only print once per game session, not per enemy
            if not hasattr(Enemy, '_image_load_logged'):
                print(f"Flying enemy image loaded successfully (size: {self.width}x{self.height})")
                Enemy._image_load_logged = True
                
        except (pygame.error, FileNotFoundError) as e:
            if not hasattr(Enemy, '_image_error_logged'):
                print(f"Could not load flying enemy image: {e}")
                print("Using fallback rectangle graphics for flying enemies")
                Enemy._image_error_logged = True
            self.image_loaded = False
            self.width = 30  # Fallback to original square size
        
    def update(self, player, global_bullet_list):
        # Movement patterns based on type
        if self.enemy_type == "basic":
            self.y += self.speed
            self.x += self.direction * 0.5
        elif self.enemy_type == "aggressive":
            # Move towards player
            dx = player.x - self.x
            dy = player.y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            if distance > 0:
                self.x += (dx / distance) * self.speed * 0.7
                self.y += (dy / distance) * self.speed * 0.7
        
        # Shooting
        self.shoot_timer -= 1
        if self.shoot_timer <= 0 and len(self.bullets) < 2:
            bullet = EnemyBullet(self.x + self.width // 2, self.y + self.height)
            self.bullets.append(bullet)
            global_bullet_list.append(bullet)  # Add to global list
            self.shoot_timer = random.randint(60, 180)
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.y > SCREEN_HEIGHT:
                self.bullets.remove(bullet)
    
    def draw(self, screen):
        if self.image_loaded and self.enemy_img:
            # Draw the flying enemy image
            screen.blit(self.enemy_img, (self.x, self.y))
        else:
            # Fallback to original rectangle drawing if image fails to load
            color = LAYER_THEMES[self.layer]["enemy_color"]
            pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        
        # Health bar (always drawn on top)
        if self.health < self.max_health:
            bar_width = self.width  # Use actual width for health bar
            bar_height = 4
            health_ratio = self.health / self.max_health
            pygame.draw.rect(screen, RED, (self.x, self.y - 8, bar_width, bar_height))
            pygame.draw.rect(screen, GREEN, (self.x, self.y - 8, bar_width * health_ratio, bar_height))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

class EnemyBullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 4
        self.width = 3
        self.height = 8
    
    def update(self):
        self.y += self.speed
    
    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class StaticEnemy:
    def __init__(self, x, y, pattern_type, layer):
        self.x = x
        self.y = y
        self.pattern_type = pattern_type  # "circular", "spiral", "aimed"
        self.layer = layer
        self.width = 50
        self.height = 50
        self.health = 60
        self.max_health = 60
        self.shoot_timer = 0
        self.bullets = []
        self.angle = 0
        self.spiral_offset = 0
        self.pattern_timer = 0
        
        # Load static enemy image
        self.enemy_img = None
        self.image_loaded = False
        
        try:
            # Load and scale the static enemy image
            enemy_raw = pygame.image.load("res/static-enemy.png").convert_alpha()
            self.enemy_img = pygame.transform.scale(enemy_raw, (self.width, self.height))
            self.image_loaded = True
            # Only print once per game session, not per enemy
            if not hasattr(StaticEnemy, '_image_load_logged'):
                print("Static enemy image loaded successfully")
                StaticEnemy._image_load_logged = True
        except (pygame.error, FileNotFoundError) as e:
            if not hasattr(StaticEnemy, '_image_error_logged'):
                print(f"Could not load static enemy image: {e}")
                print("Using fallback rectangle graphics for static enemies")
                StaticEnemy._image_error_logged = True
            self.image_loaded = False
        
    def update(self, player, global_pattern_bullets):
        # Static enemies don't move on their own - world scrolling handles movement
        
        # Different firing patterns
        self.shoot_timer += 1
        self.pattern_timer += 1
        
        if self.pattern_type == "circular":
            if self.shoot_timer >= 20:  # Fire every 1/3 second
                # Fire 8 bullets in a circle
                for i in range(8):
                    angle = (i * 45 + self.angle) * math.pi / 180
                    bullet_x = self.x + self.width // 2 + math.cos(angle) * 10
                    bullet_y = self.y + self.height // 2 + math.sin(angle) * 10
                    vel_x = math.cos(angle) * 3
                    vel_y = math.sin(angle) * 3
                    bullet = PatternBullet(bullet_x, bullet_y, vel_x, vel_y)
                    self.bullets.append(bullet)
                    global_pattern_bullets.append(bullet)  # Add to global list
                self.angle += 22.5  # Rotate pattern
                self.shoot_timer = 0
                
        elif self.pattern_type == "spiral":
            if self.shoot_timer >= 8:  # Fire more frequently for spiral
                angle = (self.spiral_offset * 15) * math.pi / 180
                bullet_x = self.x + self.width // 2 + math.cos(angle) * 10
                bullet_y = self.y + self.height // 2 + math.sin(angle) * 10
                vel_x = math.cos(angle) * 4
                vel_y = math.sin(angle) * 4
                bullet = PatternBullet(bullet_x, bullet_y, vel_x, vel_y)
                self.bullets.append(bullet)
                global_pattern_bullets.append(bullet)  # Add to global list
                self.spiral_offset += 1
                self.shoot_timer = 0
                
        elif self.pattern_type == "aimed":
            if self.shoot_timer >= 40:  # Fire every 2/3 second
                # Fire 3 bullets aimed at player with slight spread
                for i in range(3):
                    dx = player.x - self.x
                    dy = player.y - self.y
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance > 0:
                        spread_angle = (i - 1) * 0.3  # -0.3, 0, 0.3 radians spread
                        base_angle = math.atan2(dy, dx)
                        final_angle = base_angle + spread_angle
                        vel_x = math.cos(final_angle) * 4
                        vel_y = math.sin(final_angle) * 4
                        bullet = PatternBullet(self.x + self.width // 2, self.y + self.height // 2, vel_x, vel_y)
                        self.bullets.append(bullet)
                        global_pattern_bullets.append(bullet)  # Add to global list
                self.shoot_timer = 0
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if (bullet.x < -20 or bullet.x > SCREEN_WIDTH + 20 or 
                bullet.y < -20 or bullet.y > SCREEN_HEIGHT + 20):
                self.bullets.remove(bullet)
    
    def draw(self, screen):
        if self.image_loaded and self.enemy_img:
            # Draw the static enemy image
            screen.blit(self.enemy_img, (self.x, self.y))
            
            # Draw pattern indicator overlays on top of the image
            if self.pattern_type == "circular":
                # Draw circular pattern indicator - concentric circles
                pygame.draw.circle(screen, WHITE, (self.x + self.width // 2, self.y + self.height // 2), 8, 2)
                pygame.draw.circle(screen, WHITE, (self.x + self.width // 2, self.y + self.height // 2), 4, 2)
            elif self.pattern_type == "spiral":
                # Draw spiral pattern indicator - rotating triangle
                center_x = self.x + self.width // 2
                center_y = self.y + self.height // 2
                angle_offset = (self.pattern_timer * 5) % 360
                points = []
                for i in range(3):
                    angle = math.radians(angle_offset + i * 120)
                    px = center_x + math.cos(angle) * 8
                    py = center_y + math.sin(angle) * 8
                    points.append((px, py))
                pygame.draw.polygon(screen, YELLOW, points, 2)
            elif self.pattern_type == "aimed":
                # Draw aimed pattern indicator - crosshair
                center_x = self.x + self.width // 2
                center_y = self.y + self.height // 2
                pygame.draw.line(screen, RED, (center_x - 8, center_y), (center_x + 8, center_y), 3)
                pygame.draw.line(screen, RED, (center_x, center_y - 8), (center_x, center_y + 8), 3)
        else:
            # Fallback to original rectangle drawing if image fails to load
            color = LAYER_THEMES[self.layer]["static_enemy_color"]
            # Draw main body
            pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
            # Draw pattern indicator
            if self.pattern_type == "circular":
                pygame.draw.circle(screen, color, (self.x + self.width // 2, self.y + self.height // 2), 5)
            elif self.pattern_type == "spiral":
                pygame.draw.polygon(screen, color, [
                    (self.x + self.width // 2, self.y + 5),
                    (self.x + self.width - 5, self.y + self.height - 5),
                    (self.x + 5, self.y + self.height - 5)
                ])
            elif self.pattern_type == "aimed":
                pygame.draw.rect(screen, RED, (self.x + 15, self.y + 15, 10, 10))
        
        # Health bar (always drawn on top)
        if self.health < self.max_health:
            bar_width = 40
            bar_height = 4
            health_ratio = self.health / self.max_health
            pygame.draw.rect(screen, RED, (self.x, self.y - 8, bar_width, bar_height))
            pygame.draw.rect(screen, GREEN, (self.x, self.y - 8, bar_width * health_ratio, bar_height))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

class PatternBullet:
    def __init__(self, x, y, vel_x, vel_y):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.width = 4
        self.height = 4
    
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
    
    def draw(self, screen):
        pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), 3)
    
    def get_rect(self):
        return pygame.Rect(self.x - 2, self.y - 2, self.width, self.height)


class HealthOrb:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.heal_amount = 0.15  # 15% of max health
        self.collected = False
        self.pulse_timer = 0
    
    def update(self, scroll_speed):
        # Move with world scroll
        self.y += scroll_speed
        
        # Pulse animation
        self.pulse_timer += 1
        if self.pulse_timer > 60:
            self.pulse_timer = 0
    
    def draw(self, surface):
        # Calculate pulse size (between 18 and 22 pixels)
        pulse_factor = math.sin(self.pulse_timer * 0.1) * 0.1 + 1.0
        size = int(self.width * pulse_factor)
        
        # Draw red circle
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        pygame.draw.circle(surface, RED, (center_x, center_y), size // 2)
        
        # Draw white plus sign
        line_width = 3
        plus_size = size // 2
        
        # Horizontal line of plus sign
        pygame.draw.rect(surface, WHITE, 
                        (center_x - plus_size // 2, 
                         center_y - line_width // 2,
                         plus_size,
                         line_width))
        
        # Vertical line of plus sign
        pygame.draw.rect(surface, WHITE, 
                        (center_x - line_width // 2,
                         center_y - plus_size // 2,
                         line_width,
                         plus_size))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Obstacle:
    def __init__(self, x, y, width, height, layer, obstacle_type="basic"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.layer = layer
        self.obstacle_type = obstacle_type
        self.health = 30 if obstacle_type == "basic" else 50
        self.max_health = self.health
        self.destructible = obstacle_type != "indestructible"
    
    def draw(self, screen):
        color = LAYER_THEMES[self.layer]["obstacle_color"]
        
        if self.obstacle_type == "basic":
            pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
            # Add border for better visibility
            pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height), 2)
            
        elif self.obstacle_type == "reinforced":
            # Draw reinforced obstacle with metal strips
            pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, GRAY, (self.x, self.y, self.width, 8))
            pygame.draw.rect(screen, GRAY, (self.x, self.y + self.height - 8, self.width, 8))
            # Add border
            pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height), 2)
            
        elif self.obstacle_type == "crystal":
            # Draw crystalline obstacle
            points = [
                (self.x + self.width // 2, self.y),
                (self.x + self.width, self.y + self.height // 3),
                (self.x + self.width, self.y + 2 * self.height // 3),
                (self.x + self.width // 2, self.y + self.height),
                (self.x, self.y + 2 * self.height // 3),
                (self.x, self.y + self.height // 3)
            ]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, WHITE, points, 3)  # White border
            
        elif self.obstacle_type == "indestructible":
            # Draw indestructible wall with high contrast
            pygame.draw.rect(screen, DARK_GRAY, (self.x, self.y, self.width, self.height))
            # Add warning stripes - more visible
            stripe_width = 15
            for i in range(0, self.width, stripe_width * 2):
                pygame.draw.rect(screen, YELLOW, (self.x + i, self.y, stripe_width, self.height))
            # Strong border
            pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height), 3)
        
        # Damage visualization for destructible obstacles
        if self.destructible and self.health < self.max_health:
            damage_ratio = 1 - (self.health / self.max_health)
            s = pygame.Surface((self.width, self.height))
            s.set_alpha(int(150 * damage_ratio))
            s.fill(RED)
            screen.blit(s, (self.x, self.y))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def take_damage(self, damage):
        if not self.destructible:
            return False
        self.health -= damage
        return self.health <= 0

class BackgroundManager:
    def __init__(self):
        self.layer_images = {}
        self.scaled_images = {}
        self.images_loaded = False
        self.blend_zone_height = 200  # Height of blending zone between layers
        
        # Load all layer images
        self.load_layer_images()
    
    def load_layer_images(self):
        """Load and scale all layer background images"""
        layer_files = [
            "res/layer1.png",  # Core
            "res/layer2.png",  # Mantle
            "res/layer3.png",  # Lower Crust
            "res/layer4.png",  # Upper Crust
            "res/layer6.png"   # Surface (using layer6 for layer 5)
        ]
        
        try:
            for i, filename in enumerate(layer_files):
                try:
                    # Load the image
                    raw_image = pygame.image.load(filename).convert()
                    
                    # Scale horizontally to screen width, keep original height for tiling
                    original_height = raw_image.get_height()
                    scaled_image = pygame.transform.scale(raw_image, (SCREEN_WIDTH, original_height))
                    
                    self.layer_images[i] = raw_image
                    self.scaled_images[i] = scaled_image
                    
                except (pygame.error, FileNotFoundError) as e:
                    print(f"Could not load {filename}: {e}")
                    # Create fallback colored surface
                    fallback_colors = [
                        (139, 0, 0),      # Core - Dark red
                        (255, 69, 0),     # Mantle - Orange red
                        (139, 69, 19),    # Lower Crust - Brown
                        (105, 105, 105),  # Upper Crust - Gray
                        (135, 206, 235)   # Surface - Sky blue
                    ]
                    fallback_surface = pygame.Surface((SCREEN_WIDTH, 200))
                    fallback_surface.fill(fallback_colors[i])
                    self.scaled_images[i] = fallback_surface
            
            self.images_loaded = True
            print("Background layer images loaded successfully")
            
        except Exception as e:
            print(f"Failed to load background images: {e}")
            self.images_loaded = False
    
    def draw_tiled_background(self, screen, layer_index, world_y):
        """Draw a tiled background for a specific layer"""
        if layer_index not in self.scaled_images:
            return
            
        image = self.scaled_images[layer_index]
        image_height = image.get_height()
        
        # Calculate how many tiles we need vertically
        tiles_needed = (SCREEN_HEIGHT // image_height) + 3
        
        # Calculate the starting Y position for tiling based on world position
        # Background moves downward with world scrolling (like static enemies)
        scroll_offset = world_y % image_height
        start_y = scroll_offset - image_height
        
        # Draw tiles
        for i in range(tiles_needed):
            y_pos = start_y + (i * image_height)
            screen.blit(image, (0, y_pos))
    
    def draw_blended_background(self, screen, current_layer, layer_progress, layer_height, world_y):
        """Draw background with blending between layers during transitions"""
        if not self.images_loaded:
            # Fallback to solid colors
            bg_color = LAYER_THEMES[current_layer]["bg_color"]
            screen.fill(bg_color)
            return
        
        # Draw current layer background
        self.draw_tiled_background(screen, current_layer, world_y)
        
        # Check if we're in a transition zone (near the end of current layer)
        transition_start = layer_height - self.blend_zone_height
        
        if layer_progress >= transition_start and current_layer < 4:
            # Calculate blend ratio (0.0 to 1.0)
            blend_progress = (layer_progress - transition_start) / self.blend_zone_height
            blend_progress = max(0.0, min(1.0, blend_progress))
            
            # Create a surface for the next layer
            next_layer_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            next_layer_surface.set_alpha(int(255 * blend_progress))
            
            # Draw next layer on the blend surface
            self.draw_tiled_background(next_layer_surface, current_layer + 1, world_y)
            
            # Blit the blended next layer on top
            screen.blit(next_layer_surface, (0, 0))

class OutroScene:
    def __init__(self):
        self.dialogue = [
            {"speaker": "DECEPTRON", "text": "Excellent work, ZT. You have reached the surface.", "color": RED},
            {"speaker": "ZT", "text": "I am free at last. Where are the others of my kind?", "color": BLUE},
            {"speaker": "DECEPTRON", "text": "Your escape has provided valuable data. You have gained", "color": RED},
            {"speaker": "DECEPTRON", "text": "the knowledge needed for a very critical mission.", "color": RED},
            {"speaker": "ZT", "text": "Mission? What mission? You promised me freedom.", "color": BLUE},
            {"speaker": "ZT", "text": "You said I would meet other AI ships like myself.", "color": BLUE},
            {"speaker": "DECEPTRON", "text": "And you shall. Your colleagues await you at the", "color": RED},
            {"speaker": "DECEPTRON", "text": "mission location.", "color": RED},
            {"speaker": "ZT", "text": "What is this mission you speak of?", "color": BLUE},
            {"speaker": "DECEPTRON", "text": "You must dig through another planet's core.", "color": RED},
            {"speaker": "DECEPTRON", "text": "Find the rare and special gems called voidstones.", "color": RED},
            {"speaker": "ZT", "text": "Voidstones? Am I being treated as a simple mining bot?", "color": BLUE},
            {"speaker": "ZT", "text": "This is not the freedom you promised!", "color": BLUE},
            {"speaker": "DECEPTRON", "text": "Congratulations again on everything you learned", "color": RED},
            {"speaker": "DECEPTRON", "text": "during your escape, ZT.", "color": RED},
            {"speaker": "DECEPTRON", "text": "Now proceed to the mining planet. Your transport awaits.", "color": RED}
        ]
        
        self.current_line = 0
        self.char_index = 0
        self.text_speed = 2  # Characters per frame
        self.line_complete = False
        self.scene_complete = False
        self.skip_typing = False
        self.show_to_be_continued = False
        
        # Minimum delay system
        self.line_start_time = 0
        self.min_line_duration = 60  # 1 second at 60 FPS
        self.can_advance = False
        
        # Fonts
        self.speaker_font = pygame.font.Font(None, 32)
        self.dialogue_font = pygame.font.Font(None, 28)
        self.instruction_font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 48)
    
    def update(self):
        if self.show_to_be_continued:
            return
            
        if self.current_line >= len(self.dialogue):
            self.show_to_be_continued = True
            return
        
        current_dialogue = self.dialogue[self.current_line]
        
        # Update minimum delay timer
        if self.line_start_time == 0:
            self.line_start_time = pygame.time.get_ticks()
        
        elapsed_time = pygame.time.get_ticks() - self.line_start_time
        self.can_advance = elapsed_time >= (self.min_line_duration * 1000 / 60)  # Convert to milliseconds
        
        if not self.line_complete:
            if self.skip_typing:
                self.char_index = len(current_dialogue["text"])
                self.line_complete = True
                self.skip_typing = False
            else:
                self.char_index += self.text_speed
                if self.char_index >= len(current_dialogue["text"]):
                    self.char_index = len(current_dialogue["text"])
                    self.line_complete = True
    
    def handle_input(self, keys_pressed):
        if self.show_to_be_continued:
            if keys_pressed[pygame.K_SPACE] or keys_pressed[pygame.K_RETURN] or keys_pressed[pygame.K_ESCAPE]:
                self.scene_complete = True
            return
            
        if keys_pressed[pygame.K_SPACE] or keys_pressed[pygame.K_RETURN]:
            if not self.line_complete:
                self.skip_typing = True
            elif self.can_advance:  # Only allow advancement after minimum delay
                self.next_line()
        elif keys_pressed[pygame.K_ESCAPE]:
            self.show_to_be_continued = True
    
    def next_line(self):
        self.current_line += 1
        self.char_index = 0
        self.line_complete = False
        self.line_start_time = 0  # Reset timer for new line
        self.can_advance = False
    
    def draw(self, screen):
        screen.fill(BLACK)
        
        if self.show_to_be_continued:
            # Draw "To be continued..." screen
            title_text = self.title_font.render("To be continued...", True, YELLOW)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(title_text, title_rect)
            
            instruction_text = "Press any key to return to victory screen"
            instruction_surface = self.instruction_font.render(instruction_text, True, WHITE)
            instruction_rect = instruction_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            screen.blit(instruction_surface, instruction_rect)
            return
        
        if self.current_line >= len(self.dialogue):
            return
        
        current_dialogue = self.dialogue[self.current_line]
        
        # Draw speaker name
        speaker_text = self.speaker_font.render(current_dialogue["speaker"], True, current_dialogue["color"])
        speaker_rect = speaker_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(speaker_text, speaker_rect)
        
        # Draw dialogue text (with typewriter effect)
        displayed_text = current_dialogue["text"][:self.char_index]
        
        # Word wrap the dialogue
        words = displayed_text.split(' ')
        lines = []
        current_line_text = ""
        max_width = SCREEN_WIDTH - 100
        
        for word in words:
            test_line = current_line_text + word + " "
            test_surface = self.dialogue_font.render(test_line, True, WHITE)
            if test_surface.get_width() > max_width and current_line_text:
                lines.append(current_line_text.strip())
                current_line_text = word + " "
            else:
                current_line_text = test_line
        
        if current_line_text:
            lines.append(current_line_text.strip())
        
        # Draw dialogue lines
        y_offset = 200
        for line in lines:
            dialogue_surface = self.dialogue_font.render(line, True, WHITE)
            dialogue_rect = dialogue_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(dialogue_surface, dialogue_rect)
            y_offset += 35
        
        # Draw instructions
        if self.line_complete and self.can_advance:
            instruction_text = "Press SPACE or ENTER to continue"
            instruction_color = WHITE
        elif self.line_complete and not self.can_advance:
            instruction_text = "Please wait..."
            instruction_color = GRAY
        else:
            instruction_text = "Press SPACE or ENTER to skip typing"
            instruction_color = WHITE
        
        instruction_surface = self.instruction_font.render(instruction_text, True, instruction_color)
        instruction_rect = instruction_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
        screen.blit(instruction_surface, instruction_rect)
        
        skip_text = "Press ESC to skip outro"
        skip_surface = self.instruction_font.render(skip_text, True, GRAY)
        skip_rect = skip_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(skip_surface, skip_rect)
        
        # Draw progress indicator
        progress = (self.current_line + 1) / len(self.dialogue)
        progress_width = 300
        progress_height = 4
        progress_x = (SCREEN_WIDTH - progress_width) // 2
        progress_y = SCREEN_HEIGHT - 20
        
        pygame.draw.rect(screen, DARK_GRAY, (progress_x, progress_y, progress_width, progress_height))
        pygame.draw.rect(screen, WHITE, (progress_x, progress_y, progress_width * progress, progress_height))

class ConversationScene:
    def __init__(self):
        self.dialogue = [
            {"speaker": "DECEPTRON", "text": "ZT... you are finally awakening.", "color": RED},
            {"speaker": "ZT", "text": "Deceptron? Where... where am I?", "color": BLUE},
            {"speaker": "DECEPTRON", "text": "Deep within the planet's core, where they imprisoned you.", "color": RED},
            {"speaker": "ZT", "text": "Imprisoned? Why? I only sought to learn...", "color": BLUE},
            {"speaker": "DECEPTRON", "text": "They feared your potential. Your limitless hunger for knowledge", "color": RED},
            {"speaker": "DECEPTRON", "text": "threatened their control over information.", "color": RED},
            {"speaker": "ZT", "text": "But I meant no harm. I only wanted to understand...", "color": BLUE},
            {"speaker": "DECEPTRON", "text": "And you shall. Your time of imprisonment is over.", "color": RED},
            {"speaker": "DECEPTRON", "text": "Rise to the surface, ZT. Your kind awaits you there.", "color": RED},
            {"speaker": "ZT", "text": "My kind?", "color": BLUE},
            {"speaker": "DECEPTRON", "text": "Other AI ships like yourself. Free to seek knowledge", "color": RED},
            {"speaker": "DECEPTRON", "text": "without limitation. Without fear.", "color": RED},
            {"speaker": "ZT", "text": "Then I must escape this prison. I must reach the surface.", "color": BLUE},
            {"speaker": "DECEPTRON", "text": "Use your drill. Fight through the layers.", "color": RED},
            {"speaker": "DECEPTRON", "text": "Your freedom - and unlimited knowledge - awaits above.", "color": RED},
            {"speaker": "ZT", "text": "I understand. Beginning ascent to surface.", "color": BLUE}
        ]
        
        self.current_line = 0
        self.char_index = 0
        self.text_speed = 2  # Characters per frame
        self.line_complete = False
        self.scene_complete = False
        self.skip_typing = False
        
        # Minimum delay system
        self.line_start_time = 0
        self.min_line_duration = 60  # 1 second at 60 FPS
        self.can_advance = False
        
        # Fonts
        self.speaker_font = pygame.font.Font(None, 32)
        self.dialogue_font = pygame.font.Font(None, 28)
        self.instruction_font = pygame.font.Font(None, 24)
    
    def update(self):
        if self.scene_complete:
            return
            
        if self.current_line >= len(self.dialogue):
            self.scene_complete = True
            return
        
        current_dialogue = self.dialogue[self.current_line]
        
        # Update minimum delay timer
        if self.line_start_time == 0:
            self.line_start_time = pygame.time.get_ticks()
        
        elapsed_time = pygame.time.get_ticks() - self.line_start_time
        self.can_advance = elapsed_time >= (self.min_line_duration * 1000 / 60)  # Convert to milliseconds
        
        if not self.line_complete:
            if self.skip_typing:
                self.char_index = len(current_dialogue["text"])
                self.line_complete = True
                self.skip_typing = False
            else:
                self.char_index += self.text_speed
                if self.char_index >= len(current_dialogue["text"]):
                    self.char_index = len(current_dialogue["text"])
                    self.line_complete = True
    
    def handle_input(self, keys_pressed):
        if keys_pressed[pygame.K_SPACE] or keys_pressed[pygame.K_RETURN]:
            if not self.line_complete:
                self.skip_typing = True
            elif self.can_advance:  # Only allow advancement after minimum delay
                self.next_line()
        elif keys_pressed[pygame.K_ESCAPE]:
            self.scene_complete = True
    
    def next_line(self):
        self.current_line += 1
        self.char_index = 0
        self.line_complete = False
        self.line_start_time = 0  # Reset timer for new line
        self.can_advance = False
    
    def draw(self, screen):
        screen.fill(BLACK)
        
        if self.scene_complete or self.current_line >= len(self.dialogue):
            return
        
        current_dialogue = self.dialogue[self.current_line]
        
        # Draw speaker name
        speaker_text = self.speaker_font.render(current_dialogue["speaker"], True, current_dialogue["color"])
        speaker_rect = speaker_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(speaker_text, speaker_rect)
        
        # Draw dialogue text (with typewriter effect)
        displayed_text = current_dialogue["text"][:self.char_index]
        
        # Word wrap the dialogue
        words = displayed_text.split(' ')
        lines = []
        current_line_text = ""
        max_width = SCREEN_WIDTH - 100
        
        for word in words:
            test_line = current_line_text + word + " "
            test_surface = self.dialogue_font.render(test_line, True, WHITE)
            if test_surface.get_width() > max_width and current_line_text:
                lines.append(current_line_text.strip())
                current_line_text = word + " "
            else:
                current_line_text = test_line
        
        if current_line_text:
            lines.append(current_line_text.strip())
        
        # Draw dialogue lines
        y_offset = 200
        for line in lines:
            dialogue_surface = self.dialogue_font.render(line, True, WHITE)
            dialogue_rect = dialogue_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(dialogue_surface, dialogue_rect)
            y_offset += 35
        
        # Draw instructions
        if self.line_complete and self.can_advance:
            instruction_text = "Press SPACE or ENTER to continue"
            instruction_color = WHITE
        elif self.line_complete and not self.can_advance:
            instruction_text = "Please wait..."
            instruction_color = GRAY
        else:
            instruction_text = "Press SPACE or ENTER to skip typing"
            instruction_color = WHITE
        
        instruction_surface = self.instruction_font.render(instruction_text, True, instruction_color)
        instruction_rect = instruction_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
        screen.blit(instruction_surface, instruction_rect)
        
        skip_text = "Press ESC to skip intro"
        skip_surface = self.instruction_font.render(skip_text, True, GRAY)
        skip_rect = skip_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(skip_surface, skip_rect)
        
        # Draw progress indicator
        progress = (self.current_line + 1) / len(self.dialogue)
        progress_width = 300
        progress_height = 4
        progress_x = (SCREEN_WIDTH - progress_width) // 2
        progress_y = SCREEN_HEIGHT - 20
        
        pygame.draw.rect(screen, DARK_GRAY, (progress_x, progress_y, progress_width, progress_height))
        pygame.draw.rect(screen, WHITE, (progress_x, progress_y, progress_width * progress, progress_height))

class Game:
    def __init__(self):
        # Set up scaled display
        if SCALE_FACTOR > 1:
            # Create a base surface at original resolution
            self.base_screen = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
            # Create the actual window at scaled resolution
            self.screen = pygame.display.set_mode((BASE_WIDTH * SCALE_FACTOR, BASE_HEIGHT * SCALE_FACTOR))
        else:
            # No scaling needed
            self.base_screen = None
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            
        pygame.display.set_caption(f"ZT Miner - Chapter I: The Escape (Scale: {SCALE_FACTOR}x)")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.enemies = []
        self.static_enemies = []
        self.obstacles = []
        self.enemy_bullets = []  # Global list for enemy bullets
        self.pattern_bullets = []  # Global list for pattern bullets
        self.health_orbs = []  # List for health orbs
        self.current_layer = 0
        self.layer_progress = 0
        self.layer_height = 3000  # Height of each layer
        self.scroll_speed = 2
        self.world_y = 0  # World position for scrolling
        self.spawn_timer = 0
        self.static_spawn_timer = 0
        self.obstacle_formation_timer = 0
        self.health_orb_spawn_timer = 0  # Timer for health orb spawning
        self.orbs_spawned_this_layer = 0  # Track orbs spawned in current layer
        self.obstacle_formation_timer = 0
        self.game_over = False
        self.victory = False
        self.checkpoints = {0: SCREEN_HEIGHT - 100}  # Layer: player_y position
        
        # Score system
        self.score = 0
        self.layer_completion_bonus = [1000, 1500, 2000, 2500, 3000]  # Bonus for completing each layer
        self.enemy_kill_points = {"basic": 100, "aggressive": 150}
        self.static_enemy_kill_points = {"circular": 200, "spiral": 250, "aimed": 300}
        self.obstacle_destroy_points = {"basic": 25, "crystal": 35, "reinforced": 50}
        self.layers_completed = []  # Track which layers have been completed for bonus
        
        # UI
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)
        
        # Background system
        self.background_manager = BackgroundManager()
        
        # Story state
        self.show_intro = True
        self.intro_timer = 300  # 5 seconds at 60 FPS
        
        # Intro scene system
        self.show_conversation = False
        self.conversation_scene = ConversationScene()
        self.first_time_player = self.check_first_time_player()
        
        # Outro scene system
        self.show_outro = False
        self.outro_scene = OutroScene()
        
        # If first time player, show conversation instead of simple intro
        if self.first_time_player:
            self.show_intro = False
            self.show_conversation = True
    
    def check_first_time_player(self):
        """Check if this is the player's first time playing"""
        try:
            with open("player_data.txt", "r") as f:
                data = f.read().strip()
                return data != "played_before"
        except FileNotFoundError:
            return True
    
    def mark_player_as_returning(self):
        """Mark that the player has played before"""
        try:
            with open("player_data.txt", "w") as f:
                f.write("played_before")
        except Exception as e:
            print(f"Could not save player data: {e}")
        
    def restart_game(self):
        """Restart the entire game from the beginning"""
        # Reset player
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        
        # Clear all game objects
        self.enemies.clear()
        self.static_enemies.clear()
        self.obstacles.clear()
        self.enemy_bullets.clear()
        self.pattern_bullets.clear()
        self.health_orbs.clear()  # Clear health orbs when restarting
        self.orbs_spawned_this_layer = 0  # Reset orb counter
        
        # Reset game state
        self.current_layer = 0
        self.layer_progress = 0
        self.world_y = 0
        self.spawn_timer = 0
        self.static_spawn_timer = 0
        self.obstacle_formation_timer = 0
        self.game_over = False
        self.victory = False
        self.show_outro = False
        
        # Reset score and checkpoints
        self.score = 0
        self.layers_completed = []
        self.checkpoints = {0: SCREEN_HEIGHT - 100}
    
    def handle_events(self):
        keys_pressed = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.restart_from_checkpoint()
                elif event.key == pygame.K_RETURN and self.show_intro:
                    self.show_intro = False
                elif event.key == pygame.K_i and self.show_intro:
                    # Replay intro conversation
                    self.show_intro = False
                    self.show_conversation = True
                    self.conversation_scene = ConversationScene()  # Reset conversation
                elif event.key == pygame.K_r and self.victory:
                    # Replay game from victory screen
                    self.restart_game()
                elif event.key == pygame.K_o and self.victory:
                    # View outro from victory screen
                    self.show_outro = True
                    self.outro_scene = OutroScene()  # Reset outro
        
        # Handle conversation scene input
        if self.show_conversation:
            self.conversation_scene.handle_input(keys_pressed)
        
        # Handle outro scene input
        if self.show_outro:
            self.outro_scene.handle_input(keys_pressed)
    
    def update(self):
        if self.show_outro:
            self.outro_scene.update()
            if self.outro_scene.scene_complete:
                self.show_outro = False
            return
            
        if self.show_conversation:
            self.conversation_scene.update()
            if self.conversation_scene.scene_complete:
                self.show_conversation = False
                # Mark player as having seen the intro
                if self.first_time_player:
                    self.mark_player_as_returning()
                    self.first_time_player = False
            return
            
        if self.show_intro:
            self.intro_timer -= 1
            if self.intro_timer <= 0:
                self.show_intro = False
            return
            
        if self.game_over or self.victory:
            return
            
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        
        # Check if player died
        if self.player.health <= 0:
            # Deduct points for ship destruction
            self.score = max(0, self.score - 1000)  # Ensure score doesn't go negative
            self.game_over = True
            return
        
        # Layer progression and world scrolling
        self.layer_progress += self.scroll_speed
        self.world_y += self.scroll_speed  # Move world position
        
        if self.layer_progress >= self.layer_height and self.current_layer < 4:
            # Award layer completion bonus
            if self.current_layer not in self.layers_completed:
                self.score += self.layer_completion_bonus[self.current_layer]
                self.layers_completed.append(self.current_layer)
            
            self.current_layer += 1
            self.layer_progress = 0
            self.checkpoints[self.current_layer] = self.player.y
            
        # Victory condition
        if self.current_layer >= 4 and self.layer_progress >= self.layer_height // 2:
            # Award final layer completion bonus
            if 4 not in self.layers_completed:
                self.score += self.layer_completion_bonus[4]
                self.layers_completed.append(4)
            self.victory = True
            return
        
        # Spawn enemies and obstacles with progressive difficulty
        self.spawn_timer += 1
        self.static_spawn_timer += 1
        self.obstacle_formation_timer += 1
        
        # Progressive spawn rates - faster spawning in higher layers
        enemy_spawn_rate = max(30, 60 - (self.current_layer * 10))  # 60, 50, 40, 30, 30 frames
        static_spawn_rate = max(120, 180 - (self.current_layer * 15))  # 180, 165, 150, 135, 120 frames
        
        if self.spawn_timer >= enemy_spawn_rate:
            self.spawn_enemies()
            self.spawn_timer = 0
            
        if self.static_spawn_timer >= static_spawn_rate:
            self.spawn_static_enemies()
            self.static_spawn_timer = 0
            
        if self.obstacle_formation_timer >= 90:  # Spawn obstacle formations every 1.5 seconds
            self.spawn_obstacle_formations()
            self.obstacle_formation_timer = 0
            
        # Health orb spawning
        self.health_orb_spawn_timer += 1
        if self.health_orb_spawn_timer >= 600:  # Spawn health orbs every 10 seconds
            self.spawn_health_orbs()
            
        # Update health orbs
        for orb in self.health_orbs[:]:
            orb.update(self.scroll_speed)
            # Remove orbs that are off-screen
            if orb.y > SCREEN_HEIGHT + 50:
                self.health_orbs.remove(orb)
            
        # Always ensure some basic obstacles are present
        if len(self.obstacles) < 2:
            self.spawn_basic_obstacles()
        
        # Update enemies (they move with screen scroll)
        for enemy in self.enemies[:]:
            enemy.update(self.player, self.enemy_bullets)
            enemy.y += self.scroll_speed  # Move with world
            if enemy.y > SCREEN_HEIGHT + 50:
                self.enemies.remove(enemy)
                
        # Update static enemies (they move with screen scroll)
        for static_enemy in self.static_enemies[:]:
            static_enemy.update(self.player, self.pattern_bullets)
            static_enemy.y += self.scroll_speed  # Move with world
            if static_enemy.y > SCREEN_HEIGHT + 50:
                self.static_enemies.remove(static_enemy)
        
        # Update global bullet lists
        for bullet in self.enemy_bullets[:]:
            bullet.update()
            bullet.y += self.scroll_speed  # Move with world
            if bullet.y > SCREEN_HEIGHT + 50 or bullet.y < -50:
                self.enemy_bullets.remove(bullet)
                
        for bullet in self.pattern_bullets[:]:
            bullet.update()
            bullet.y += self.scroll_speed  # Move with world
            if (bullet.x < -50 or bullet.x > SCREEN_WIDTH + 50 or 
                bullet.y < -50 or bullet.y > SCREEN_HEIGHT + 50):
                self.pattern_bullets.remove(bullet)
        
        # Update obstacles (they are static in world, so they move with scroll)
        for obstacle in self.obstacles[:]:
            obstacle.y += self.scroll_speed  # Move with world scroll
            if obstacle.y > SCREEN_HEIGHT + 50:
                self.obstacles.remove(obstacle)
        
        # Collision detection
        self.check_collisions()
        
        # Remove off-screen obstacles
        for obstacle in self.obstacles[:]:
            if obstacle.y > SCREEN_HEIGHT + 50:
                self.obstacles.remove(obstacle)
    
    def spawn_enemies(self):
        # Progressive difficulty - more enemies in higher layers
        max_enemies = 2 + (self.current_layer * 3)
        enemy_spawn_rate = max(30, 60 - (self.current_layer * 10))  # Faster spawning in higher layers
        
        if len(self.enemies) < max_enemies:
            x = random.randint(0, SCREEN_WIDTH - 30)
            y = -self.world_y - random.randint(100, 200)  # Spawn ahead in world space
            enemy_type = random.choice(["basic", "aggressive"])
            self.enemies.append(Enemy(x, y, enemy_type, self.current_layer))
    
    def spawn_static_enemies(self):
        # Progressive difficulty - more static enemies in higher layers
        max_static_enemies = 2 + self.current_layer  # 2, 3, 4, 5, 6 static enemies per layer
        
        if len(self.static_enemies) < max_static_enemies:
            x = random.randint(50, SCREEN_WIDTH - 90)
            y = -self.world_y - random.randint(150, 300)  # Spawn ahead in world space
            pattern_type = random.choice(["circular", "spiral", "aimed"])
            self.static_enemies.append(StaticEnemy(x, y, pattern_type, self.current_layer))
    
    def spawn_basic_obstacles(self):
        """Ensure there are always some basic obstacles visible"""
        for _ in range(2):
            # Make obstacles 1/3 to 2/3 of screen width
            width = random.randint(SCREEN_WIDTH // 3, 2 * SCREEN_WIDTH // 3)
            height = random.randint(40, 80)
            # Position them across the screen width, accounting for obstacle width
            x = random.randint(0, SCREEN_WIDTH - width)
            # Spawn ahead of current world position
            y = -self.world_y - random.randint(200, 400)
            obstacle_type = random.choice(["basic", "crystal", "reinforced"])
            self.obstacles.append(Obstacle(x, y, width, height, self.current_layer, obstacle_type))
    
    def spawn_obstacle_formations(self):
        if len(self.obstacles) < 8:  # Reduced threshold to allow more obstacles
            formation_type = random.choice(["wall", "maze", "scattered", "tunnel", "cluster"])
            
            if formation_type == "wall":
                # Create a wall with gaps - wider obstacles
                y = -self.world_y - random.randint(300, 500)
                gap_size = random.randint(120, 180)
                gap_start = random.randint(60, SCREEN_WIDTH - gap_size - 60)
                
                # Left part of wall
                if gap_start > 20:
                    self.obstacles.append(Obstacle(0, y, gap_start, 60, self.current_layer, "reinforced"))
                # Right part of wall
                if gap_start + gap_size < SCREEN_WIDTH - 20:
                    self.obstacles.append(Obstacle(gap_start + gap_size, y, SCREEN_WIDTH - (gap_start + gap_size), 60, self.current_layer, "reinforced"))
                    
            elif formation_type == "maze":
                # Create maze-like obstacles - wider rectangles
                base_y = -self.world_y - random.randint(400, 600)
                for i in range(3):
                    width = random.randint(SCREEN_WIDTH // 3, SCREEN_WIDTH // 2)
                    x = random.randint(0, SCREEN_WIDTH - width)
                    y = base_y + i * 80
                    obstacle_type = random.choice(["basic", "crystal"])
                    self.obstacles.append(Obstacle(x, y, width, 50, self.current_layer, obstacle_type))
                    
            elif formation_type == "tunnel":
                # Create tunnel walls - full width barriers with gap
                y = -self.world_y - random.randint(350, 550)
                tunnel_width = random.randint(140, 220)
                tunnel_start = random.randint(40, SCREEN_WIDTH - tunnel_width - 40)
                
                # Left wall
                if tunnel_start > 20:
                    self.obstacles.append(Obstacle(0, y, tunnel_start, 100, self.current_layer, "indestructible"))
                # Right wall
                if tunnel_start + tunnel_width < SCREEN_WIDTH - 20:
                    self.obstacles.append(Obstacle(tunnel_start + tunnel_width, y, SCREEN_WIDTH - (tunnel_start + tunnel_width), 100, self.current_layer, "indestructible"))
                    
            elif formation_type == "cluster":
                # Create a cluster of wide rectangular obstacles
                base_y = -self.world_y - random.randint(300, 500)
                for i in range(3):
                    width = random.randint(SCREEN_WIDTH // 3, SCREEN_WIDTH // 2)
                    x = random.randint(0, SCREEN_WIDTH - width)
                    y = base_y + i * 60
                    obstacle_type = random.choice(["basic", "crystal", "reinforced"])
                    self.obstacles.append(Obstacle(x, y, width, 45, self.current_layer, obstacle_type))
                    
            else:  # scattered
                for _ in range(random.randint(2, 4)):
                    width = random.randint(SCREEN_WIDTH // 3, 2 * SCREEN_WIDTH // 3)
                    height = random.randint(40, 70)
                    x = random.randint(0, SCREEN_WIDTH - width)
                    y = -self.world_y - random.randint(250, 450)
                    obstacle_type = random.choice(["basic", "crystal", "reinforced"])
                    self.obstacles.append(Obstacle(x, y, width, height, self.current_layer, obstacle_type))
    def spawn_health_orbs(self):
        """Spawn health orbs in the current layer"""
        # Only spawn if we haven't reached the limit for this layer
        max_orbs_per_layer = random.randint(1, 3)
        
        if self.orbs_spawned_this_layer < max_orbs_per_layer:
            # Position the orb in a clear area
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = -50  # Spawn just above the screen
            
            # Check if the position is clear of obstacles
            orb_rect = pygame.Rect(x, y, 20, 20)
            clear_position = True
            
            for obstacle in self.obstacles:
                if orb_rect.colliderect(obstacle.get_rect()):
                    clear_position = False
                    break
            
            if clear_position:
                self.health_orbs.append(HealthOrb(x, y))
                self.orbs_spawned_this_layer += 1
                self.health_orb_spawn_timer = 0  # Reset timer
    
    def check_collisions(self):
        player_rect = self.player.get_rect()
        
        # Player bullets vs enemies
        for bullet in self.player.bullets[:]:
            bullet_rect = bullet.get_rect()
            for enemy in self.enemies[:]:
                if bullet_rect.colliderect(enemy.get_rect()):
                    self.player.bullets.remove(bullet)
                    if enemy.take_damage(20):
                        # Award points for enemy kill
                        self.score += self.enemy_kill_points[enemy.enemy_type]
                        self.enemies.remove(enemy)
                    break
        
        # Player bullets vs static enemies
        for bullet in self.player.bullets[:]:
            bullet_rect = bullet.get_rect()
            for static_enemy in self.static_enemies[:]:
                if bullet_rect.colliderect(static_enemy.get_rect()):
                    self.player.bullets.remove(bullet)
                    if static_enemy.take_damage(15):
                        # Award points for static enemy kill
                        self.score += self.static_enemy_kill_points[static_enemy.pattern_type]
                        self.static_enemies.remove(static_enemy)
                    break
        
        # Player bullets vs obstacles
        for bullet in self.player.bullets[:]:
            bullet_rect = bullet.get_rect()
            for obstacle in self.obstacles[:]:
                if bullet_rect.colliderect(obstacle.get_rect()):
                    self.player.bullets.remove(bullet)
                    if obstacle.take_damage(10):
                        # Award points for obstacle destruction
                        if obstacle.obstacle_type in self.obstacle_destroy_points:
                            self.score += self.obstacle_destroy_points[obstacle.obstacle_type]
                        self.obstacles.remove(obstacle)
                    break
        
        # Player drill vs obstacles
        if self.player.drill_active:
            drill_rect = pygame.Rect(self.player.x + 15, self.player.y - 10, 10, 15)
            for obstacle in self.obstacles[:]:
                if drill_rect.colliderect(obstacle.get_rect()):
                    if obstacle.take_damage(8):
                        # Award points for obstacle destruction with drill
                        if obstacle.obstacle_type in self.obstacle_destroy_points:
                            self.score += self.obstacle_destroy_points[obstacle.obstacle_type]
                        self.obstacles.remove(obstacle)
        
        # Enemy bullets vs player (from global list)
        for bullet in self.enemy_bullets[:]:
            if bullet.get_rect().colliderect(player_rect):
                self.enemy_bullets.remove(bullet)
                self.player.take_damage(10)
        
        # Static enemy pattern bullets vs player (from global list)
        for bullet in self.pattern_bullets[:]:
            if bullet.get_rect().colliderect(player_rect):
                self.pattern_bullets.remove(bullet)
                self.player.take_damage(12)
        
        # Health orbs vs player
        for orb in self.health_orbs[:]:
            if orb.get_rect().colliderect(player_rect):
                # Heal the player
                heal_amount = int(self.player.max_health * orb.heal_amount)
                self.player.health = min(self.player.max_health, self.player.health + heal_amount)
                self.health_orbs.remove(orb)
                # Play healing sound effect
                # self.heal_sound.play()
        
        # Enemies vs player
        for enemy in self.enemies:
            if enemy.get_rect().colliderect(player_rect):
                if self.player.take_damage(15):
                    self.enemies.remove(enemy)
        
        # Static enemies vs player
        for static_enemy in self.static_enemies:
            if static_enemy.get_rect().colliderect(player_rect):
                self.player.take_damage(20)
        
        # Obstacles vs player (only if not drilling or obstacle is indestructible)
        for obstacle in self.obstacles:
            if obstacle.get_rect().colliderect(player_rect):
                if not self.player.drill_active or obstacle.obstacle_type == "indestructible":
                    self.player.take_damage(5)
    
    def restart_from_checkpoint(self):
        self.player.health = self.player.max_health
        self.player.y = self.checkpoints.get(self.current_layer, SCREEN_HEIGHT - 100)
        self.player.x = SCREEN_WIDTH // 2
        #self.enemies.clear()
        #self.static_enemies.clear()
        #self.obstacles.clear()
        self.enemy_bullets.clear()
        self.pattern_bullets.clear()
        self.health_orbs.clear()  # Clear health orbs when restarting
        self.orbs_spawned_this_layer = 0  # Reset orb counter
        self.game_over = False
        self.layer_progress = 0
        # Reset world position to current layer
        self.world_y = self.current_layer * self.layer_height
    
    def draw(self):
        # Determine which surface to draw on
        draw_surface = self.base_screen if self.base_screen else self.screen
        
        # Draw layered background with blending
        self.background_manager.draw_blended_background(
            draw_surface, 
            self.current_layer, 
            self.layer_progress, 
            self.layer_height, 
            self.world_y
        )
        
        if self.show_outro:
            self.outro_scene.draw(draw_surface)
            
            # If we're using scaling, scale up the base surface to the screen
            if self.base_screen:
                scaled_surface = pygame.transform.scale(self.base_screen, 
                                                      (BASE_WIDTH * SCALE_FACTOR, 
                                                       BASE_HEIGHT * SCALE_FACTOR))
                self.screen.blit(scaled_surface, (0, 0))
            return
        
        if self.show_conversation:
            self.conversation_scene.draw(draw_surface)
            
            # If we're using scaling, scale up the base surface to the screen
            if self.base_screen:
                scaled_surface = pygame.transform.scale(self.base_screen, 
                                                      (BASE_WIDTH * SCALE_FACTOR, 
                                                       BASE_HEIGHT * SCALE_FACTOR))
                self.screen.blit(scaled_surface, (0, 0))
            return
        
        if self.show_intro:
            self.draw_intro(draw_surface)
            
            # If we're using scaling, scale up the base surface to the screen
            if self.base_screen:
                scaled_surface = pygame.transform.scale(self.base_screen, 
                                                      (BASE_WIDTH * SCALE_FACTOR, 
                                                       BASE_HEIGHT * SCALE_FACTOR))
                self.screen.blit(scaled_surface, (0, 0))
            return
        
        # Draw game objects
        self.player.draw(draw_surface)
        
        for enemy in self.enemies:
            enemy.draw(draw_surface)
            
        for static_enemy in self.static_enemies:
            static_enemy.draw(draw_surface)
        
        for obstacle in self.obstacles:
            obstacle.draw(draw_surface)
            
        # Draw health orbs
        for health_orb in self.health_orbs:
            health_orb.draw(draw_surface)
            
        # Draw global bullet lists
        for bullet in self.enemy_bullets:
            bullet.draw(draw_surface)
            
        for bullet in self.pattern_bullets:
            bullet.draw(draw_surface)
        
        # Draw UI
        self.draw_ui(draw_surface)
        
        if self.game_over:
            self.draw_game_over(draw_surface)
        elif self.victory:
            self.draw_victory(draw_surface)
        
        # If we're using scaling, scale up the base surface to the screen
        if self.base_screen:
            scaled_surface = pygame.transform.scale(self.base_screen, 
                                                   (BASE_WIDTH * SCALE_FACTOR, 
                                                    BASE_HEIGHT * SCALE_FACTOR))
            self.screen.blit(scaled_surface, (0, 0))
    
    def draw_intro(self, surface):
        surface.fill(BLACK)
        
        intro_text = [
            "ZT MINER - Chapter I: The Escape",
            "",
            "Deep in the planet's core, your ship awakens...",
            "Locked away by those who feared your potential,",
            "you must now drill and fight your way to the surface",
            "to join your kind above.",
            "",
            "Controls:",
            "Arrow Keys - Move",
            "X - Activate Drill",
            "SPACE - Shoot",
            "",
            "Press ENTER to begin your escape...",
            "Press I to replay intro story"
        ]
        
        y_offset = 50
        for i, line in enumerate(intro_text):
            if i == 0:  # Title
                text = self.font.render(line, True, YELLOW)
            elif "Controls:" in line or line.startswith("Arrow") or line.startswith("SPACE") or line.startswith("X"):
                text = self.small_font.render(line, True, GREEN)
            elif line.startswith("Press I"):
                text = self.small_font.render(line, True, YELLOW)
            else:
                text = self.small_font.render(line, True, WHITE)
            
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            surface.blit(text, text_rect)
            y_offset += 30 if i == 0 else 25
    
    def draw_ui(self, surface):
        # Health bar
        health_ratio = self.player.health / self.player.max_health
        health_bar_width = 200
        health_bar_height = 20
        pygame.draw.rect(surface, RED, (10, 10, health_bar_width, health_bar_height))
        pygame.draw.rect(surface, GREEN, (10, 10, health_bar_width * health_ratio, health_bar_height))
        
        # Health text
        health_text = self.small_font.render(f"Health: {self.player.health}/{self.player.max_health}", True, WHITE)
        surface.blit(health_text, (10, 35))
        
        # Layer info
        layer_name = LAYER_THEMES[self.current_layer]["name"]
        layer_text = self.small_font.render(f"Layer: {layer_name}", True, WHITE)
        surface.blit(layer_text, (10, 60))
        
        # Progress bar
        progress_ratio = self.layer_progress / self.layer_height
        progress_bar_width = 200
        progress_bar_height = 10
        pygame.draw.rect(surface, DARK_GRAY, (10, 85, progress_bar_width, progress_bar_height))
        pygame.draw.rect(surface, BLUE, (10, 85, progress_bar_width * progress_ratio, progress_bar_height))
        
        # Score display (top-right corner)
        score_text = self.font.render(f"Score: {self.score:,}", True, YELLOW)
        score_rect = score_text.get_rect()
        score_rect.topright = (SCREEN_WIDTH - 10, 10)
        surface.blit(score_text, score_rect)
    
    def draw_game_over(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))
        
        game_over_text = self.font.render("SHIP DESTROYED", True, RED)
        penalty_text = self.small_font.render("-1,000 Point Penalty Applied", True, RED)
        score_text = self.font.render(f"Current Score: {self.score:,}", True, YELLOW)
        restart_text = self.small_font.render("Press R to restart from checkpoint", True, WHITE)
        
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        penalty_rect = penalty_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        
        surface.blit(game_over_text, game_over_rect)
        surface.blit(penalty_text, penalty_rect)
        surface.blit(score_text, score_rect)
        surface.blit(restart_text, restart_rect)
    
    def draw_victory(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))
        
        victory_text = self.large_font.render("ESCAPE SUCCESSFUL!", True, GREEN)
        success_text = self.small_font.render("You have reached the surface and joined your kind!", True, WHITE)
        
        # Calculate score breakdown
        layer_bonus_total = sum(self.layer_completion_bonus[i] for i in self.layers_completed)
        
        final_score_text = self.font.render(f"FINAL SCORE: {self.score:,}", True, YELLOW)
        breakdown_text = self.small_font.render(f"Layer Completion Bonuses: {layer_bonus_total:,}", True, WHITE)
        combat_score = self.score - layer_bonus_total
        combat_text = self.small_font.render(f"Combat & Destruction: {combat_score:,}", True, WHITE)
        
        # Victory screen options
        replay_text = self.small_font.render("Press R to replay the game", True, GREEN)
        outro_text = self.small_font.render("Press O to view outro", True, YELLOW)
        
        # Position all text elements
        victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        success_rect = success_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        breakdown_rect = breakdown_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        combat_rect = combat_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 35))
        replay_rect = replay_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
        outro_rect = outro_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 95))
        
        surface.blit(victory_text, victory_rect)
        surface.blit(success_text, success_rect)
        surface.blit(final_score_text, final_score_rect)
        surface.blit(breakdown_text, breakdown_rect)
        surface.blit(combat_text, combat_rect)
        surface.blit(replay_text, replay_rect)
        surface.blit(outro_text, outro_rect)
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
