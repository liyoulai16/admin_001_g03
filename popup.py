import pygame
import math
from typing import Dict, Optional, Tuple, List, Callable
from config import UI_COLORS, BACKGROUND_COLOR, BUILDING_INFO
from localization import Localization
from font_manager import FontManager


class PopupButton:
    def __init__(self, rect: pygame.Rect, text: str, action: str, 
                 color: Tuple[int, int, int] = None, enabled: bool = True):
        self.rect = rect
        self.text = text
        self.action = action
        self.color = color if color else UI_COLORS['menu_button_normal']
        self.enabled = enabled
        self.hovered = False
        self.pressed = False
        
        self.anim_progress = 0.0
        self.target_visible = True
        
    def update(self, mouse_pos: Tuple[int, int], mouse_down: bool, dt: float):
        if self.target_visible:
            self.anim_progress = min(self.anim_progress + dt * 8.0, 1.0)
        else:
            self.anim_progress = max(self.anim_progress - dt * 10.0, 0.0)
        
        if self.anim_progress < 0.5:
            return
        
        self.hovered = self.enabled and self.rect.collidepoint(mouse_pos)
        
        if self.hovered and mouse_down and not self.pressed:
            self.pressed = True
        elif not mouse_down:
            self.pressed = False


class BasePopup:
    def __init__(self, width: int, height: int, title: str, 
                 localization: Localization, font_manager: FontManager):
        self.width = width
        self.height = height
        self.title = title
        self.loc = localization
        self.font_manager = font_manager
        
        self.visible = False
        self.anim_progress = 0.0
        self.buttons: List[PopupButton] = []
        
        self.screen_width = 0
        self.screen_height = 0
        self.x = 0
        self.y = 0
        
        self.mouse_pos = (0, 0)
        self.mouse_down = False
        self.mouse_was_down = False
        
        self.result = None
        
    def update_position(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2
        
    def update(self, dt: float):
        if self.visible:
            self.anim_progress = min(self.anim_progress + dt * 6.0, 1.0)
        else:
            self.anim_progress = max(self.anim_progress - dt * 8.0, 0.0)
        
        for button in self.buttons:
            button.update(self.mouse_pos, self.mouse_down, dt)
    
    def show(self):
        self.visible = True
        self.anim_progress = max(self.anim_progress, 0.01)
        self.result = None
    
    def hide(self):
        self.visible = False
    
    def set_mouse_state(self, mouse_pos: Tuple[int, int], mouse_down: bool):
        self.mouse_was_down = self.mouse_down
        self.mouse_pos = mouse_pos
        self.mouse_down = mouse_down
    
    def handle_click(self) -> Optional[str]:
        if not self.visible or self.anim_progress < 0.5:
            return None
        
        if self.mouse_was_down and not self.mouse_down:
            for button in self.buttons:
                if button.enabled and button.hovered:
                    return button.action
            
            if not self._is_point_in_popup(self.mouse_pos):
                return 'close'
        
        return None
    
    def _is_point_in_popup(self, pos: Tuple[int, int]) -> bool:
        return (self.x <= pos[0] <= self.x + self.width and
                self.y <= pos[1] <= self.y + self.height)
    
    def draw(self, screen: pygame.Surface):
        if self.anim_progress <= 0:
            return
        
        def ease_out_cubic(t):
            return 1 - math.pow(1 - t, 3) if t < 1 else 1
        
        eased_progress = ease_out_cubic(self.anim_progress)
        
        scale = 0.9 + 0.1 * eased_progress
        alpha = int(255 * eased_progress)
        
        draw_width = int(self.width * scale)
        draw_height = int(self.height * scale)
        draw_x = self.x + (self.width - draw_width) // 2
        draw_y = self.y + (self.height - draw_height) // 2
        
        shadow_rect = pygame.Rect(draw_x + 5, draw_y + 5, draw_width, draw_height)
        shadow_alpha = int(60 * alpha / 255 * 255) if alpha > 0 else 0
        shadow_surface = pygame.Surface((draw_width, draw_height), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, shadow_alpha))
        screen.blit(shadow_surface, (draw_x + 5, draw_y + 5))
        
        popup_surface = pygame.Surface((draw_width, draw_height), pygame.SRCALPHA)
        popup_color = (
            UI_COLORS['menu_background'][0],
            UI_COLORS['menu_background'][1],
            UI_COLORS['menu_background'][2],
            alpha
        )
        popup_surface.fill(popup_color)
        border_color = (
            UI_COLORS['highlight_border'][0],
            UI_COLORS['highlight_border'][1],
            UI_COLORS['highlight_border'][2],
            alpha
        )
        pygame.draw.rect(popup_surface, border_color, popup_surface.get_rect(), 3)
        
        screen.blit(popup_surface, (draw_x, draw_y))
        
        if eased_progress > 0.7:
            title_alpha = int(255 * min(1, (eased_progress - 0.7) * 5))
            self._draw_title(screen, draw_x, draw_y, draw_width, title_alpha)
            
            for button in self.buttons:
                if button.anim_progress > 0.3:
                    self._draw_popup_button(screen, button, draw_x, draw_y)
    
    def _draw_title(self, screen: pygame.Surface, x: int, y: int, width: int, alpha: int):
        title_font = self.font_manager.get_font(28, self.loc.get_language())
        try:
            title_surface = title_font.render(self.title, True, UI_COLORS['menu_title'])
        except Exception:
            fallback_font = pygame.font.Font(None, 28)
            title_surface = fallback_font.render(self.title, True, UI_COLORS['menu_title'])
        
        title_surface.set_alpha(alpha)
        title_rect = title_surface.get_rect(centerx=x + width // 2, y=y + 20)
        screen.blit(title_surface, title_rect)
    
    def _draw_popup_button(self, screen: pygame.Surface, button: PopupButton, 
                          popup_x: int, popup_y: int):
        def ease_out_cubic(t):
            return 1 - math.pow(1 - t, 3) if t < 1 else 1
        
        anim_progress = button.anim_progress
        if anim_progress <= 0:
            return
        
        eased = ease_out_cubic(anim_progress)
        alpha = int(255 * min(1, anim_progress * 2))
        
        scale = 1.0
        if button.pressed:
            scale = 0.95
        elif button.hovered:
            scale = 1.02
        
        rect = button.rect
        
        if scale != 1.0:
            center_x = rect.centerx
            center_y = rect.centery
            new_width = int(rect.width * scale)
            new_height = int(rect.height * scale)
            draw_rect = pygame.Rect(
                center_x - new_width // 2,
                center_y - new_height // 2,
                new_width,
                new_height
            )
        else:
            draw_rect = rect.copy()
        
        draw_rect.x += popup_x
        draw_rect.y += popup_y
        
        base_color = button.color
        if button.hovered:
            draw_color = (
                min(255, base_color[0] + 20),
                min(255, base_color[1] + 20),
                min(255, base_color[2] + 20)
            )
        else:
            draw_color = base_color
        
        draw_color_with_alpha = (
            draw_color[0],
            draw_color[1],
            draw_color[2],
            alpha
        )
        
        button_surface = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
        button_surface.fill(draw_color_with_alpha)
        
        border_color = UI_COLORS['highlight_border'] if button.hovered else (60, 70, 80)
        border_width = 3 if button.hovered else 2
        pygame.draw.rect(button_surface, (*border_color, alpha), 
                        button_surface.get_rect(), border_width)
        
        screen.blit(button_surface, draw_rect)
        
        text_font = self.font_manager.get_font(22, self.loc.get_language())
        try:
            text_surface = text_font.render(button.text, True, UI_COLORS['menu_text'])
        except Exception:
            fallback_font = pygame.font.Font(None, 22)
            text_surface = fallback_font.render(button.text, True, UI_COLORS['menu_text'])
        
        text_surface.set_alpha(alpha)
        text_rect = text_surface.get_rect(center=draw_rect.center)
        screen.blit(text_surface, text_rect)


class SettingsPopup(BasePopup):
    def __init__(self, width: int, height: int, localization: Localization, 
                 font_manager: FontManager):
        super().__init__(width, height, localization.t('settings'), localization, font_manager)
        
        self._create_buttons()
    
    def _create_buttons(self):
        button_width = 220
        button_height = 50
        center_x = (self.width - button_width) // 2
        start_y = 90
        
        chinese_available = self.font_manager.is_chinese_available()
        
        en_button = PopupButton(
            pygame.Rect(center_x, start_y, button_width, button_height),
            self.loc.t('language_en'),
            'set_language_en',
            color=(100, 150, 100) if self.loc.get_language() == 'en' else (80, 100, 150)
        )
        self.buttons.append(en_button)
        
        start_y += button_height + 15
        
        if chinese_available:
            zh_button = PopupButton(
                pygame.Rect(center_x, start_y, button_width, button_height),
                self.loc.t('language_zh'),
                'set_language_zh',
                color=(100, 150, 100) if self.loc.get_language() == 'zh' else (80, 80, 80)
            )
            self.buttons.append(zh_button)
        else:
            zh_button = PopupButton(
                pygame.Rect(center_x, start_y, button_width, button_height),
                self.loc.t('language_zh') + ' (Install Font)',
                'show_font_help',
                color=(120, 100, 60)
            )
            self.buttons.append(zh_button)
        
        start_y += button_height + 15
        
        close_button = PopupButton(
            pygame.Rect(center_x, start_y, button_width, button_height),
            self.loc.t('cancel'),
            'close',
            color=(120, 80, 80)
        )
        self.buttons.append(close_button)


class BuildPopup(BasePopup):
    def __init__(self, width: int, height: int, localization: Localization, 
                 font_manager: FontManager, player):
        self.player = player
        super().__init__(width, height, localization.t('select_building'), localization, font_manager)
        
        self._create_buttons()
    
    def _create_buttons(self):
        button_width = 220
        button_height = 45
        center_x = (self.width - button_width) // 2
        start_y = 80
        
        for building_type, info in BUILDING_INFO.items():
            cost = info['cost']
            can_afford = self.player.can_afford(cost)
            
            cost_str = ", ".join([f"{self.loc.get_resource_icon(k)}{v}" for k, v in cost.items()])
            building_name = self.loc.get_building_name(building_type)
            button_text = f"{building_name} ({cost_str})"
            
            button_color = (80, 80, 150) if can_afford else (80, 80, 80)
            
            button = PopupButton(
                pygame.Rect(center_x, start_y, button_width, button_height),
                button_text,
                f'build_{building_type}',
                color=button_color,
                enabled=can_afford
            )
            self.buttons.append(button)
            
            start_y += button_height + 10
        
        start_y += 10
        
        close_button = PopupButton(
            pygame.Rect(center_x, start_y, button_width, button_height),
            self.loc.t('cancel'),
            'close',
            color=(120, 80, 80)
        )
        self.buttons.append(close_button)
    
    def update_player(self, player):
        self.player = player
        for button in self.buttons:
            if button.action.startswith('build_'):
                building_type = button.action[6:]
                if building_type in BUILDING_INFO:
                    cost = BUILDING_INFO[building_type]['cost']
                    can_afford = self.player.can_afford(cost)
                    button.enabled = can_afford
                    button.color = (80, 80, 150) if can_afford else (80, 80, 80)


class TrainPopup(BasePopup):
    def __init__(self, width: int, height: int, localization: Localization, 
                 font_manager: FontManager, player):
        self.player = player
        from config import UNIT_INFO
        self.UNIT_INFO = UNIT_INFO
        super().__init__(width, height, localization.t('select_unit'), localization, font_manager)
        
        self._create_buttons()
    
    def _create_buttons(self):
        button_width = 220
        button_height = 45
        center_x = (self.width - button_width) // 2
        start_y = 80
        
        for unit_type, info in self.UNIT_INFO.items():
            cost = info['cost']
            can_afford = self.player.can_afford(cost)
            
            cost_str = ", ".join([f"{self.loc.get_resource_icon(k)}{v}" for k, v in cost.items()])
            unit_name = self.loc.get_unit_name(unit_type)
            button_text = f"{unit_name} ({cost_str})"
            
            button_color = (80, 120, 80) if can_afford else (80, 80, 80)
            
            button = PopupButton(
                pygame.Rect(center_x, start_y, button_width, button_height),
                button_text,
                f'train_{unit_type}',
                color=button_color,
                enabled=can_afford
            )
            self.buttons.append(button)
            
            start_y += button_height + 10
        
        start_y += 10
        
        close_button = PopupButton(
            pygame.Rect(center_x, start_y, button_width, button_height),
            self.loc.t('cancel'),
            'close',
            color=(120, 80, 80)
        )
        self.buttons.append(close_button)
    
    def update_player(self, player):
        self.player = player
        for button in self.buttons:
            if button.action.startswith('train_'):
                unit_type = button.action[6:]
                if unit_type in self.UNIT_INFO:
                    cost = self.UNIT_INFO[unit_type]['cost']
                    can_afford = self.player.can_afford(cost)
                    button.enabled = can_afford
                    button.color = (80, 120, 80) if can_afford else (80, 80, 80)
