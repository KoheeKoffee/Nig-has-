import pygame
import sys
import os
import subprocess
import json
import math


pygame.init()
pygame.mixer.init()


WINDOW_SIZE = (1280, 720)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Blue Vs Red: ft. Dante from DMC")


background = pygame.image.load("background_menu.png")
background = pygame.transform.scale(background, WINDOW_SIZE)
background_rect = background.get_rect(center=(WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2))


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
TRANSPARENT_BLACK = (0, 0, 0, 128)


title_font = pygame.font.Font("alagard.ttf", 100)
menu_font = pygame.font.Font("alagard.ttf", 50)
settings_font = pygame.font.Font(None, 36)


BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_PADDING = 20
MENU_BOX_WIDTH = 300
MENU_BOX_HEIGHT = 350
BUTTON_HOVER_OFFSET = 10

SETTINGS_WIDTH = 400
SETTINGS_HEIGHT = 400
SLIDER_WIDTH = 300
SLIDER_HEIGHT = 20
MASTER_SLIDER_Y = WINDOW_SIZE[1]//2 - 100
MUSIC_SLIDER_Y = WINDOW_SIZE[1]//2

def get_volume_settings():
    try:
        with open('settings.json', 'r') as f:
            settings = json.load(f)
            return (settings.get('master_volume', 0.3), 
                   settings.get('music_volume', 0.3))
    except:
        return 0.3, 0.3

def initialize_settings():
    master_volume, music_volume = get_volume_settings()
    settings = {
        'master_volume': master_volume,
        'music_volume': music_volume
    }
    with open('settings.json', 'w') as f:
        json.dump(settings, f)
    return master_volume, music_volume, settings

master_volume, music_volume, settings = initialize_settings()

def save_volume_settings(master_vol, music_vol):
    settings['master_volume'] = master_vol
    settings['music_volume'] = music_vol
    with open('settings.json', 'w') as f:
        json.dump(settings, f)

def draw_button(text, y_position):
    mouse_pos = pygame.mouse.get_pos()
    button_rect = pygame.Rect((WINDOW_SIZE[0] - BUTTON_WIDTH) // 2, 
                            y_position,
                            BUTTON_WIDTH, 
                            BUTTON_HEIGHT)
    
    is_hovered = button_rect.collidepoint(mouse_pos)
    
    if is_hovered:
        y_position -= BUTTON_HOVER_OFFSET
        button_rect.y = y_position
        text_color = YELLOW
    else:
        text_color = WHITE

    text_surface = menu_font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)
    
    return button_rect

