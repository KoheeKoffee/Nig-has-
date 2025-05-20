import pygame
import sys
import os
import subprocess
import json
from characters import Knight

pygame.init()
pygame.mixer.init()  # Initialize the mixer module

WINDOW_SIZE = (1280, 720)  
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Two Players")

# Load master and music volume from settings
try:
    with open('settings.json', 'r') as f:
        settings = json.load(f)
        master_volume = settings.get('master_volume', 0.3)
        music_volume = settings.get('music_volume', 0.3)
except:
    master_volume = 0.3
    music_volume = 0.3

DEBUG_SHOW_RECTS = True  # Set to False to hide the core rects

# Camera variables
camera_offset = [0, 0]
CAMERA_BOTTOM_LIMIT = 500  # Point below which camera won't follow
CAMERA_SMOOTHING = 0.05  # Reduced from 0.1 for smoother camera

# Background variables
BACKGROUND_PARALLAX = 0.3  # Reduced from 0.5 for less dramatic movement
BACKGROUND_SCALE = 1.5  # Scale factor for background

# Pause button constants
PAUSE_BUTTON_SIZE = 40
PAUSE_BUTTON_PADDING = 20
PAUSE_BUTTON_POS = (WINDOW_SIZE[0] - PAUSE_BUTTON_SIZE - PAUSE_BUTTON_PADDING, PAUSE_BUTTON_PADDING)

bgm = pygame.mixer.Sound("bgm_sample.mp3")
bgm.set_volume(master_volume * music_volume)  # Use both master_volume and music_volume from settings
bgm.play(-1)  

# Load and scale background
background = pygame.image.load("bg.png")
bg_width = int(WINDOW_SIZE[0] * BACKGROUND_SCALE)
bg_height = int(WINDOW_SIZE[1] * BACKGROUND_SCALE)
background = pygame.transform.scale(background, (bg_width, bg_height))
background_rect = background.get_rect()

# Calculate background boundaries
BG_MIN_X = -background_rect.width + WINDOW_SIZE[0]
BG_MAX_X = 0
BG_MIN_Y = -background_rect.height + WINDOW_SIZE[1]
BG_MAX_Y = 0

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
TRANSPARENT_BLACK = (0, 0, 0, 128)  # Added transparent black color

PLAYER_SIZE = 50
INITIAL_POS1 = [280, 300]
INITIAL_POS2 = [950, 300]
PLAYER_SPEED = 5
GRAVITY = 0.6
REDUCED_GRAVITY = 0.1  # Added reduced gravity for below main platform
JUMP_SPEED = -15
VOID_Y = 900  # Changed to match window height
VOID_DAMAGE = 20

