import pygame
import sys
from typing import Dict, List, Optional, Callable, Any, Tuple
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, UI_COLORS, GAME_STATES,
    BACKGROUND_COLOR
)
from localization import Localization
from font_manager import FontManager
from animation import AnimationManager, ButtonAnimation, ParticleSystem


class MenuButton:
    def __init__(self, rect: pygame.Rect, text: str, action: str, 
                 color: Tuple[int, int, int] = None):
        self.rect = rect
        self.text = text
        self.action = action
        self.color = color if color else UI_COLORS['menu_button_normal']
        self.enabled = True
        self.animation = ButtonAnimation()
    
    def update(self, mouse_pos: Tuple[int, int], mouse_down: bool, dt: float):
        is_hovered = self.rect.collidepoint(mouse_pos)
        self.animation.update(is_hovered, mouse_down, dt)
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        is_hovered = self.animation.hover_progress > 0.0
        is_clicked = self.animation.click_progress > 0.0
        
        if is_clicked:
            scale = 0.90
        elif is_hovered:
            scale = 1.05
        else:
            scale = 1.0
        
        if scale != 1.0:
            center_x = self.rect.centerx
            center_y = self.rect.centery
            new_width = int(self.rect.width * scale)
            new_height = int(self.rect.height * scale)
            draw_rect = pygame.Rect(
                center_x - new_width // 2,
                center_y - new_height // 2,
                new_width,
                new_height
            )
        else:
            draw_rect = self.rect.copy()
        
        base_color = self.color
        if is_clicked:
            draw_color = (
                max(0, base_color[0] - 40),
                max(0, base_color[1] - 40),
                max(0, base_color[2] - 40)
            )
        elif is_hovered:
            draw_color = (
                min(255, base_color[0] + 20),
                min(255, base_color[1] + 20),
                min(255, base_color[2] + 20)
            )
        else:
            draw_color = base_color
        
        pygame.draw.rect(screen, draw_color, draw_rect, border_radius=8)
        
        border_color = UI_COLORS['highlight_border'] if is_hovered else (60, 70, 80)
        border_width = 4 if is_hovered else 2
        pygame.draw.rect(screen, border_color, draw_rect, border_width, border_radius=8)
        
        try:
            text_surface = font.render(self.text, True, UI_COLORS['menu_text'])
            text_rect = text_surface.get_rect(center=draw_rect.center)
            screen.blit(text_surface, text_rect)
        except Exception:
            fallback_font = pygame.font.Font(None, 24)
            text_surface = fallback_font.render(self.text, True, UI_COLORS['menu_text'])
            text_rect = text_surface.get_rect(center=draw_rect.center)
            screen.blit(text_surface, text_rect)