def draw_settings_window():
    settings_rect = pygame.Rect(
        (WINDOW_SIZE[0] - SETTINGS_WIDTH)//2,
        (WINDOW_SIZE[1] - SETTINGS_HEIGHT)//2,
        SETTINGS_WIDTH,
        SETTINGS_HEIGHT
    )
    pygame.draw.rect(screen, WHITE, settings_rect)
    pygame.draw.rect(screen, BLACK, settings_rect, 2)
    
    title = settings_font.render("Settings", True, BLACK)
    title_rect = title.get_rect(center=(WINDOW_SIZE[0]//2, settings_rect.top + 30))
    screen.blit(title, title_rect)
    
    master_text = settings_font.render("Master Volume", True, BLACK)
    master_rect = master_text.get_rect(center=(WINDOW_SIZE[0]//2, MASTER_SLIDER_Y - 30))
    screen.blit(master_text, master_rect)
    
    master_slider_bg = pygame.Rect(
        (WINDOW_SIZE[0] - SLIDER_WIDTH)//2,
        MASTER_SLIDER_Y,
        SLIDER_WIDTH,
        SLIDER_HEIGHT
    )
    pygame.draw.rect(screen, GRAY, master_slider_bg)
    
    master_handle_x = ((WINDOW_SIZE[0] - SLIDER_WIDTH)//2) + (master_volume * SLIDER_WIDTH)
    master_handle = pygame.Rect(master_handle_x - 5, MASTER_SLIDER_Y - 5, 10, SLIDER_HEIGHT + 10)
    pygame.draw.rect(screen, BLACK, master_handle)

    music_text = settings_font.render("Music Volume", True, BLACK)
    music_rect = music_text.get_rect(center=(WINDOW_SIZE[0]//2, MUSIC_SLIDER_Y - 30))
    screen.blit(music_text, music_rect)
    
    music_slider_bg = pygame.Rect(
        (WINDOW_SIZE[0] - SLIDER_WIDTH)//2,
        MUSIC_SLIDER_Y,
        SLIDER_WIDTH,
        SLIDER_HEIGHT
    )
    pygame.draw.rect(screen, GRAY, music_slider_bg)
    
    music_handle_x = ((WINDOW_SIZE[0] - SLIDER_WIDTH)//2) + (music_volume * SLIDER_WIDTH)
    music_handle = pygame.Rect(music_handle_x - 5, MUSIC_SLIDER_Y - 5, 10, SLIDER_HEIGHT + 10)
    pygame.draw.rect(screen, BLACK, music_handle)
    
    return (master_slider_bg, music_slider_bg), settings_rect

def main_menu():
    global master_volume, music_volume

    menu_bgm = pygame.mixer.Sound("bgm_menu_sample.mp3")
    menu_bgm.set_volume(master_volume * music_volume)
    menu_bgm.play(-1)
    
    settings_active = False
    dragging_master = False
    dragging_music = False
    
    title_pulse = 0
    
    while True:
        screen.blit(background, background_rect)
        
        menu_box = pygame.Surface((MENU_BOX_WIDTH, MENU_BOX_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(menu_box, (0, 0, 0, 180), menu_box.get_rect())
        menu_box_rect = menu_box.get_rect(center=(WINDOW_SIZE[0]//2, 500))
        screen.blit(menu_box, menu_box_rect)
        
        title_pulse = (title_pulse + 0.01) % (2 * math.pi)
        
        layers = 3
        base_offset = 8
        layer_spacing = 3
        
        title_text1 = "Knights of"
        title_text2 = "the Reject Table"
        
        for i in range(layers):
            offset = base_offset - (i * layer_spacing)
            shadow_color = tuple(max(0, min(255, c - i * 40)) for c in (128, 128, 128))
            
            shadow_surface1 = title_font.render(title_text1, True, shadow_color)
            shadow_rect1 = shadow_surface1.get_rect(center=(WINDOW_SIZE[0]//2 + offset, 80 + offset))
            screen.blit(shadow_surface1, shadow_rect1)
            
            shadow_surface2 = title_font.render(title_text2, True, shadow_color)
            shadow_rect2 = shadow_surface2.get_rect(center=(WINDOW_SIZE[0]//2 + offset, 160 + offset))
            screen.blit(shadow_surface2, shadow_rect2)
        
        pulse_amplitude = 6
        ease_factor = (math.sin(title_pulse) + 1) / 2
        pulse_offset_x = -ease_factor * pulse_amplitude
        pulse_offset_y = -ease_factor * pulse_amplitude
        
        title_surface1 = title_font.render(title_text1, True, WHITE)
        title_surface2 = title_font.render(title_text2, True, WHITE)
        
        title_rect1 = title_surface1.get_rect(center=(WINDOW_SIZE[0]//2 + pulse_offset_x, 80 + pulse_offset_y))
        title_rect2 = title_surface2.get_rect(center=(WINDOW_SIZE[0]//2 + pulse_offset_x, 160 + pulse_offset_y))
        
        screen.blit(title_surface1, title_rect1)
        screen.blit(title_surface2, title_rect2)

        start_button = draw_button("Start", 350)
        controls_button = draw_button("Controls", 430) 
        settings_button = draw_button("Settings", 510)
        quit_button = draw_button("Quit Game", 590)

        if settings_active:
            sliders, settings_rect = draw_settings_window()
            master_slider, music_slider = sliders

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_bgm.stop() 
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if settings_active:
                    if master_slider.collidepoint(mouse_pos):
                        dragging_master = True
                    elif music_slider.collidepoint(mouse_pos):
                        dragging_music = True
                    elif not settings_rect.collidepoint(mouse_pos):
                        settings_active = False
                        save_volume_settings(master_volume, music_volume)
                else:
                    if start_button.collidepoint(mouse_pos):
                        menu_bgm.stop()
                        save_volume_settings(master_volume, music_volume)
                        pygame.quit()
                        subprocess.run(['python', 'game_test.py'])
                        return
                    elif controls_button.collidepoint(mouse_pos):
                        return "controls"
                    elif settings_button.collidepoint(mouse_pos):
                        settings_active = True
                    elif quit_button.collidepoint(mouse_pos):
                        menu_bgm.stop() 
                        pygame.quit()
                        sys.exit()
                        
            if event.type == pygame.MOUSEBUTTONUP:
                dragging_master = False
                dragging_music = False
                
            if event.type == pygame.MOUSEMOTION:
                mouse_x = pygame.mouse.get_pos()[0]
                slider_left = (WINDOW_SIZE[0] - SLIDER_WIDTH)//2
                slider_right = slider_left + SLIDER_WIDTH
                
                if dragging_master or dragging_music:
                    if mouse_x < slider_left:
                        new_volume = 0
                    elif mouse_x > slider_right:
                        new_volume = 1
                    else:
                        new_volume = (mouse_x - slider_left) / SLIDER_WIDTH
                        
                    if dragging_master:
                        master_volume = new_volume
                    else:
                        music_volume = new_volume
                    
                    menu_bgm.set_volume(master_volume * music_volume)
                    save_volume_settings(master_volume, music_volume)

        pygame.display.flip()

if __name__ == "__main__":
    main_menu()