MAX_HEALTH = 100
HEALTH_BAR_WIDTH = 200
HEALTH_BAR_HEIGHT = 20
HEALTH_BAR_P1_POS = (WINDOW_SIZE[0]//2 - HEALTH_BAR_WIDTH - 350, 30)
HEALTH_BAR_P2_POS = (WINDOW_SIZE[0]//2 + 350, 30)

GAME_DURATION = 60

running = True
paused = False
game_over = False
clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)
timer_font = pygame.font.Font(None, 48)
countdown_font = pygame.font.Font(None, 150)
pause_font = pygame.font.Font(None, 74)
victory_font = pygame.font.Font(None, 100)

# Button dimensions
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_PADDING = 20

# Define platforms in world coordinates
platforms = [
    pygame.Rect(160, 500, 960, 20),
    pygame.Rect(280, 350, 120, 20),
    pygame.Rect(580, 250, 120, 20),
    pygame.Rect(880, 350, 120, 20)
]

# Define controls
controls_p1 = {
    'left': pygame.K_a,
    'right': pygame.K_d,
    'jump': pygame.K_w,
    'drop': pygame.K_s,
    'attack1': pygame.K_g,
    'attack2': pygame.K_h
}

controls_p2 = {
    'left': pygame.K_LEFT,
    'right': pygame.K_RIGHT,
    'jump': pygame.K_UP,
    'drop': pygame.K_DOWN,
    'attack1': pygame.K_KP1,
    'attack2': pygame.K_KP2
}

# Create knights
knight1 = Knight(INITIAL_POS1[0], INITIAL_POS1[1], controls_p1, BLUE, INITIAL_POS1, VOID_Y, MAX_HEALTH)
knight2 = Knight(INITIAL_POS2[0], INITIAL_POS2[1], controls_p2, RED, INITIAL_POS2, VOID_Y, MAX_HEALTH)
knight2.facing_left = True  # Make player 2 face left by default

def world_to_screen(pos):
    return [pos[0] - camera_offset[0], pos[1] - camera_offset[1]]

def update_camera():
    # Calculate the midpoint between players
    mid_x = (knight1.rect.centerx + knight2.rect.centerx) / 2
    mid_y = (knight1.rect.centery + knight2.rect.centery) / 2
    
    # Update camera position to center on midpoint
    target_x = mid_x - WINDOW_SIZE[0] / 2
    target_y = mid_y - WINDOW_SIZE[1] / 2
    
    # Don't follow below the bottom limit
    if mid_y > CAMERA_BOTTOM_LIMIT:
        target_y = CAMERA_BOTTOM_LIMIT - WINDOW_SIZE[1] / 2
        
    # Smoother camera movement
    camera_offset[0] += (target_x - camera_offset[0]) * CAMERA_SMOOTHING
    camera_offset[1] += (target_y - camera_offset[1]) * CAMERA_SMOOTHING

def draw_background():
    # Calculate background position based on camera offset and parallax effect
    bg_x = max(BG_MIN_X, min(BG_MAX_X, -camera_offset[0] * BACKGROUND_PARALLAX))
    bg_y = max(BG_MIN_Y, min(BG_MAX_Y, -camera_offset[1] * BACKGROUND_PARALLAX))
    
    # Draw background with parallax effect and boundaries
    screen.blit(background, (bg_x, bg_y))

def draw_pause_button():
    pause_rect = pygame.Rect(PAUSE_BUTTON_POS[0], PAUSE_BUTTON_POS[1], PAUSE_BUTTON_SIZE, PAUSE_BUTTON_SIZE)
    pygame.draw.rect(screen, BLACK, pause_rect, 2)
    pygame.draw.rect(screen, (200, 200, 200), pause_rect)
    
    # Draw pause icon
    bar_width = 4
    bar_height = 20
    bar_padding = 8
    pygame.draw.rect(screen, BLACK, (PAUSE_BUTTON_POS[0] + bar_padding, 
                                   PAUSE_BUTTON_POS[1] + (PAUSE_BUTTON_SIZE - bar_height)//2,
                                   bar_width, bar_height))
    pygame.draw.rect(screen, BLACK, (PAUSE_BUTTON_POS[0] + PAUSE_BUTTON_SIZE - bar_padding - bar_width,
                                   PAUSE_BUTTON_POS[1] + (PAUSE_BUTTON_SIZE - bar_height)//2,
                                   bar_width, bar_height))
    return pause_rect

def draw_button(text, position, width=BUTTON_WIDTH, height=BUTTON_HEIGHT):
    button_rect = pygame.Rect(position[0], position[1], width, height)
    pygame.draw.rect(screen, BLACK, button_rect, 2)
    pygame.draw.rect(screen, (200, 200, 200), button_rect)
    
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)
    return button_rect

def restart_game():
    knight1.reset()
    knight2.reset()
    knight2.facing_left = True  # Reset player 2 to face left
    global game_over, game_started, current_number, countdown_start, start_time
    game_over = False
    game_started = False
    current_number = 0
    countdown_start = pygame.time.get_ticks()
    bgm.stop()
    bgm.play(-1)

# Countdown sequence
countdown_numbers = ["3", "2", "1", "FIGHT!"]
countdown_duration = 1000  # 1 second per number
game_started = False
countdown_start = pygame.time.get_ticks()
current_number = 0

