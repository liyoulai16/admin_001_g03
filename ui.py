import pygame
import math
from typing import Dict, Optional, Tuple, List
from config import (
    UI_PANEL_COLOR, TEXT_COLOR, HIGHLIGHT_COLOR, SELECTED_COLOR,
    BUILDING_INFO, UI_COLORS
)
from player import Player, Building, Unit
from hex_map import HexMap, HexTile
from localization import Localization
from font_manager import FontManager
from animation import AnimationManager, ButtonAnimation


class UI:
    def __init__(self, screen_width: int, screen_height: int, localization: Localization, 
                 animation_manager: AnimationManager = None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.panel_width = 250
        self.panel_x = screen_width - self.panel_width
        self.loc = localization
        
        if not pygame.font.get_init():
            pygame.font.init()
        
        self.font_manager = FontManager()
        self._init_fonts()
        
        self.buttons: List[Dict] = []
        self.build_menu_open = False
        self.settings_menu_open = False
        self.language_menu_open = False
        self.unit_menu_open = False
        
        self._language_warning_shown = False
        
        self.animation_manager = animation_manager
        self.button_states: Dict[str, Dict] = {}
        self.mouse_pos = (0, 0)
        self.mouse_down = False
    
    def _init_fonts(self):
        language = self.loc.get_language()
        self.font_large = self.font_manager.get_font(28, language)
        self.font_medium = self.font_manager.get_font(22, language)
        self.font_small = self.font_manager.get_font(18, language)
    
    def set_localization(self, localization: Localization):
        self.loc = localization
        self._init_fonts()
    
    def get_font_manager(self) -> FontManager:
        return self.font_manager
    
    def draw_resource_panel(self, screen: pygame.Surface, player: Player, turn: int):
        panel_rect = pygame.Rect(self.panel_x, 0, self.panel_width, 120)
        pygame.draw.rect(screen, UI_PANEL_COLOR, panel_rect)
        pygame.draw.line(screen, (100, 100, 100), 
                        (self.panel_x, 0), (self.panel_x, self.screen_height), 2)
        
        turn_text = self.font_large.render(f"{self.loc.t('turn')}: {turn}", True, TEXT_COLOR)
        screen.blit(turn_text, (self.panel_x + 10, 10))
        
        y_offset = 45
        for res_type, amount in player.resources.items():
            icon = self.loc.get_resource_icon(res_type)
            name = self.loc.get_resource_name(res_type)
            text = self.font_medium.render(f"{icon} {name}: {amount}", True, TEXT_COLOR)
            screen.blit(text, (self.panel_x + 10, y_offset))
            y_offset += 25
    
    def draw_tile_info(self, screen: pygame.Surface, tile: Optional[HexTile]):
        panel_rect = pygame.Rect(self.panel_x, 130, self.panel_width, 180)
        pygame.draw.rect(screen, UI_PANEL_COLOR, panel_rect)
        
        title = self.font_large.render(self.loc.t('tile_info'), True, TEXT_COLOR)
        screen.blit(title, (self.panel_x + 10, 140))
        
        if tile is None:
            no_info = self.font_medium.render(self.loc.t('no_tile_selected'), True, (150, 150, 150))
            screen.blit(no_info, (self.panel_x + 10, 170))
            return
        
        terrain_name = self.loc.get_terrain_name(tile.terrain)
        terrain_text = self.font_medium.render(f"{self.loc.t('terrain')}: {terrain_name}", True, TEXT_COLOR)
        screen.blit(terrain_text, (self.panel_x + 10, 170))
        
        owner_name = tile.owner.name if tile.owner else self.loc.t('none')
        owner_text = self.font_medium.render(f"{self.loc.t('owner')}: {owner_name}", 
                                             True, TEXT_COLOR)
        screen.blit(owner_text, (self.panel_x + 10, 195))
        
        if tile.building:
            building_name = self.loc.get_building_name(tile.building.building_type)
            building_text = self.font_medium.render(f"{self.loc.t('building')}: {building_name}", True, TEXT_COLOR)
            screen.blit(building_text, (self.panel_x + 10, 220))
            hp_text = self.font_small.render(f"HP: {tile.building.health}/{tile.building.max_health}", 
                                             True, TEXT_COLOR)
            screen.blit(hp_text, (self.panel_x + 20, 245))
        
        if tile.unit:
            unit_name = self.loc.get_unit_name(tile.unit.unit_type)
            unit_text = self.font_medium.render(f"{self.loc.t('unit')}: {unit_name}", True, TEXT_COLOR)
            screen.blit(unit_text, (self.panel_x + 10, 270 if tile.building else 220))
            hp_text = self.font_small.render(f"HP: {tile.unit.health}/{tile.unit.max_health}", 
                                             True, TEXT_COLOR)
            screen.blit(hp_text, (self.panel_x + 20, 295 if tile.building else 245))
    
    def draw_action_buttons(self, screen: pygame.Surface, selected_tile: Optional[HexTile], 
                            current_player: Player, 
                            can_expand_territory: bool = False,
                            can_clear_enemy_tile: bool = False) -> List[Dict]:
        self.buttons = []
        
        button_y = 320
        button_height = 40
        button_width = self.panel_width - 20
        
        end_turn_button = {
            'rect': pygame.Rect(self.panel_x + 10, button_y, button_width, button_height),
            'text': self.loc.t('end_turn'),
            'action': 'end_turn',
            'color': (80, 150, 100)
        }
        self.buttons.append(end_turn_button)
        self._draw_button(screen, end_turn_button)
        
        button_y += button_height + 10
        
        settings_button = {
            'rect': pygame.Rect(self.panel_x + 10, button_y, button_width, button_height),
            'text': self.loc.t('settings'),
            'action': 'open_settings_popup',
            'color': (100, 80, 150)
        }
        self.buttons.append(settings_button)
        self._draw_button(screen, settings_button)
        
        button_y += button_height + 10
        
        return_to_menu_button = {
            'rect': pygame.Rect(self.panel_x + 10, button_y, button_width, button_height),
            'text': self.loc.t('back_to_menu'),
            'action': 'return_to_menu',
            'color': (150, 100, 100)
        }
        self.buttons.append(return_to_menu_button)
        self._draw_button(screen, return_to_menu_button)
        
        button_y += button_height + 10
        
        if can_clear_enemy_tile:
            clear_button = {
                'rect': pygame.Rect(self.panel_x + 10, button_y, button_width, button_height),
                'text': self.loc.t('clear_enemy_tile'),
                'action': 'clear_enemy_tile',
                'color': (180, 100, 100)
            }
            self.buttons.append(clear_button)
            self._draw_button(screen, clear_button)
            button_y += button_height + 10
        
        if selected_tile and selected_tile.owner == current_player:
            if selected_tile.builder_unit and selected_tile.builder_unit.can_build:
                if not selected_tile.building and selected_tile.terrain not in ['mountain', 'water']:
                    build_button = {
                        'rect': pygame.Rect(self.panel_x + 10, button_y, button_width, button_height),
                        'text': self.loc.t('build'),
                        'action': 'open_build_popup',
                        'color': (100, 100, 180)
                    }
                    self.buttons.append(build_button)
                    self._draw_button(screen, build_button)
                    button_y += button_height + 10
            
            if selected_tile.building:
                from config import BUILDING_INFO, UNIT_INFO
                building_type = selected_tile.building.building_type
                building_info = BUILDING_INFO.get(building_type, {})
                can_train = building_info.get('can_train', [])
                
                can_train_now = False
                for unit_type in can_train:
                    unit_info = UNIT_INFO.get(unit_type, {})
                    is_builder = unit_info.get('can_build', False)
                    if is_builder:
                        if not selected_tile.builder_unit:
                            can_train_now = True
                            break
                    else:
                        if not selected_tile.unit:
                            can_train_now = True
                            break
                
                if can_train and can_train_now:
                    train_button = {
                        'rect': pygame.Rect(self.panel_x + 10, button_y, button_width, button_height),
                        'text': self.loc.t('train'),
                        'action': 'open_train_popup',
                        'color': (80, 150, 100)
                    }
                    self.buttons.append(train_button)
                    self._draw_button(screen, train_button)
                    button_y += button_height + 10
            
            if selected_tile.unit:
                move_text = self.loc.t('moved') if selected_tile.unit.moved_this_turn else self.loc.t('can_move')
                attack_text = self.loc.t('attacked') if selected_tile.unit.attacked_this_turn else self.loc.t('can_attack')
                unit_name = self.loc.get_unit_name(selected_tile.unit.unit_type)
                info_text = f"{unit_name}: {move_text}, {attack_text}"
                info_surface = self.font_small.render(info_text, True, TEXT_COLOR)
                screen.blit(info_surface, (self.panel_x + 10, button_y + 5))
                button_y += 20
            
            if selected_tile.builder_unit:
                move_text = self.loc.t('moved') if selected_tile.builder_unit.moved_this_turn else self.loc.t('can_move')
                attack_text = self.loc.t('attacked') if selected_tile.builder_unit.attacked_this_turn else self.loc.t('can_attack')
                unit_name = self.loc.get_unit_name(selected_tile.builder_unit.unit_type)
                info_text = f"{unit_name}: {move_text}, {attack_text}"
                info_surface = self.font_small.render(info_text, True, TEXT_COLOR)
                screen.blit(info_surface, (self.panel_x + 10, button_y + 5))
        
        if can_expand_territory:
            expand_button = {
                'rect': pygame.Rect(self.panel_x + 10, button_y, button_width, button_height),
                'text': self.loc.t('expand_territory'),
                'action': 'expand_territory',
                'color': (100, 150, 100)
            }
            self.buttons.append(expand_button)
            self._draw_button(screen, expand_button)
            button_y += button_height + 10
        
        return self.buttons
    
    def set_mouse_state(self, mouse_pos: Tuple[int, int], mouse_down: bool):
        self.mouse_pos = mouse_pos
        self.mouse_down = mouse_down
    
    def _get_button_id(self, button: Dict) -> str:
        action = button.get('action', '')
        text = button.get('text', '')
        return f"{action}_{text}"
    
    def _draw_button(self, screen: pygame.Surface, button: Dict, small: bool = False):
        button_id = self._get_button_id(button)
        
        if self.animation_manager:
            button_anim = self.animation_manager.get_button_animation(button_id)
            is_hovered = button['rect'].collidepoint(self.mouse_pos)
            dt = self.animation_manager.get_dt() if self.animation_manager else 0.016
            button_anim.update(is_hovered, self.mouse_down, dt)
            
            scale = button_anim.scale
            color_offset = button_anim.color_offset
            border_width = button_anim.border_width
        else:
            scale = 1.0
            color_offset = 0
            border_width = 2
            is_hovered = button['rect'].collidepoint(self.mouse_pos)
            if is_hovered:
                border_width = 3
        
        rect = button['rect']
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
        
        base_color = button['color']
        if color_offset != 0:
            draw_color = (
                max(0, min(255, base_color[0] + color_offset)),
                max(0, min(255, base_color[1] + color_offset)),
                max(0, min(255, base_color[2] + color_offset))
            )
        else:
            draw_color = base_color
        
        if is_hovered and color_offset == 0:
            draw_color = (
                min(255, base_color[0] + 20),
                min(255, base_color[1] + 20),
                min(255, base_color[2] + 20)
            )
        
        pygame.draw.rect(screen, draw_color, draw_rect)
        
        border_color = UI_COLORS.get('highlight_border', (100, 200, 255)) if is_hovered else (50, 50, 50)
        pygame.draw.rect(screen, border_color, draw_rect, border_width)
        
        font = self.font_small if small else self.font_medium
        text = button.get('text', '')
        
        try:
            text_surface = font.render(text, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=draw_rect.center)
            screen.blit(text_surface, text_rect)
        except Exception as e:
            fallback_font = pygame.font.Font(None, 16 if small else 20)
            text_surface = fallback_font.render(text, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=draw_rect.center)
            screen.blit(text_surface, text_rect)
    
    def handle_click(self, mouse_pos: Tuple[int, int], buttons: List[Dict]) -> Optional[str]:
        for button in buttons:
            if button.get('enabled', True) and button['rect'].collidepoint(mouse_pos):
                return button['action']
        return None
    
    def open_build_menu(self):
        pass
    
    def close_build_menu(self):
        pass
    
    def open_settings_menu(self):
        pass
    
    def close_settings_menu(self):
        pass
    
    def open_language_menu(self):
        pass
    
    def close_language_menu(self):
        pass
    
    def update_menu_animations(self, dt: float):
        pass
    
    def draw_combat_log(self, screen: pygame.Surface, messages: List[str]):
        log_x = 10
        log_y = 40
        log_width = self.panel_x - 30
        log_height = 100
        
        log_rect = pygame.Rect(log_x, log_y, log_width, log_height)
        pygame.draw.rect(screen, UI_PANEL_COLOR, log_rect)
        pygame.draw.rect(screen, (100, 100, 100), log_rect, 2)
        
        title = self.font_medium.render(self.loc.t('combat_log'), True, TEXT_COLOR)
        screen.blit(title, (log_x + 10, log_y + 5))
        
        y_offset = log_y + 30
        max_messages = 3
        
        start_index = max(0, len(messages) - max_messages)
        visible_messages = messages[start_index:]
        
        for msg in reversed(visible_messages):
            try:
                msg_surface = self.font_small.render(msg, True, TEXT_COLOR)
            except Exception:
                fallback_font = pygame.font.Font(None, 16)
                msg_surface = fallback_font.render(msg, True, TEXT_COLOR)
            screen.blit(msg_surface, (log_x + 10, y_offset))
            y_offset += 20
