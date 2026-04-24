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
        self.anim_progress = 1.0
        
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
        self._just_opened = False
        
    def update_position(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2
        
    def update(self, dt: float):
        if self.visible:
            self.anim_progress = 1.0
        else:
            self.anim_progress = max(self.anim_progress - dt * 15.0, 0.0)
        
        if self._just_opened and self.mouse_was_down and not self.mouse_down:
            self._just_opened = False
        
        local_mouse_pos = (self.mouse_pos[0] - self.x, self.mouse_pos[1] - self.y)
        
        for button in self.buttons:
            button.update(local_mouse_pos, self.mouse_down, dt)
    
    def show(self):
        if self.visible:
            self.hide()
            return
        
        self.visible = True
        self.anim_progress = 1.0
        for button in self.buttons:
            button.anim_progress = 1.0
        self.result = None
        self._just_opened = True
    
    def hide(self):
        self.visible = False
        self._just_opened = False
    
    def set_mouse_state(self, mouse_pos: Tuple[int, int], mouse_down: bool):
        self.mouse_was_down = self.mouse_down
        self.mouse_pos = mouse_pos
        self.mouse_down = mouse_down
    
    def handle_click(self) -> Optional[str]:
        if not self.visible:
            return None
        
        if self.mouse_down and not self.mouse_was_down:
            for button in self.buttons:
                button_screen_rect = pygame.Rect(
                    button.rect.x + self.x,
                    button.rect.y + self.y,
                    button.rect.width,
                    button.rect.height
                )
                if button.enabled and button_screen_rect.collidepoint(self.mouse_pos):
                    return button.action
        
        if self.mouse_was_down and not self.mouse_down:
            if not self._just_opened and not self._is_point_in_popup(self.mouse_pos):
                return 'close'
        
        return None
    
    def _is_point_in_popup(self, pos: Tuple[int, int]) -> bool:
        return (self.x <= pos[0] <= self.x + self.width and
                self.y <= pos[1] <= self.y + self.height)
    
    def draw(self, screen: pygame.Surface):
        if self.anim_progress <= 0:
            return
        
        draw_x = self.x
        draw_y = self.y
        draw_width = self.width
        draw_height = self.height
        
        shadow_alpha = 60
        shadow_surface = pygame.Surface((draw_width, draw_height), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, shadow_alpha))
        screen.blit(shadow_surface, (draw_x + 5, draw_y + 5))
        
        popup_surface = pygame.Surface((draw_width, draw_height), pygame.SRCALPHA)
        popup_color = (
            UI_COLORS['menu_background'][0],
            UI_COLORS['menu_background'][1],
            UI_COLORS['menu_background'][2],
            255
        )
        popup_surface.fill(popup_color)
        border_color = (
            UI_COLORS['highlight_border'][0],
            UI_COLORS['highlight_border'][1],
            UI_COLORS['highlight_border'][2],
            255
        )
        pygame.draw.rect(popup_surface, border_color, popup_surface.get_rect(), 3)
        
        screen.blit(popup_surface, (draw_x, draw_y))
        
        self._draw_title(screen, draw_x, draw_y, draw_width, 255)
        
        for button in self.buttons:
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
        scale = 1.0
        if button.enabled and button.pressed:
            scale = 0.95
        elif button.enabled and button.hovered:
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
        if button.enabled and button.hovered:
            draw_color = (
                min(255, base_color[0] + 20),
                min(255, base_color[1] + 20),
                min(255, base_color[2] + 20)
            )
        elif not button.enabled:
            draw_color = (60, 60, 60)
        else:
            draw_color = base_color
        
        button_surface = pygame.Surface((draw_rect.width, draw_rect.height))
        button_surface.fill(draw_color)
        
        if button.enabled and button.hovered:
            border_color = UI_COLORS['highlight_border']
            border_width = 3
        elif not button.enabled:
            border_color = (80, 80, 80)
            border_width = 2
        else:
            border_color = (60, 70, 80)
            border_width = 2
        
        pygame.draw.rect(button_surface, border_color, 
                        button_surface.get_rect(), border_width)
        
        screen.blit(button_surface, draw_rect)
        
        text_font = self.font_manager.get_font(22, self.loc.get_language())
        text_color = (120, 120, 120) if not button.enabled else UI_COLORS['menu_text']
        try:
            text_surface = text_font.render(button.text, True, text_color)
        except Exception:
            fallback_font = pygame.font.Font(None, 22)
            text_surface = fallback_font.render(button.text, True, text_color)
        
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
        self.selected_tile = None
        super().__init__(width, height, localization.t('select_building'), localization, font_manager)
        
        self._create_buttons()
    
    def set_selected_tile(self, tile):
        self.selected_tile = tile
        self._update_buttons()
    
    def _can_build_on_tile(self, building_type: str) -> bool:
        if not self.selected_tile:
            return False
        
        if self.selected_tile.building:
            return False
        
        if self.selected_tile.terrain in ['mountain', 'water']:
            return False
        
        building_info = BUILDING_INFO.get(building_type, {})
        required_terrain = building_info.get('required_terrain', [])
        
        if required_terrain:
            if self.selected_tile.terrain not in required_terrain:
                return False
        
        return True
    
    def _create_buttons(self):
        button_width = 220
        button_height = 45
        center_x = (self.width - button_width) // 2
        start_y = 80
        
        for building_type, info in BUILDING_INFO.items():
            cost = info['cost']
            can_afford = self.player.can_afford(cost)
            can_build = self._can_build_on_tile(building_type)
            
            cost_str = ", ".join([f"{self.loc.get_resource_icon(k)}{v}" for k, v in cost.items()])
            building_name = self.loc.get_building_name(building_type)
            
            required_terrain = info.get('required_terrain', [])
            if required_terrain:
                terrain_names = ", ".join([self.loc.get_terrain_name(t) for t in required_terrain])
                button_text = f"{building_name} ({cost_str}) [{terrain_names} only]"
            else:
                button_text = f"{building_name} ({cost_str})"
            
            if can_afford and can_build:
                button_color = (80, 120, 80)
                enabled = True
            elif can_afford and not can_build:
                button_color = (120, 100, 80)
                enabled = False
            else:
                button_color = (80, 80, 80)
                enabled = False
            
            button = PopupButton(
                pygame.Rect(center_x, start_y, button_width, button_height),
                button_text,
                f'build_{building_type}',
                color=button_color,
                enabled=enabled
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
    
    def _update_buttons(self):
        self.buttons = []
        self._create_buttons()
    
    def update_player(self, player):
        self.player = player
        for button in self.buttons:
            if button.action.startswith('build_'):
                building_type = button.action[6:]
                if building_type in BUILDING_INFO:
                    cost = BUILDING_INFO[building_type]['cost']
                    can_afford = self.player.can_afford(cost)
                    can_build = self._can_build_on_tile(building_type)
                    
                    if can_afford and can_build:
                        button.color = (80, 120, 80)
                        button.enabled = True
                    elif can_afford and not can_build:
                        button.color = (120, 100, 80)
                        button.enabled = False
                    else:
                        button.color = (80, 80, 80)
                        button.enabled = False


class TrainPopup(BasePopup):
    def __init__(self, width: int, height: int, localization: Localization, 
                 font_manager: FontManager, player):
        self.player = player
        from config import UNIT_INFO, BUILDING_INFO
        self.UNIT_INFO = UNIT_INFO
        self.BUILDING_INFO = BUILDING_INFO
        self.selected_tile = None
        super().__init__(width, height, localization.t('select_unit'), localization, font_manager)
        
        self._create_buttons()
    
    def set_selected_tile(self, tile):
        self.selected_tile = tile
        self._update_buttons()
    
    def _get_trainable_units(self):
        if not self.selected_tile or not self.selected_tile.building:
            return []
        
        building_type = self.selected_tile.building.building_type
        building_info = self.BUILDING_INFO.get(building_type, {})
        return building_info.get('can_train', [])
    
    def _create_buttons(self):
        button_width = 220
        button_height = 45
        center_x = (self.width - button_width) // 2
        start_y = 80
        
        trainable_units = self._get_trainable_units()
        
        for unit_type in trainable_units:
            if unit_type not in self.UNIT_INFO:
                continue
            
            info = self.UNIT_INFO[unit_type]
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
    
    def _update_buttons(self):
        self.buttons = []
        self._create_buttons()
    
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