while running:
    # Check for volume changes
    try:
        with open('settings.json', 'r') as f:
            settings = json.load(f)
            new_master_volume = settings.get('master_volume', master_volume)
            new_music_volume = settings.get('music_volume', music_volume)
            if new_master_volume != master_volume or new_music_volume != music_volume:
                master_volume = new_master_volume
                music_volume = new_music_volume
                bgm.set_volume(master_volume * music_volume)
    except:
        pass

    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if game_started and not game_over:
                pause_rect = pygame.Rect(PAUSE_BUTTON_POS[0], PAUSE_BUTTON_POS[1], PAUSE_BUTTON_SIZE, PAUSE_BUTTON_SIZE)
                if pause_rect.collidepoint(mouse_pos):
                    paused = not paused
            elif paused:
                paused = False
            elif game_over:
                rematch_rect = pygame.Rect((WINDOW_SIZE[0]//2 - BUTTON_WIDTH//2, 
                                          WINDOW_SIZE[1]//2 + 50), 
                                         (BUTTON_WIDTH, BUTTON_HEIGHT))
                main_menu_rect = pygame.Rect((WINDOW_SIZE[0]//2 - BUTTON_WIDTH//2,
                                            WINDOW_SIZE[1]//2 + 120),
                                           (BUTTON_WIDTH, BUTTON_HEIGHT))
                if rematch_rect.collidepoint(mouse_pos):
                    restart_game()
                elif main_menu_rect.collidepoint(mouse_pos):
                    bgm.stop()
                    pygame.quit()
                    subprocess.run(['python', 'Main_menu.py'])
                    sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                paused = not paused

    # Show countdown screen
    if not game_started:
        screen.fill(WHITE)
        # Draw background with parallax effect during countdown
        draw_background()
        
        if current_number < len(countdown_numbers):
            number = countdown_numbers[current_number]
            text = countdown_font.render(number, True, BLACK)
            text_rect = text.get_rect(center=(WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2))
            screen.blit(text, text_rect)
            
            if current_time - countdown_start >= countdown_duration:
                current_number += 1
                countdown_start = current_time
                
            pygame.display.flip()
            clock.tick(60)
            continue
        else:
            game_started = True
            start_time = pygame.time.get_ticks()

    # Check for game over conditions
    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
    time_left = max(0, GAME_DURATION - elapsed_time)
    
    if knight1.health <= 0 or knight2.health <= 0 or time_left <= 0:
        game_over = True
        screen.fill(BLACK)
        
        if knight1.health <= 0:
            winner_text = "PLAYER 2 WINS!"
        elif knight2.health <= 0:
            winner_text = "PLAYER 1 WINS!"
        elif time_left <= 0:
            if knight1.health > knight2.health:
                winner_text = "PLAYER 1 WINS!"
            elif knight2.health > knight1.health:
                winner_text = "PLAYER 2 WINS!"
            else:
                winner_text = "IT'S A TIE!!"

        text = victory_font.render(winner_text, True, WHITE)
        text_rect = text.get_rect(center=(WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2 - 50))
        screen.blit(text, text_rect)

        rematch_rect = draw_button("REMATCH", 
                                 (WINDOW_SIZE[0]//2 - BUTTON_WIDTH//2, 
                                  WINDOW_SIZE[1]//2 + 50))
                                  
        main_menu_rect = draw_button("MAIN MENU",
                                   (WINDOW_SIZE[0]//2 - BUTTON_WIDTH//2,
                                    WINDOW_SIZE[1]//2 + 120))

        pygame.display.flip()
        clock.tick(60)
        continue

    if paused:
        # Create a semi-transparent black overlay
        pause_overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        pause_overlay.fill(TRANSPARENT_BLACK)
        screen.blit(pause_overlay, (0, 0))
        
        pause_text = pause_font.render("GAME PAUSED", True, WHITE)
        pause_rect = pause_text.get_rect(center=(WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2))
        screen.blit(pause_text, pause_rect)
        
        resume_text = font.render("Press Esc to Continue", True, WHITE)
        resume_rect = resume_text.get_rect(center=(WINDOW_SIZE[0]//2, WINDOW_SIZE[1]-50))
        screen.blit(resume_text, resume_rect)
        
        pygame.display.flip()
        clock.tick(60)
        continue

    if not game_over and not paused and game_started:
        keys = pygame.key.get_pressed()
        
        # Handle input
        knight1.handle_input(keys)
        knight2.handle_input(keys)
        
        # Update knights
        knight1.update(platforms, WINDOW_SIZE)
        knight2.update(platforms, WINDOW_SIZE)
        


        # Update camera
        update_camera()

    # Drawing
    screen.fill(WHITE)
    draw_background()
    
    # Draw platforms
    screen_platforms = [pygame.Rect(p.x - camera_offset[0], p.y - camera_offset[1], p.width, p.height) 
                       for p in platforms]
    for platform in screen_platforms:
        pygame.draw.rect(screen, BLACK, platform)
    
    # Draw knights with camera offset and debug rects
    knight1.draw(screen, font, "P1", WINDOW_SIZE, camera_offset, show_rect=DEBUG_SHOW_RECTS)
    knight2.draw(screen, font, "P2", WINDOW_SIZE, camera_offset, show_rect=DEBUG_SHOW_RECTS)
    
    # Draw UI
    knight1.draw_health_bar(screen, HEALTH_BAR_P1_POS, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT, font, "PLAYER 1")
    knight2.draw_health_bar(screen, HEALTH_BAR_P2_POS, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT, font, "PLAYER2")

    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
    time_left = max(0, GAME_DURATION - elapsed_time)
    timer_text = timer_font.render(str(time_left), True, BLACK)
    timer_rect = timer_text.get_rect(center=(WINDOW_SIZE[0]//2, 30))
    screen.blit(timer_text, timer_rect)

    # Draw pause button (fixed on screen)
    if game_started and not game_over:
        draw_pause_button()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