class DifficultyMenu:
    def __init__(self, screen: pygame.Surface, localization: Localization, 
                 animation_manager: AnimationManager = None):
        self.screen = screen
        self.loc = localization
        self.animation_manager = animation_manager
        
        if not pygame.font.get_init():
            pygame.font.init()
        
        self.font_manager = FontManager()
        self._init_fonts()
        
        self.buttons: List[MenuButton] = []
        self._create_buttons()
        
        self.mouse_pos = (0, 0)
        self.mouse_down = False
        self.last_time = pygame.time.get_ticks() / 1000.0
        
        self.selected_difficulty = 'normal'
    
    def _init_fonts(self):
        language = self.loc.get_language()
        self.font_title = self.font_manager.get_font(48, language)
        self.font_button = self.font_manager.get_font(28, language)
        self.font_help = self.font_manager.get_font(20, language)
    
    def _create_buttons(self):
        button_width = 300
        button_height = 60
        center_x = SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2 - 80
        
        easy_button = MenuButton(
            pygame.Rect(center_x - button_width // 2, start_y, button_width, button_height),
            self.loc.t('difficulty_easy'),
            'select_easy',
            (80, 150, 100)
        )
        self.buttons.append(easy_button)
        
        normal_button = MenuButton(
            pygame.Rect(center_x - button_width // 2, start_y + button_height + 20, button_width, button_height),
            self.loc.t('difficulty_normal'),
            'select_normal',
            (150, 150, 80)
        )
        self.buttons.append(normal_button)
        
        hard_button = MenuButton(
            pygame.Rect(center_x - button_width // 2, start_y + (button_height + 20) * 2, button_width, button_height),
            self.loc.t('difficulty_hard'),
            'select_hard',
            (150, 80, 80)
        )
        self.buttons.append(hard_button)
        
        back_button = MenuButton(
            pygame.Rect(center_x - button_width // 2, start_y + (button_height + 20) * 3 + 30, button_width, button_height),
            self.loc.t('back_to_menu'),
            'back_to_menu',
            (120, 80, 120)
        )
        self.buttons.append(back_button)
    
    def set_mouse_state(self, mouse_pos: Tuple[int, int], mouse_down: bool):
        self.mouse_pos = mouse_pos
        self.mouse_down = mouse_down
    
    def update(self):
        current_time = pygame.time.get_ticks() / 1000.0
        dt = current_time - self.last_time
        self.last_time = current_time
        
        for button in self.buttons:
            button.update(self.mouse_pos, self.mouse_down, dt)
    
    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        title_text = self.loc.t('select_difficulty')
        try:
            title_surface = self.font_title.render(title_text, True, UI_COLORS['menu_title'])
        except Exception:
            fallback_font = pygame.font.Font(None, 48)
            title_surface = fallback_font.render(title_text, True, UI_COLORS['menu_title'])
        
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_surface, title_rect)
        
        for button in self.buttons:
            button.draw(self.screen, self.font_button)
    
    def handle_click(self) -> Optional[str]:
        for button in self.buttons:
            if button.enabled and button.rect.collidepoint(self.mouse_pos):
                if self.animation_manager:
                    self.animation_manager.particle_system.emit(
                        button.rect.centerx, button.rect.centery,
                        UI_COLORS['menu_title'], count=15, spread=80
                    )
                return button.action
        return None


class MainMenu:
    def __init__(self, screen: pygame.Surface, localization: Localization, 
                 animation_manager: AnimationManager = None):
        self.screen = screen
        self.loc = localization
        self.animation_manager = animation_manager
        
        if not pygame.font.get_init():
            pygame.font.init()
        
        self.font_manager = FontManager()
        self._init_fonts()
        
        self.buttons: List[MenuButton] = []
        self._create_buttons()
        
        self.mouse_pos = (0, 0)
        self.mouse_down = False
        self.last_time = pygame.time.get_ticks() / 1000.0
        
        self._init_background_particles()
        self.background_pulse_time = 0.0
        self.title_animation_time = 0.0
    
    def _init_fonts(self):
        language = self.loc.get_language()
        self.font_title = self.font_manager.get_font(56, language)
        self.font_subtitle = self.font_manager.get_font(32, language)
        self.font_button = self.font_manager.get_font(28, language)
        self.font_help = self.font_manager.get_font(20, language)
    
    def _create_buttons(self):
        button_width = 300
        button_height = 60
        center_x = SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2 - 50
        
        start_button = MenuButton(
            pygame.Rect(center_x - button_width // 2, start_y, button_width, button_height),
            self.loc.t('start_game'),
            'start_game',
            (80, 150, 100)
        )
        self.buttons.append(start_button)
        
        help_button = MenuButton(
            pygame.Rect(center_x - button_width // 2, start_y + button_height + 20, button_width, button_height),
            self.loc.t('game_help'),
            'show_help',
            (100, 100, 180)
        )
        self.buttons.append(help_button)
        
        settings_button = MenuButton(
            pygame.Rect(center_x - button_width // 2, start_y + (button_height + 20) * 2, button_width, button_height),
            self.loc.t('settings'),
            'show_settings',
            (150, 100, 80)
        )
        self.buttons.append(settings_button)
        
        quit_button = MenuButton(
            pygame.Rect(center_x - button_width // 2, start_y + (button_height + 20) * 3, button_width, button_height),
            self.loc.t('quit_game'),
            'quit_game',
            (150, 80, 80)
        )
        self.buttons.append(quit_button)
    
    def _init_background_particles(self):
        import random
        self.background_particles = ParticleSystem()
        self.floating_particles = []
        
        for _ in range(50):
            particle = {
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'size': random.randint(2, 6),
                'speed_x': random.uniform(-0.3, 0.3),
                'speed_y': random.uniform(-0.2, 0.2),
                'alpha': random.randint(30, 100),
                'color': (
                    random.randint(60, 120),
                    random.randint(80, 140),
                    random.randint(100, 160)
                )
            }
            self.floating_particles.append(particle)
        
        for _ in range(30):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            color = (
                random.randint(40, 80),
                random.randint(60, 100),
                random.randint(80, 120)
            )
            self.background_particles.emit(x, y, color, count=1, spread=20)
    
    def set_mouse_state(self, mouse_pos: Tuple[int, int], mouse_down: bool):
        self.mouse_pos = mouse_pos
        self.mouse_down = mouse_down
    
    def update(self):
        current_time = pygame.time.get_ticks() / 1000.0
        dt = current_time - self.last_time
        self.last_time = current_time
        
        self.background_pulse_time += dt
        self.title_animation_time += dt
        
        for particle in self.floating_particles:
            particle['x'] += particle['speed_x']
            particle['y'] += particle['speed_y']
            
            if particle['x'] < -10:
                particle['x'] = SCREEN_WIDTH + 10
            elif particle['x'] > SCREEN_WIDTH + 10:
                particle['x'] = -10
            if particle['y'] < -10:
                particle['y'] = SCREEN_HEIGHT + 10
            elif particle['y'] > SCREEN_HEIGHT + 10:
                particle['y'] = -10
        
        for button in self.buttons:
            button.update(self.mouse_pos, self.mouse_down, dt)
    
    def draw(self):
        self._draw_gradient_background()
        self._draw_floating_particles()
        self._draw_background_hexagons()
        self._draw_decorative_elements()
        self._draw_title()
        
        for button in self.buttons:
            button.draw(self.screen, self.font_button)
        
        self._draw_version()
    
    def _draw_gradient_background(self):
        import math
        
        gradient_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        for y in range(SCREEN_HEIGHT):
            progress = y / SCREEN_HEIGHT
            pulse = math.sin(self.background_pulse_time * 0.5) * 0.1 + 0.9
            
            top_color = (
                int(BACKGROUND_COLOR[0] * pulse),
                int(BACKGROUND_COLOR[1] * pulse),
                int(BACKGROUND_COLOR[2] * pulse)
            )
            bottom_color = (
                int(min(255, BACKGROUND_COLOR[0] + 15) * pulse),
                int(min(255, BACKGROUND_COLOR[1] + 20) * pulse),
                int(min(255, BACKGROUND_COLOR[2] + 25) * pulse)
            )
            
            r = int(top_color[0] + (bottom_color[0] - top_color[0]) * progress)
            g = int(top_color[1] + (bottom_color[1] - top_color[1]) * progress)
            b = int(top_color[2] + (bottom_color[2] - top_color[2]) * progress)
            
            pygame.draw.line(gradient_surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        self.screen.blit(gradient_surface, (0, 0))
    
    def _draw_floating_particles(self):
        import math
        
        for particle in self.floating_particles:
            pulse_alpha = particle['alpha'] + int(math.sin(self.background_pulse_time * 2 + particle['x']) * 20)
            pulse_alpha = max(10, min(150, pulse_alpha))
            
            color_with_alpha = (
                particle['color'][0],
                particle['color'][1],
                particle['color'][2],
                pulse_alpha
            )
            
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                particle_surface,
                color_with_alpha,
                (particle['size'], particle['size']),
                particle['size']
            )
            self.screen.blit(
                particle_surface,
                (int(particle['x'] - particle['size']), int(particle['y'] - particle['size']))
            )
    
    def _draw_decorative_elements(self):
        import math
        
        corner_size = 60
        alpha = 80
        
        corners = [
            (0, 0),
            (SCREEN_WIDTH - corner_size, 0),
            (0, SCREEN_HEIGHT - corner_size),
            (SCREEN_WIDTH - corner_size, SCREEN_HEIGHT - corner_size)
        ]
        
        for i, (x, y) in enumerate(corners):
            rotation = i * math.pi / 2
            
            corner_surface = pygame.Surface((corner_size, corner_size), pygame.SRCALPHA)
            
            points = [
                (0, 0),
                (corner_size, 0),
                (0, corner_size)
            ]
            
            glow_color = (
                UI_COLORS['highlight_border'][0],
                UI_COLORS['highlight_border'][1],
                UI_COLORS['highlight_border'][2],
                alpha
            )
            
            pygame.draw.polygon(corner_surface, glow_color, points)
            pygame.draw.polygon(corner_surface, (255, 255, 255, alpha // 2), points, 2)
            
            rotated_surface = pygame.transform.rotate(corner_surface, math.degrees(rotation))
            self.screen.blit(rotated_surface, (x, y))
        
        pulse_size = 100 + math.sin(self.background_pulse_time) * 20
        
        center_glow = pygame.Surface((pulse_size * 2, pulse_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            center_glow,
            (UI_COLORS['menu_title'][0], UI_COLORS['menu_title'][1], UI_COLORS['menu_title'][2], 30),
            (pulse_size, pulse_size),
            pulse_size
        )
        self.screen.blit(
            center_glow,
            (SCREEN_WIDTH // 2 - pulse_size, SCREEN_HEIGHT // 2 - pulse_size)
        )
    
    def _draw_background_hexagons(self):
        import math
        hex_size = 50
        offset_x = 0
        offset_y = 0
        
        pulse = math.sin(self.background_pulse_time * 0.3) * 0.2 + 0.8
        
        for row in range(0, SCREEN_HEIGHT // hex_size + 2):
            for col in range(0, SCREEN_WIDTH // hex_size + 2):
                q = col
                r = row - col // 2
                
                x = hex_size * (3/2 * q) + offset_x
                y = hex_size * (math.sqrt(3)/2 * q + math.sqrt(3) * r) + offset_y
                
                corners = []
                for i in range(6):
                    angle = math.pi / 3 * i
                    cx = x + hex_size * 0.8 * math.cos(angle)
                    cy = y + hex_size * 0.8 * math.sin(angle)
                    corners.append((cx, cy))
                
                alpha = int(25 * pulse)
                color = (
                    BACKGROUND_COLOR[0] + 20,
                    BACKGROUND_COLOR[1] + 25,
                    BACKGROUND_COLOR[2] + 30,
                    alpha
                )
                
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                pygame.draw.polygon(s, color, corners, 1)
                self.screen.blit(s, (0, 0))
    
    def _draw_title(self):
        title_text = self.loc.t('game_title')
        subtitle_text = self.loc.t('game_subtitle')
        
        try:
            title_surface = self.font_title.render(title_text, True, UI_COLORS['menu_title'])
        except Exception:
            fallback_font = pygame.font.Font(None, 56)
            title_surface = fallback_font.render(title_text, True, UI_COLORS['menu_title'])
        
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_surface, title_rect)
        
        try:
            subtitle_surface = self.font_subtitle.render(subtitle_text, True, UI_COLORS['help_text'])
        except Exception:
            fallback_font = pygame.font.Font(None, 28)
            subtitle_surface = fallback_font.render(subtitle_text, True, UI_COLORS['help_text'])
        
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, 220))
        self.screen.blit(subtitle_surface, subtitle_rect)
    
    def _draw_version(self):
        version_text = "Version 1.0"
        try:
            version_surface = self.font_help.render(version_text, True, (100, 100, 100))
        except Exception:
            fallback_font = pygame.font.Font(None, 16)
            version_surface = fallback_font.render(version_text, True, (100, 100, 100))
        
        version_rect = version_surface.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
        self.screen.blit(version_surface, version_rect)
    
    def handle_click(self) -> Optional[str]:
        for button in self.buttons:
            if button.enabled and button.rect.collidepoint(self.mouse_pos):
                if self.animation_manager:
                    self.animation_manager.particle_system.emit(
                        button.rect.centerx, button.rect.centery,
                        UI_COLORS['menu_title'], count=15, spread=80
                    )
                return button.action
        return None


class SettingsMenu:
    def __init__(self, screen: pygame.Surface, localization: Localization, 
                 animation_manager: AnimationManager = None):
        self.screen = screen
        self.loc = localization
        self.animation_manager = animation_manager
        
        if not pygame.font.get_init():
            pygame.font.init()
        
        self.font_manager = FontManager()
        self._init_fonts()
        
        self.buttons: List[MenuButton] = []
        self._create_buttons()
        
        self.mouse_pos = (0, 0)
        self.mouse_down = False
        self.last_time = pygame.time.get_ticks() / 1000.0
    
    def _init_fonts(self):
        language = self.loc.get_language()
        self.font_title = self.font_manager.get_font(48, language)
        self.font_button = self.font_manager.get_font(24, language)
    
    def _create_buttons(self):
        button_width = 300
        button_height = 50
        center_x = SCREEN_WIDTH // 2
        start_y = 250
        
        en_button = MenuButton(
            pygame.Rect(center_x - button_width // 2, start_y, button_width, button_height),
            'English',
            'set_language_en',
            (100, 150, 100) if self.loc.get_language() == 'en' else (80, 100, 150)
        )
        self.buttons.append(en_button)
        
        chinese_available = self.font_manager.is_chinese_available()
        if chinese_available:
            zh_button = MenuButton(
                pygame.Rect(center_x - button_width // 2, start_y + button_height + 15, button_width, button_height),
                self.loc.t('language_zh'),
                'set_language_zh',
                (100, 150, 100) if self.loc.get_language() == 'zh' else (80, 80, 80)
            )
            self.buttons.append(zh_button)
        else:
            zh_button = MenuButton(
                pygame.Rect(center_x - button_width // 2, start_y + button_height + 15, button_width, button_height),
                'Chinese (Install Font)',
                'show_font_help',
                (120, 100, 60)
            )
            self.buttons.append(zh_button)
        
        back_button = MenuButton(
            pygame.Rect(center_x - button_width // 2, start_y + (button_height + 15) * 3, button_width, button_height),
            self.loc.t('back_to_menu'),
            'back_to_menu',
            (120, 80, 80)
        )
        self.buttons.append(back_button)
    
    def set_mouse_state(self, mouse_pos: Tuple[int, int], mouse_down: bool):
        self.mouse_pos = mouse_pos
        self.mouse_down = mouse_down
    
    def update(self):
        current_time = pygame.time.get_ticks() / 1000.0
        dt = current_time - self.last_time
        self.last_time = current_time
        
        for button in self.buttons:
            button.update(self.mouse_pos, self.mouse_down, dt)
    
    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        title_text = self.loc.t('settings')
        try:
            title_surface = self.font_title.render(title_text, True, UI_COLORS['menu_title'])
        except Exception:
            fallback_font = pygame.font.Font(None, 48)
            title_surface = fallback_font.render(title_text, True, UI_COLORS['menu_title'])
        
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_surface, title_rect)
        
        lang_text = self.loc.t('language') + ':'
        try:
            lang_surface = self.font_button.render(lang_text, True, UI_COLORS['menu_text'])
        except Exception:
            fallback_font = pygame.font.Font(None, 24)
            lang_surface = fallback_font.render(lang_text, True, UI_COLORS['menu_text'])
        
        lang_rect = lang_surface.get_rect(center=(SCREEN_WIDTH // 2, 220))
        self.screen.blit(lang_surface, lang_rect)
        
        for button in self.buttons:
            button.draw(self.screen, self.font_button)
    
    def handle_click(self) -> Optional[str]:
        for button in self.buttons:
            if button.enabled and button.rect.collidepoint(self.mouse_pos):
                return button.action
        return None
