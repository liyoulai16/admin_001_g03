import pygame
from typing import Dict, Optional, Tuple, List
from config import (
    UI_PANEL_COLOR, TEXT_COLOR, HIGHLIGHT_COLOR, SELECTED_COLOR,
    BUILDING_INFO
)
from player import Player, Building, Unit
from hex_map import HexMap, HexTile
from localization import Localization
from font_manager import FontManager


class UI:
    def __init__(self, screen_width: int, screen_height: int, localization: Localization):
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
                            current_player: Player) -> List[Dict]:
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
            'action': 'open_settings_menu',
            'color': (100, 80, 150)
        }
        self.buttons.append(settings_button)
        self._draw_button(screen, settings_button)
        
        button_y += button_height + 10
        
        if self.settings_menu_open:
            self._draw_settings_menu(screen, button_y, button_width, button_height)
        elif self.language_menu_open:
            self._draw_language_menu(screen, button_y, button_width, button_height)
        elif selected_tile and selected_tile.owner == current_player:
            if not selected_tile.building and selected_tile.terrain not in ['mountain', 'water']:
                build_button = {
                    'rect': pygame.Rect(self.panel_x + 10, button_y, button_width, button_height),
                    'text': self.loc.t('build'),
                    'action': 'open_build_menu',
                    'color': (100, 100, 180)
                }
                self.buttons.append(build_button)
                self._draw_button(screen, build_button)
                button_y += button_height + 10
            
            if selected_tile.unit:
                move_text = self.loc.t('moved') if selected_tile.unit.moved_this_turn else self.loc.t('can_move')
                attack_text = self.loc.t('attacked') if selected_tile.unit.attacked_this_turn else self.loc.t('can_attack')
                info_text = f"{self.loc.t('status')}: {move_text}, {attack_text}"
                info_surface = self.font_small.render(info_text, True, TEXT_COLOR)
                screen.blit(info_surface, (self.panel_x + 10, button_y + 5))
        
        if self.build_menu_open and selected_tile:
            self._draw_build_menu(screen, current_player, selected_tile)
        
        return self.buttons
    
    def _draw_settings_menu(self, screen: pygame.Surface, start_y: int, width: int, height: int):
        menu_y = start_y
        menu_width = width
        menu_height = height
        
        language_button = {
            'rect': pygame.Rect(self.panel_x + 10, menu_y, menu_width, menu_height),
            'text': self.loc.t('language'),
            'action': 'open_language_menu',
            'color': (80, 100, 120)
        }
        self.buttons.append(language_button)
        self._draw_button(screen, language_button)
        
        menu_y += menu_height + 10
        
        close_button = {
            'rect': pygame.Rect(self.panel_x + 10, menu_y, menu_width, menu_height),
            'text': self.loc.t('cancel'),
            'action': 'close_settings_menu',
            'color': (120, 80, 80)
        }
        self.buttons.append(close_button)
        self._draw_button(screen, close_button)
    
    def _draw_language_menu(self, screen: pygame.Surface, start_y: int, width: int, height: int):
        menu_y = start_y
        menu_width = width
        menu_height = height
        
        chinese_available = self.font_manager.is_chinese_available()
        
        en_button = {
            'rect': pygame.Rect(self.panel_x + 10, menu_y, menu_width, menu_height),
            'text': 'English',
            'action': 'set_language_en',
            'color': (100, 150, 100) if self.loc.get_language() == 'en' else (80, 100, 150)
        }
        self.buttons.append(en_button)
        self._draw_button(screen, en_button)
        
        menu_y += menu_height + 5
        
        if chinese_available:
            zh_button = {
                'rect': pygame.Rect(self.panel_x + 10, menu_y, menu_width, menu_height),
                'text': self.loc.t('language_zh'),
                'action': 'set_language_zh',
                'enabled': True,
                'color': (100, 150, 100) if self.loc.get_language() == 'zh' else (80, 80, 80)
            }
            self.buttons.append(zh_button)
            self._draw_button(screen, zh_button)
        else:
            zh_button = {
                'rect': pygame.Rect(self.panel_x + 10, menu_y, menu_width, menu_height),
                'text': 'Chinese (Install Font)',
                'action': 'show_font_help',
                'enabled': True,
                'color': (120, 100, 60)
            }
            self.buttons.append(zh_button)
            self._draw_button(screen, zh_button)
            
            menu_y += menu_height + 10
            
            hint_y = menu_y
            hint_text1 = self.font_small.render("* Put Chinese font (.ttf) in", True, (255, 200, 100))
            hint_text2 = self.font_small.render("  'fonts/' folder in game dir", True, (255, 200, 100))
            screen.blit(hint_text1, (self.panel_x + 12, hint_y))
            screen.blit(hint_text2, (self.panel_x + 12, hint_y + 18))
            menu_y += 36
        
        menu_y += menu_height + 10
        
        back_button = {
            'rect': pygame.Rect(self.panel_x + 10, menu_y, menu_width, menu_height),
            'text': self.loc.t('cancel'),
            'action': 'close_language_menu',
            'color': (120, 80, 80)
        }
        self.buttons.append(back_button)
        self._draw_button(screen, back_button)
    
    def _draw_build_menu(self, screen: pygame.Surface, player: Player, tile: HexTile):
        menu_y = 400
        menu_height = 30
        menu_width = self.panel_width - 30
        
        title = self.font_medium.render(self.loc.t('select_building'), True, TEXT_COLOR)
        screen.blit(title, (self.panel_x + 15, menu_y))
        menu_y += 35
        
        for building_type, info in BUILDING_INFO.items():
            cost = info['cost']
            can_afford = player.can_afford(cost)
            
            button_color = (80, 80, 150) if can_afford else (80, 80, 80)
            
            cost_str = ", ".join([f"{self.loc.get_resource_icon(k)}{v}" for k, v in cost.items()])
            building_name = self.loc.get_building_name(building_type)
            button_text = f"{building_name} ({cost_str})"
            
            button = {
                'rect': pygame.Rect(self.panel_x + 15, menu_y, menu_width, menu_height),
                'text': button_text,
                'action': f'build_{building_type}',
                'color': button_color,
                'enabled': can_afford
            }
            self.buttons.append(button)
            self._draw_button(screen, button, small=True)
            menu_y += menu_height + 5
        
        close_button = {
            'rect': pygame.Rect(self.panel_x + 15, menu_y, menu_width, menu_height),
            'text': self.loc.t('cancel'),
            'action': 'close_build_menu',
            'color': (120, 80, 80)
        }
        self.buttons.append(close_button)
        self._draw_button(screen, close_button, small=True)
    
    def _draw_button(self, screen: pygame.Surface, button: Dict, small: bool = False):
        pygame.draw.rect(screen, button['color'], button['rect'])
        pygame.draw.rect(screen, (50, 50, 50), button['rect'], 2)
        
        font = self.font_small if small else self.font_medium
        text = button.get('text', '')
        
        try:
            text_surface = font.render(text, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=button['rect'].center)
            screen.blit(text_surface, text_rect)
        except Exception as e:
            fallback_font = pygame.font.Font(None, 16 if small else 20)
            text_surface = fallback_font.render(text, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=button['rect'].center)
            screen.blit(text_surface, text_rect)
    
    def handle_click(self, mouse_pos: Tuple[int, int], buttons: List[Dict]) -> Optional[str]:
        for button in buttons:
            if button.get('enabled', True) and button['rect'].collidepoint(mouse_pos):
                return button['action']
        return None
    
    def open_build_menu(self):
        self.build_menu_open = True
        self.settings_menu_open = False
        self.language_menu_open = False
    
    def close_build_menu(self):
        self.build_menu_open = False
    
    def open_settings_menu(self):
        self.settings_menu_open = True
        self.build_menu_open = False
        self.language_menu_open = False
    
    def close_settings_menu(self):
        self.settings_menu_open = False
    
    def open_language_menu(self):
        self.language_menu_open = True
        self.settings_menu_open = False
        self.build_menu_open = False
    
    def close_language_menu(self):
        self.language_menu_open = False
    
    def draw_combat_log(self, screen: pygame.Surface, messages: List[str], max_messages: int = 5):
        log_y = self.screen_height - 150
        log_height = 140
        
        panel_rect = pygame.Rect(10, log_y, self.screen_width - self.panel_width - 30, log_height)
        pygame.draw.rect(screen, (30, 35, 45), panel_rect)
        pygame.draw.rect(screen, (80, 80, 80), panel_rect, 1)
        
        title = self.font_medium.render(self.loc.t('combat_log'), True, TEXT_COLOR)
        screen.blit(title, (20, log_y + 5))
        
        start_idx = max(0, len(messages) - max_messages)
        display_messages = messages[start_idx:]
        
        y_offset = log_y + 30
        for msg in display_messages:
            try:
                text_surface = self.font_small.render(msg, True, (200, 200, 200))
                screen.blit(text_surface, (20, y_offset))
            except:
                fallback_font = pygame.font.Font(None, 16)
                text_surface = fallback_font.render(msg, True, (200, 200, 200))
                screen.blit(text_surface, (20, y_offset))
            y_offset += 22
