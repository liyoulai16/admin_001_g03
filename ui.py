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
        
        self.build_menu_visible = False
        self.settings_menu_visible = False
        self.language_menu_visible = False
        self.menu_animation_progress = {}
        self.menu_animation_speed = 8.0
        self._menu_expanding = {}
        self._menu_collapsing = {}
        
        self._cached_build_menu_buttons = []
        self._cached_settings_menu_buttons = []
        self._cached_language_menu_buttons = []
    
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
        
        return_to_menu_button = {
            'rect': pygame.Rect(self.panel_x + 10, button_y, button_width, button_height),
            'text': self.loc.t('back_to_menu'),
            'action': 'return_to_menu',
            'color': (150, 100, 100)
        }
        self.buttons.append(return_to_menu_button)
        self._draw_button(screen, return_to_menu_button)
        
        button_y += button_height + 10
        
        if self.settings_menu_visible:
            self._draw_settings_menu(screen, button_y, button_width, button_height)
        elif self.language_menu_visible:
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
        
        if self.build_menu_visible and selected_tile:
            self._draw_build_menu(screen, current_player, selected_tile, button_y)
        
        return self.buttons
    
    def _draw_animated_button(self, screen: pygame.Surface, button: Dict, 
                                start_x: float, start_y: float, 
                                target_x: float, target_y: float,
                                progress: float, small: bool = False) -> Dict:
        import math
        
        def ease_out_cubic(t):
            return 1 - math.pow(1 - t, 3) if t < 1 else 1
        
        def ease_out_quad(t):
            return 1 - (1 - t) * (1 - t) if t < 1 else 1
        
        eased_progress = ease_out_cubic(progress)
        
        current_x = start_x + (target_x - start_x) * eased_progress
        current_y = start_y + (target_y - start_y) * eased_progress
        
        alpha = int(255 * min(progress * 1.5, 1.0))
        
        button_copy = button.copy()
        original_rect = button['rect']
        
        draw_rect = pygame.Rect(current_x, current_y, original_rect.width, original_rect.height)
        button_copy['rect'] = draw_rect
        button_copy['_target_rect'] = original_rect
        button_copy['_alpha'] = alpha
        
        button_copy['_is_clickable'] = progress > 0.15
        
        if progress > 0.02:
            base_color = button['color']
            color_alpha = (
                int(base_color[0] * alpha / 255),
                int(base_color[1] * alpha / 255),
                int(base_color[2] * alpha / 255),
            )
            
            pygame.draw.rect(screen, color_alpha, draw_rect)
            
            border_alpha = int(alpha * 0.8)
            border_color = (
                int(50 * border_alpha / 255),
                int(50 * border_alpha / 255),
                int(50 * border_alpha / 255),
            )
            pygame.draw.rect(screen, border_color, draw_rect, 2)
            
            font = self.font_small if small else self.font_medium
            text = button.get('text', '')
            
            try:
                text_surface = font.render(text, True, TEXT_COLOR)
                text_surface.set_alpha(alpha)
                text_rect = text_surface.get_rect(center=draw_rect.center)
                screen.blit(text_surface, text_rect)
            except Exception:
                fallback_font = pygame.font.Font(None, 16 if small else 20)
                text_surface = fallback_font.render(text, True, TEXT_COLOR)
                text_surface.set_alpha(alpha)
                text_rect = text_surface.get_rect(center=draw_rect.center)
                screen.blit(text_surface, text_rect)
        
        return button_copy
    
    def _draw_settings_menu(self, screen: pygame.Surface, start_y: int, width: int, height: int):
        import math
        
        menu_progress = self.menu_animation_progress.get('settings', 0.0)
        
        menu_y = start_y
        menu_width = width
        menu_height = height
        
        language_button = {
            'rect': pygame.Rect(self.panel_x + 10, menu_y, menu_width, menu_height),
            'text': self.loc.t('language'),
            'action': 'open_language_menu',
            'color': (80, 100, 120)
        }
        
        start_x = self.panel_x + self.panel_width
        start_y_lang = menu_y
        target_x = self.panel_x + 10
        target_y_lang = menu_y
        
        lang_progress = max(0, min(1, (menu_progress - 0.0) * 2.0))
        animated_lang_button = self._draw_animated_button(
            screen, language_button,
            start_x, start_y_lang, target_x, target_y_lang,
            lang_progress
        )
        self.buttons.append(animated_lang_button)
        
        menu_y += menu_height + 10
        
        close_button = {
            'rect': pygame.Rect(self.panel_x + 10, menu_y, menu_width, menu_height),
            'text': self.loc.t('cancel'),
            'action': 'close_settings_menu',
            'color': (120, 80, 80)
        }
        
        start_y_close = start_y + height + 10
        close_progress = max(0, min(1, (menu_progress - 0.3) * 2.0))
        animated_close_button = self._draw_animated_button(
            screen, close_button,
            start_x, start_y_close, target_x, menu_y,
            close_progress
        )
        self.buttons.append(animated_close_button)
    
    def _draw_language_menu(self, screen: pygame.Surface, start_y: int, width: int, height: int):
        import math
        
        menu_progress = self.menu_animation_progress.get('language', 0.0)
        
        menu_y = start_y
        menu_width = width
        menu_height = height
        
        chinese_available = self.font_manager.is_chinese_available()
        
        start_x = self.panel_x + self.panel_width
        target_x = self.panel_x + 10
        
        button_delay = 0.15
        
        en_button = {
            'rect': pygame.Rect(self.panel_x + 10, menu_y, menu_width, menu_height),
            'text': self.loc.t('language_en'),
            'action': 'set_language_en',
            'color': (100, 150, 100) if self.loc.get_language() == 'en' else (80, 100, 150)
        }
        
        en_progress = max(0, min(1, (menu_progress - 0.0) * 2.5))
        animated_en_button = self._draw_animated_button(
            screen, en_button,
            start_x, menu_y, target_x, menu_y,
            en_progress
        )
        self.buttons.append(animated_en_button)
        
        menu_y += menu_height + 5
        
        if chinese_available:
            zh_button = {
                'rect': pygame.Rect(self.panel_x + 10, menu_y, menu_width, menu_height),
                'text': self.loc.t('language_zh'),
                'action': 'set_language_zh',
                'enabled': True,
                'color': (100, 150, 100) if self.loc.get_language() == 'zh' else (80, 80, 80)
            }
            
            zh_progress = max(0, min(1, (menu_progress - button_delay) * 2.5))
            animated_zh_button = self._draw_animated_button(
                screen, zh_button,
                start_x, menu_y, target_x, menu_y,
                zh_progress
            )
            self.buttons.append(animated_zh_button)
        else:
            zh_button = {
                'rect': pygame.Rect(self.panel_x + 10, menu_y, menu_width, menu_height),
                'text': self.loc.t('language_zh') + ' (Install Font)',
                'action': 'show_font_help',
                'enabled': True,
                'color': (120, 100, 60)
            }
            
            zh_progress = max(0, min(1, (menu_progress - button_delay) * 2.5))
            animated_zh_button = self._draw_animated_button(
                screen, zh_button,
                start_x, menu_y, target_x, menu_y,
                zh_progress
            )
            self.buttons.append(animated_zh_button)
            
            if zh_progress > 0.5:
                hint_y = menu_y + menu_height + 10
                hint_text1 = self.font_small.render("* Put Chinese font (.ttf) in", True, (255, 200, 100))
                hint_text2 = self.font_small.render("  'fonts/' folder in game dir", True, (255, 200, 100))
                screen.blit(hint_text1, (self.panel_x + 12, hint_y))
                screen.blit(hint_text2, (self.panel_x + 12, hint_y + 18))
        
        menu_y += menu_height + 10
        
        back_button = {
            'rect': pygame.Rect(self.panel_x + 10, menu_y, menu_width, menu_height),
            'text': self.loc.t('cancel'),
            'action': 'close_language_menu',
            'color': (120, 80, 80)
        }
        
        back_progress = max(0, min(1, (menu_progress - button_delay * 2) * 2.5))
        animated_back_button = self._draw_animated_button(
            screen, back_button,
            start_x, menu_y, target_x, menu_y,
            back_progress
        )
        self.buttons.append(animated_back_button)
    
    def _draw_build_menu(self, screen: pygame.Surface, player: Player, tile: HexTile, start_y: int):
        import math
        
        menu_progress = self.menu_animation_progress.get('build', 0.0)
        
        menu_y = start_y
        menu_height = 30
        menu_width = self.panel_width - 30
        
        start_x = self.panel_x + self.panel_width
        target_x = self.panel_x + 15
        button_delay = 0.1
        
        if menu_progress > 0.1:
            title_alpha = int(255 * min(1, (menu_progress - 0.1) * 3))
            title = self.font_medium.render(self.loc.t('select_building'), True, TEXT_COLOR)
            title_surface = pygame.Surface(title.get_size(), pygame.SRCALPHA)
            title_surface.blit(title, (0, 0))
            title_surface.set_alpha(title_alpha)
            screen.blit(title_surface, (self.panel_x + 15, menu_y))
        menu_y += 35
        
        button_index = 0
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
            
            btn_progress = max(0, min(1, (menu_progress - button_delay * button_index) * 3.0))
            animated_button = self._draw_animated_button(
                screen, button,
                start_x, menu_y, target_x, menu_y,
                btn_progress,
                small=True
            )
            self.buttons.append(animated_button)
            
            menu_y += menu_height + 5
            button_index += 1
        
        close_button = {
            'rect': pygame.Rect(self.panel_x + 15, menu_y, menu_width, menu_height),
            'text': self.loc.t('cancel'),
            'action': 'close_build_menu',
            'color': (120, 80, 80)
        }
        
        close_progress = max(0, min(1, (menu_progress - button_delay * button_index) * 3.0))
        animated_close_button = self._draw_animated_button(
            screen, close_button,
            start_x, menu_y, target_x, menu_y,
            close_progress,
            small=True
        )
        self.buttons.append(animated_close_button)
    
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
            if not button.get('enabled', True):
                continue
            
            click_rect = button.get('_target_rect', button['rect'])
            
            is_clickable = button.get('_is_clickable', True)
            
            if is_clickable and click_rect.collidepoint(mouse_pos):
                return button['action']
        return None
    
    def open_build_menu(self):
        self.build_menu_visible = True
        self.settings_menu_visible = False
        self.language_menu_visible = False
        self._menu_expanding['build'] = True
        self._menu_collapsing.pop('build', None)
        self.menu_animation_progress['build'] = 0.0
    
    def close_build_menu(self):
        self._menu_collapsing['build'] = True
        self._menu_expanding.pop('build', None)
    
    def open_settings_menu(self):
        self.settings_menu_visible = True
        self.build_menu_visible = False
        self.language_menu_visible = False
        self._menu_expanding['settings'] = True
        self._menu_collapsing.pop('settings', None)
        self.menu_animation_progress['settings'] = 0.0
    
    def close_settings_menu(self):
        self._menu_collapsing['settings'] = True
        self._menu_expanding.pop('settings', None)
    
    def open_language_menu(self):
        self.language_menu_visible = True
        self.settings_menu_visible = False
        self.build_menu_visible = False
        self._menu_expanding['language'] = True
        self._menu_collapsing.pop('language', None)
        self.menu_animation_progress['language'] = 0.0
    
    def close_language_menu(self):
        self._menu_collapsing['language'] = True
        self._menu_expanding.pop('language', None)
    
    def update_menu_animations(self, dt: float):
        for menu_name in ['build', 'settings', 'language']:
            current_progress = self.menu_animation_progress.get(menu_name, 0.0)
            
            if self._menu_expanding.get(menu_name, False):
                if current_progress < 1.0:
                    new_progress = min(current_progress + dt * self.menu_animation_speed, 1.0)
                    self.menu_animation_progress[menu_name] = new_progress
                    
                    if new_progress >= 1.0:
                        self._menu_expanding[menu_name] = False
            
            elif self._menu_collapsing.get(menu_name, False):
                if current_progress > 0.0:
                    new_progress = max(current_progress - dt * self.menu_animation_speed * 1.5, 0.0)
                    self.menu_animation_progress[menu_name] = new_progress
                    
                    if new_progress <= 0.0:
                        self._menu_collapsing[menu_name] = False
                        if menu_name == 'build':
                            self.build_menu_visible = False
                        elif menu_name == 'settings':
                            self.settings_menu_visible = False
                        elif menu_name == 'language':
                            self.language_menu_visible = False
            else:
                is_visible = False
                if menu_name == 'build':
                    is_visible = self.build_menu_visible
                elif menu_name == 'settings':
                    is_visible = self.settings_menu_visible
                elif menu_name == 'language':
                    is_visible = self.language_menu_visible
                
                if is_visible and current_progress < 1.0:
                    self.menu_animation_progress[menu_name] = min(current_progress + dt * self.menu_animation_speed, 1.0)
    
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
