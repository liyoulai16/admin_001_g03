import pygame
import sys
import math
from typing import Dict, Tuple, Optional, List
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BACKGROUND_COLOR, 
    HEX_SIZE, MAP_ROWS, MAP_COLS,
    BUILDING_INFO, SELECTED_COLOR, GAME_STATES, UI_COLORS,
    TERRAIN_DECORATION_COLORS, BUILDING_DETAIL_COLORS, UNIT_DETAIL_COLORS,
    ZOOM_CONFIG, EDGE_SCROLL_CONFIG,
    UI_PANEL_COLOR, TEXT_COLOR, HIGHLIGHT_COLOR,
    EXPAND_TERRITORY_COST, TERRAIN_TYPES, TERRAIN_COLORS, RIVER_COLORS, HEX_DIRECTIONS
)
from hex_map import HexMap, HexTile
from terrain_generator import TerrainGenerator
from player import Player, Building, Unit
from ai import SimpleAI
from ui import UI
from localization import Localization
from animation import AnimationManager
from menu import MainMenu, SettingsMenu
from help_menu import HelpMenu
from popup import SettingsPopup, BuildPopup, TrainPopup


class Game:
    def __init__(self, default_language: str = 'en'):
        pygame.init()
        pygame.font.init()
        
        self.loc = Localization(default_language)
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(self.loc.t('game_title'))
        self.clock = pygame.time.Clock()
        
        self.animation_manager = AnimationManager()
        
        self.ui = UI(SCREEN_WIDTH, SCREEN_HEIGHT, self.loc, self.animation_manager)
        
        self.main_menu = MainMenu(self.screen, self.loc, self.animation_manager)
        self.settings_menu = SettingsMenu(self.screen, self.loc, self.animation_manager)
        self.help_menu = HelpMenu(self.screen, self.loc)
        
        self.game_state = GAME_STATES['MENU']
        self.previous_state = None
        
        self.hex_map: Optional[HexMap] = None
        self.players: List[Player] = []
        self.ais: Dict[int, SimpleAI] = {}
        self.current_player_idx = 0
        self.turn = 1
        
        self.selected_tile: Optional[HexTile] = None
        self.selected_unit: Optional[Unit] = None
        self.map_offset_x = 50
        self.map_offset_y = 50
        
        self.zoom_level = ZOOM_CONFIG['default_zoom']
        self.min_zoom = ZOOM_CONFIG['min_zoom']
        self.max_zoom = ZOOM_CONFIG['max_zoom']
        self.zoom_step = ZOOM_CONFIG['zoom_step']
        self.scroll_speed = EDGE_SCROLL_CONFIG['scroll_speed']
        self.edge_threshold = EDGE_SCROLL_CONFIG['edge_threshold']
        
        self.unit_detail_panel_visible = False
        self.unit_detail_panel_rect = pygame.Rect(
            SCREEN_WIDTH - 300, SCREEN_HEIGHT - 350, 280, 320
        )
        
        self.tile_detail_panel_visible = False
        self.tile_detail_tile: Optional[HexTile] = None
        self.tile_detail_panel_rect = pygame.Rect(
            SCREEN_WIDTH - 300, SCREEN_HEIGHT - 450, 280, 420
        )
        
        self.unit_selection_pending: bool = False
        self.unit_selection_tile: Optional[HexTile] = None
        self.unit_selection_buttons: List[Dict] = []
        
        self.game_messages: List[str] = []
        self.running = True
        
        self.mouse_pos = (0, 0)
        self.mouse_down = False
        self.mouse_buttons_pressed = {1: False, 2: False, 3: False}
        
        self.settings_popup = None
        self.build_popup = None
        self.train_popup = None
        self._popup_initialized = False
    
    def _init_popups(self):
        if self._popup_initialized:
            return
        
        self.settings_popup = SettingsPopup(
            300, 280, self.loc, self.ui.get_font_manager()
        )
        self.settings_popup.update_position(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        if self.players:
            self.build_popup = BuildPopup(
                300, 450, self.loc, self.ui.get_font_manager(),
                self.get_current_player()
            )
            self.build_popup.update_position(SCREEN_WIDTH, SCREEN_HEIGHT)
            
            self.train_popup = TrainPopup(
                300, 280, self.loc, self.ui.get_font_manager(),
                self.get_current_player()
            )
            self.train_popup.update_position(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        self._popup_initialized = True
    
    def _refresh_popups(self):
        if self._popup_initialized:
            if self.players:
                self.settings_popup = SettingsPopup(
                    300, 280, self.loc, self.ui.get_font_manager()
                )
                self.settings_popup.update_position(SCREEN_WIDTH, SCREEN_HEIGHT)
                
                self.build_popup = BuildPopup(
                    300, 450, self.loc, self.ui.get_font_manager(),
                    self.get_current_player()
                )
                self.build_popup.update_position(SCREEN_WIDTH, SCREEN_HEIGHT)
                
                self.train_popup = TrainPopup(
                    300, 280, self.loc, self.ui.get_font_manager(),
                    self.get_current_player()
                )
                self.train_popup.update_position(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    def set_language(self, language: str):
        self.loc.set_language(language)
        self.ui.set_localization(self.loc)
        pygame.display.set_caption(self.loc.t('game_title'))
        
        self.main_menu = MainMenu(self.screen, self.loc, self.animation_manager)
        self.settings_menu = SettingsMenu(self.screen, self.loc, self.animation_manager)
        self.help_menu = HelpMenu(self.screen, self.loc)
        
        self._popup_initialized = False
        
        for i, player in enumerate(self.players):
            if player.is_ai:
                player.name = f"{self.loc.t('ai')} {player.player_id}"
            else:
                player.name = f"{self.loc.t('player')} {player.player_id}"
    
    def _get_msg(self, key: str, *args) -> str:
        template = self.loc.t(key)
        if args:
            return template.format(*args)
        return template
    
    def new_game(self):
        self.hex_map = HexMap(MAP_ROWS, MAP_COLS)
        terrain_gen = TerrainGenerator(seed=42)
        terrain_gen.generate_random_map(self.hex_map, MAP_ROWS, MAP_COLS)
        
        player1 = Player(player_id=1, is_ai=False)
        player2 = Player(player_id=2, is_ai=True)
        
        player1.name = f"{self.loc.t('player')} 1"
        player2.name = f"{self.loc.t('ai')} 2"
        
        self.players = [player1, player2]
        self.ais = {2: SimpleAI(player2)}
        
        start_positions = terrain_gen.get_start_positions(self.hex_map, 2)
        
        for i, player in enumerate(self.players):
            if i < len(start_positions):
                q, r = start_positions[i]
                tile = self.hex_map.get_tile(q, r)
                if tile:
                    tile.owner = player
                    building = Building('town', q, r, player)
                    tile.building = building
                    player.add_building(building)
                    player.tiles_owned = 1
                    
                    unit = Unit('warrior', q, r, player)
                    tile.unit = unit
                    player.add_unit(unit)
        
        self.current_player_idx = 0
        self.turn = 1
        self.selected_tile = None
        self.selected_unit = None
        self.game_messages = [self._get_msg('msg_game_start')]
        self.ui.close_build_menu()
        self.ui.close_settings_menu()
        self.ui.close_language_menu()
    
    def get_current_player(self) -> Player:
        return self.players[self.current_player_idx]
    
    def get_screen_to_hex(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        x = (screen_x - self.map_offset_x) / self.zoom_level
        y = (screen_y - self.map_offset_y) / self.zoom_level
        return self.hex_map.pixel_to_hex(x, y)
    
    def handle_tile_click(self, q: int, r: int):
        tile = self.hex_map.get_tile(q, r)
        if not tile:
            return
        
        if self.animation_manager:
            self.animation_manager.add_tile_selection((q, r))
        
        if self.selected_unit and self.selected_unit.can_move_to(self.hex_map, q, r):
            self.move_unit(self.selected_unit, tile)
            return
        
        if self.selected_unit and self.selected_unit.can_attack(self.hex_map, q, r):
            self.attack_with_unit(self.selected_unit, tile)
            return
        
        self.select_tile(tile)
    
    def select_tile(self, tile: HexTile):
        self.hex_map.clear_highlights()
        self.selected_tile = tile
        self.selected_unit = None
        tile.selected = True
        self.ui.close_build_menu()
        
        self.unit_selection_pending = False
        self.unit_selection_tile = None
        self.unit_selection_buttons = []
        
        current_player = self.get_current_player()
        has_military = tile.unit and tile.unit.owner == current_player
        has_builder = tile.builder_unit and tile.builder_unit.owner == current_player
        
        if has_military and has_builder:
            self.unit_selection_pending = True
            self.unit_selection_tile = tile
            self._create_unit_selection_buttons(tile)
        elif has_military:
            self.selected_unit = tile.unit
            self.show_unit_range(tile.unit)
        elif has_builder:
            self.selected_unit = tile.builder_unit
            self.show_unit_range(tile.builder_unit)
    
    def show_unit_range(self, unit: Unit):
        if not unit.moved_this_turn:
            reachable = self.hex_map.get_tiles_in_range(unit.tile_q, unit.tile_r, unit.movement)
            for q, r in reachable:
                target_tile = self.hex_map.get_tile(q, r)
                if target_tile and unit.can_move_to(self.hex_map, q, r):
                    target_tile.reachable = True
        
        if not unit.attacked_this_turn:
            attackable = self.hex_map.get_neighbors(unit.tile_q, unit.tile_r)
            for q, r in attackable:
                target_tile = self.hex_map.get_tile(q, r)
                if target_tile and unit.can_attack(self.hex_map, q, r):
                    target_tile.attackable = True
    
    def _create_unit_selection_buttons(self, tile: HexTile):
        x, y = self.hex_map.hex_to_pixel(tile.q, tile.r)
        screen_x = x + self.map_offset_x
        screen_y = y + self.map_offset_y
        
        button_width = 70
        button_height = 25
        
        military_unit_name = self.loc.get_unit_name(tile.unit.unit_type) if tile.unit else "Military"
        builder_unit_name = self.loc.get_unit_name(tile.builder_unit.unit_type) if tile.builder_unit else "Builder"
        
        military_button = {
            'rect': pygame.Rect(screen_x - button_width - 5, screen_y - button_height - 30, button_width, button_height),
            'text': military_unit_name,
            'action': 'select_military_unit',
            'color': (100, 120, 180),
            'unit': tile.unit
        }
        
        builder_button = {
            'rect': pygame.Rect(screen_x + 5, screen_y - button_height - 30, button_width, button_height),
            'text': builder_unit_name,
            'action': 'select_builder_unit',
            'color': (100, 180, 120),
            'unit': tile.builder_unit
        }
        
        self.unit_selection_buttons = [military_button, builder_button]
    
    def _draw_unit_selection_buttons(self, screen: pygame.Surface):
        if not self.unit_selection_pending:
            return
        
        for button in self.unit_selection_buttons:
            rect = button['rect']
            is_hovered = rect.collidepoint(self.mouse_pos)
            
            color = button['color']
            if is_hovered:
                color = (min(255, color[0] + 30), min(255, color[1] + 30), min(255, color[2] + 30))
            
            pygame.draw.rect(screen, color, rect)
            border_color = (255, 255, 255) if is_hovered else (150, 150, 150)
            pygame.draw.rect(screen, border_color, rect, 2)
            
            text = button['text']
            try:
                text_surface = self.ui.font_small.render(text, True, (255, 255, 255))
            except Exception:
                fallback_font = pygame.font.Font(None, 16)
                text_surface = fallback_font.render(text, True, (255, 255, 255))
            
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)
    
    def _handle_unit_selection_click(self, mouse_pos: Tuple[int, int]) -> Optional[str]:
        if not self.unit_selection_pending:
            return None
        
        for button in self.unit_selection_buttons:
            if button['rect'].collidepoint(mouse_pos):
                return button['action']
        
        return None
    
    def _select_specific_unit(self, action: str):
        if not self.unit_selection_tile:
            return
        
        if action == 'select_military_unit' and self.unit_selection_tile.unit:
            self.selected_unit = self.unit_selection_tile.unit
            self.show_unit_range(self.unit_selection_tile.unit)
        elif action == 'select_builder_unit' and self.unit_selection_tile.builder_unit:
            self.selected_unit = self.unit_selection_tile.builder_unit
            self.show_unit_range(self.unit_selection_tile.builder_unit)
        
        self.unit_selection_pending = False
        self.unit_selection_buttons = []
    
    def move_unit(self, unit: Unit, target_tile: HexTile):
        source_tile = self.hex_map.get_tile(unit.tile_q, unit.tile_r)
        if not source_tile:
            return
        
        if self.animation_manager:
            start_x, start_y = self.hex_map.hex_to_pixel(unit.tile_q, unit.tile_r)
            end_x, end_y = self.hex_map.hex_to_pixel(target_tile.q, target_tile.r)
            start_screen_x = start_x * self.zoom_level + self.map_offset_x
            start_screen_y = start_y * self.zoom_level + self.map_offset_y
            end_screen_x = end_x * self.zoom_level + self.map_offset_x
            end_screen_y = end_y * self.zoom_level + self.map_offset_y
            
            unit_id = id(unit)
            self.animation_manager.add_unit_move(unit_id, (start_screen_x, start_screen_y), 
                                                    (end_screen_x, end_screen_y))
        
        if unit.can_build:
            source_tile.builder_unit = None
        else:
            source_tile.unit = None
        
        unit.tile_q = target_tile.q
        unit.tile_r = target_tile.r
        
        if unit.can_build:
            target_tile.builder_unit = unit
        else:
            target_tile.unit = unit
        
        unit.moved_this_turn = True
        
        self.select_tile(target_tile)
    
    def _has_adjacent_ally(self, tile, current_player):
        neighbors = self.hex_map.get_neighbors(tile.q, tile.r)
        for nq, nr in neighbors:
            neighbor_tile = self.hex_map.get_tile(nq, nr)
            if neighbor_tile and neighbor_tile.owner == current_player:
                return True
        return False
    
    def _can_expand_now(self, tile, current_player):
        if not tile:
            return False
        if not tile.builder_unit:
            return False
        if not tile.builder_unit.can_expand_territory:
            return False
        if tile.builder_unit.expanded_territory_this_turn:
            return False
        if tile.owner == current_player:
            return False
        if tile.owner is not None:
            return False
        terrain_info = TERRAIN_TYPES.get(tile.terrain, {})
        if not terrain_info.get('passable', True):
            return False
        if not self._has_adjacent_ally(tile, current_player):
            return False
        return True
    
    def expand_territory(self):
        if not self.selected_tile:
            return
        
        if not self.selected_tile.builder_unit:
            return
        
        builder = self.selected_tile.builder_unit
        if not builder.can_expand_territory:
            return
        
        current_player = self.get_current_player()
        builder_tile = self.selected_tile
        
        if builder.expanded_territory_this_turn:
            self.add_message(self._get_msg('msg_already_expanded_this_turn'))
            return
        
        if builder_tile.owner == current_player:
            self.add_message(self._get_msg('msg_cannot_expand_from_own_tile'))
            return
        
        terrain_info = TERRAIN_TYPES.get(builder_tile.terrain, {})
        if not terrain_info.get('passable', True):
            self.add_message(self._get_msg('msg_cannot_expand_impassable'))
            return
        
        if not self._has_adjacent_ally(builder_tile, current_player):
            self.add_message(self._get_msg('msg_no_adjacent_ally_territory'))
            return
        
        if not current_player.can_afford(EXPAND_TERRITORY_COST):
            self.add_message(self._get_msg('msg_not_enough_resources'))
            return
        
        if current_player.spend_resources(EXPAND_TERRITORY_COST):
            old_owner = builder_tile.owner
            
            if builder_tile.owner:
                builder_tile.owner.tiles_owned -= 1
            
            builder_tile.owner = current_player
            current_player.tiles_owned += 1
            
            builder.expanded_territory_this_turn = True
            
            unit_name = self.loc.get_unit_name(builder.unit_type)
            if old_owner:
                msg = f"{unit_name} {self._get_msg('msg_captured_enemy_tile')}"
            else:
                msg = f"{unit_name} {self._get_msg('msg_captured_neutral_tile')}"
            self.add_message(msg)
            
            if self.animation_manager:
                x, y = self.hex_map.hex_to_pixel(builder_tile.q, builder_tile.r)
                screen_x = x * self.zoom_level + self.map_offset_x
                screen_y = y * self.zoom_level + self.map_offset_y
                self.animation_manager.particle_system.emit(
                    screen_x, screen_y, current_player.color, count=20, spread=100
                )
    
    def attack_with_unit(self, unit: Unit, target_tile: HexTile):
        unit.attacked_this_turn = True
        unit_name = self.loc.get_unit_name(unit.unit_type)
        
        if self.animation_manager:
            start_x, start_y = self.hex_map.hex_to_pixel(unit.tile_q, unit.tile_r)
            target_x, target_y = self.hex_map.hex_to_pixel(target_tile.q, target_tile.r)
            start_screen_x = start_x * self.zoom_level + self.map_offset_x
            start_screen_y = start_y * self.zoom_level + self.map_offset_y
            target_screen_x = target_x * self.zoom_level + self.map_offset_x
            target_screen_y = target_y * self.zoom_level + self.map_offset_y
            
            unit_id = id(unit)
            self.animation_manager.add_unit_attack(unit_id, (start_screen_x, start_screen_y),
                                                      (target_screen_x, target_screen_y))
        
        target_unit = None
        is_builder_target = False
        
        if target_tile.unit and target_tile.unit.owner != unit.owner:
            target_unit = target_tile.unit
            is_builder_target = False
        elif target_tile.builder_unit and target_tile.builder_unit.owner != unit.owner:
            target_unit = target_tile.builder_unit
            is_builder_target = True
        
        if target_unit:
            target = target_unit
            target_name = self.loc.get_unit_name(target.unit_type)
            damage = max(1, unit.attack - target.defense // 2)
            target.health -= damage
            
            msg = f"{unit_name} {self._get_msg('msg_attacked')} {target_name}, {damage} {self._get_msg('msg_damage')}"
            
            if target.health <= 0:
                target.owner.remove_unit(target)
                if is_builder_target:
                    target_tile.builder_unit = None
                else:
                    target_tile.unit = None
                msg += f", {target_name} {self._get_msg('msg_destroyed')}"
                
                if self.animation_manager:
                    x, y = self.hex_map.hex_to_pixel(target_tile.q, target_tile.r)
                    screen_x = x * self.zoom_level + self.map_offset_x
                    screen_y = y * self.zoom_level + self.map_offset_y
                    self.animation_manager.particle_system.emit(
                        screen_x, screen_y, (255, 100, 100), count=30, spread=120
                    )
            
            self.add_message(msg)
        
        elif target_tile.building and target_tile.building.owner != unit.owner:
            target = target_tile.building
            target_name = self.loc.get_building_name(target.building_type)
            damage = max(1, unit.attack - 5)
            target.health -= damage
            
            msg = f"{unit_name} {self._get_msg('msg_attacked')} {target_name}, {damage} {self._get_msg('msg_damage')}"
            
            if target.health <= 0:
                target.owner.remove_building(target)
                target_tile.building = None
                msg += f", {target_name} {self._get_msg('msg_destroyed')}"
            
            self.add_message(msg)
        
        elif target_tile.owner and target_tile.owner != unit.owner:
            if not target_tile.unit and not target_tile.building:
                if target_tile.owner:
                    target_tile.owner.tiles_owned -= 1
                
                target_tile.owner = None
                self.add_message(f"{unit_name} {self._get_msg('msg_cleared_enemy_tile')}")
        
        self.select_tile(target_tile)
    
    def train_unit(self, unit_type: str):
        from config import UNIT_INFO, BUILDING_INFO
        if not self.selected_tile:
            return
        
        player = self.get_current_player()
        if self.selected_tile.owner != player:
            self.add_message(self._get_msg('msg_can_only_train_own'))
            return
        
        if not self.selected_tile.building:
            self.add_message(self._get_msg('msg_need_training_building'))
            return
        
        building_type = self.selected_tile.building.building_type
        building_info = BUILDING_INFO.get(building_type, {})
        can_train = building_info.get('can_train', [])
        
        if unit_type not in can_train:
            self.add_message(self._get_msg('msg_cannot_train_this_unit'))
            return
        
        unit_info = UNIT_INFO.get(unit_type, {})
        is_builder = unit_info.get('can_build', False)
        
        if is_builder:
            if self.selected_tile.builder_unit:
                self.add_message(self._get_msg('msg_tile_has_builder'))
                return
        else:
            if self.selected_tile.unit:
                self.add_message(self._get_msg('msg_tile_has_unit'))
                return
        
        if unit_type not in UNIT_INFO:
            return
        
        cost = UNIT_INFO[unit_type]['cost']
        if not player.can_afford(cost):
            self.add_message(self._get_msg('msg_not_enough_resources'))
            return
        
        if player.spend_resources(cost):
            unit = Unit(unit_type, self.selected_tile.q, self.selected_tile.r, player)
            
            if unit.can_build:
                self.selected_tile.builder_unit = unit
            else:
                self.selected_tile.unit = unit
            
            player.add_unit(unit)
            
            name = self.loc.get_unit_name(unit_type)
            self.add_message(f"{self._get_msg('msg_trained')} {name}")
            
            if self.train_popup:
                self.train_popup.hide()
            
            if self.animation_manager:
                x, y = self.hex_map.hex_to_pixel(self.selected_tile.q, self.selected_tile.r)
                screen_x = x * self.zoom_level + self.map_offset_x
                screen_y = y * self.zoom_level + self.map_offset_y
                self.animation_manager.particle_system.emit(
                    screen_x, screen_y, player.color, count=20, spread=80
                )
    
    def build_structure(self, building_type: str):
        if not self.selected_tile:
            return
        
        player = self.get_current_player()
        if self.selected_tile.owner != player:
            self.add_message(self._get_msg('msg_can_only_build_own'))
            return
        
        if not self.selected_tile.builder_unit or not self.selected_tile.builder_unit.can_build:
            self.add_message(self._get_msg('msg_need_builder'))
            return
        
        if self.selected_tile.building:
            self.add_message(self._get_msg('msg_tile_has_building'))
            return
        
        building_info = BUILDING_INFO.get(building_type, {})
        required_feature = building_info.get('required_feature', [])
        
        if required_feature:
            if self.selected_tile.feature not in required_feature:
                from config import FEATURE_NAMES
                feature_names = ", ".join([FEATURE_NAMES.get(t, t) for t in required_feature])
                self.add_message(f"{self.loc.get_building_name(building_type)} can only be built on {feature_names}!")
                return
        
        if building_type not in BUILDING_INFO:
            return
        
        cost = BUILDING_INFO[building_type]['cost']
        if not player.can_afford(cost):
            self.add_message(self._get_msg('msg_not_enough_resources'))
            return
        
        if player.spend_resources(cost):
            building = Building(building_type, self.selected_tile.q, self.selected_tile.r, player)
            self.selected_tile.building = building
            player.add_building(building)
            
            name = self.loc.get_building_name(building_type)
            self.add_message(f"{self._get_msg('msg_built')} {name}")
            self.ui.close_build_menu()
            
            if self.animation_manager:
                x, y = self.hex_map.hex_to_pixel(self.selected_tile.q, self.selected_tile.r)
                screen_x = x * self.zoom_level + self.map_offset_x
                screen_y = y * self.zoom_level + self.map_offset_y
                self.animation_manager.particle_system.emit(
                    screen_x, screen_y, player.color, count=25, spread=100
                )
    
    def end_turn(self):
        current_player = self.get_current_player()
        
        for unit in current_player.units:
            unit.reset_for_new_turn()
        
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        next_player = self.get_current_player()
        
        self.hex_map.clear_highlights()
        self.selected_tile = None
        self.selected_unit = None
        self.ui.close_build_menu()
        
        if next_player.is_ai and next_player.player_id in self.ais:
            self.add_message(f"--- {self.loc.t('ai')} {next_player.player_id} {self._get_msg('msg_ai_turn')} ---")
            ai = self.ais[next_player.player_id]
            result = ai.take_turn(self.hex_map)
            
            for unit in next_player.units:
                unit.reset_for_new_turn()
            
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            self.turn += 1
            
            human_player = self.get_current_player()
            income = human_player.calculate_income()
            human_player.add_resources(income)
            
            income_str = ", ".join([f"{k}+{v}" for k, v in income.items() if v > 0])
            if income_str:
                self.add_message(f"{self._get_msg('msg_new_turn_gained')} {income_str}")
        else:
            if self.current_player_idx == 0:
                self.turn += 1
            
            income = next_player.calculate_income()
            next_player.add_resources(income)
            
            income_str = ", ".join([f"{k}+{v}" for k, v in income.items() if v > 0])
            if income_str:
                self.add_message(f"{self._get_msg('msg_new_turn_gained')} {income_str}")
        
        self.check_game_end()
    
    def check_game_end(self):
        for player in self.players:
            if player.tiles_owned <= 0 and len(player.units) <= 0:
                winner = [p for p in self.players if p != player][0]
                self.add_message(f"{self._get_msg('msg_game_over')} {winner.name} {self._get_msg('msg_wins')}")
                self.running = False
                return
    
    def add_message(self, msg: str):
        self.game_messages.append(msg)
        if len(self.game_messages) > 50:
            self.game_messages = self.game_messages[-50:]
    
    def draw(self):
        if self.game_state == GAME_STATES['MENU']:
            self.main_menu.update()
            self.main_menu.draw()
        elif self.game_state == GAME_STATES['SETTINGS']:
            self.settings_menu.update()
            self.settings_menu.draw()
        elif self.game_state == GAME_STATES['PLAYING'] or self.game_state == GAME_STATES['PAUSED']:
            self._draw_game()
        elif self.game_state == GAME_STATES['HELP']:
            self.help_menu.update()
            self.help_menu.draw()
        
        pygame.display.flip()
    
    def _draw_game(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        if not self._popup_initialized:
            self._init_popups()
        
        if self.animation_manager:
            self.animation_manager.update_all()
            dt = self.animation_manager.get_dt()
            self.ui.update_menu_animations(dt)
        
        self._handle_edge_scroll()
        
        if self.hex_map:
            for (q, r), tile in self.hex_map.tiles.items():
                x, y = self.hex_map.hex_to_pixel(q, r)
                screen_x = x * self.zoom_level + self.map_offset_x
                screen_y = y * self.zoom_level + self.map_offset_y
                
                if screen_x < -HEX_SIZE * self.zoom_level * 2 or screen_x > SCREEN_WIDTH + HEX_SIZE * self.zoom_level * 2:
                    continue
                if screen_y < -HEX_SIZE * self.zoom_level * 2 or screen_y > SCREEN_HEIGHT + HEX_SIZE * self.zoom_level * 2:
                    continue
                
                corners = self._get_scaled_hex_corners(screen_x, screen_y)
                
                tile_scale = 1.0
                if self.animation_manager and (q, r) in self.animation_manager.tile_animations:
                    tile_scale = self.animation_manager.tile_animations[(q, r)].scale
                
                if tile_scale != 1.0:
                    scaled_corners = []
                    for cx, cy in corners:
                        dx = cx - screen_x
                        dy = cy - screen_y
                        scaled_corners.append((
                            screen_x + dx * tile_scale,
                            screen_y + dy * tile_scale
                        ))
                    corners = scaled_corners
                
                self._draw_tile_simple(screen_x, screen_y, corners, tile)
                
                self._draw_terrain_decoration(screen_x, screen_y, tile)
                
                if tile.building:
                    self.draw_building_icon(screen_x, screen_y, tile.building)
                
                if tile.unit:
                    unit_id = id(tile.unit)
                    if self.animation_manager and self.animation_manager.is_unit_animating(unit_id):
                        anim_pos = self.animation_manager.get_unit_position(unit_id, (screen_x, screen_y))
                        self.draw_unit_icon(anim_pos[0], anim_pos[1] + 5 * self.zoom_level, tile.unit)
                    else:
                        self.draw_unit_icon(screen_x, screen_y + 5 * self.zoom_level, tile.unit)
                
                if tile.builder_unit:
                    unit_id = id(tile.builder_unit)
                    if self.animation_manager and self.animation_manager.is_unit_animating(unit_id):
                        anim_pos = self.animation_manager.get_unit_position(unit_id, (screen_x, screen_y))
                        self.draw_unit_icon(anim_pos[0] - 6 * self.zoom_level, anim_pos[1] - 5 * self.zoom_level, tile.builder_unit)
                    else:
                        self.draw_unit_icon(screen_x - 6 * self.zoom_level, screen_y - 5 * self.zoom_level, tile.builder_unit)
        
        if self.animation_manager:
            self.animation_manager.particle_system.draw(self.screen)
        
        self.ui.set_mouse_state(self.mouse_pos, self.mouse_buttons_pressed.get(1, False))
        
        current_player = self.get_current_player()
        can_expand = self._can_expand_now(self.selected_tile, current_player)
        
        self.ui.draw_resource_panel(self.screen, current_player, self.turn)
        self.ui.draw_tile_info(self.screen, self.selected_tile)
        buttons = self.ui.draw_action_buttons(self.screen, self.selected_tile, current_player, can_expand)
        self.ui.draw_combat_log(self.screen, self.game_messages)
        
        turn_indicator = self.ui.font_large.render(
            f"{self.loc.t('current_player')}: {self.get_current_player().name}", 
            True, self.get_current_player().color
        )
        self.screen.blit(turn_indicator, (10, 10))
        
        self._draw_unit_selection_buttons(self.screen)
        
        if self.unit_detail_panel_visible and self.selected_unit:
            self._draw_unit_detail_panel(self.screen)
        
        if self.tile_detail_panel_visible and self.tile_detail_tile:
            self._draw_tile_detail_panel(self.screen)
        
        self._draw_popups()
    
    def _get_scaled_hex_corners(self, center_x: float, center_y: float) -> List[Tuple[float, float]]:
        corners = []
        scaled_hex_size = HEX_SIZE * self.zoom_level
        for i in range(6):
            angle = math.pi / 3 * i
            x = center_x + scaled_hex_size * math.cos(angle)
            y = center_y + scaled_hex_size * math.sin(angle)
            corners.append((x, y))
        return corners
    
    def _draw_tile_simple(self, screen_x: float, screen_y: float, corners: List[Tuple[float, float]], tile: HexTile):
        base_color = tile.get_color()
        
        scale = self.zoom_level
        shadow_offset = 2 * scale
        shadow_corners = [(cx + shadow_offset, cy + shadow_offset) for cx, cy in corners]
        
        shadow_color = (max(0, base_color[0] - 60), max(0, base_color[1] - 60), max(0, base_color[2] - 60))
        pygame.draw.polygon(self.screen, shadow_color, shadow_corners)
        
        highlight_corners = [(cx, cy - shadow_offset) for cx, cy in corners]
        highlight_color = (min(255, base_color[0] + 20), min(255, base_color[1] + 20), min(255, base_color[2] + 20))
        
        side_corners_right = [
            corners[0],
            corners[1],
            highlight_corners[1],
            highlight_corners[0]
        ]
        pygame.draw.polygon(self.screen, highlight_color, side_corners_right)
        
        side_corners_front = [
            corners[1],
            corners[2],
            highlight_corners[2],
            highlight_corners[1]
        ]
        pygame.draw.polygon(self.screen, base_color, side_corners_front)
        
        pygame.draw.polygon(self.screen, highlight_color, highlight_corners)
        
        pygame.draw.polygon(self.screen, tile.get_border_color(), highlight_corners, 1)
    
    def _draw_25d_town(self, x: float, y: float, owner_color: tuple, scale: float):
        detail_colors = BUILDING_DETAIL_COLORS.get('town', {})
        roof_color = detail_colors.get('roof', (200, 100, 80))
        wall_color = detail_colors.get('wall', (180, 160, 140))
        door_color = detail_colors.get('door', (100, 60, 40))
        window_color = detail_colors.get('window', (255, 255, 200))
        
        base_width = 18 * scale
        base_height = 10 * scale
        wall_height = 12 * scale
        
        base_shadow = (
            (x - base_width/2, y),
            (x + base_width/2, y),
            (x + base_width/2 + 2 * scale, y + 2 * scale),
            (x - base_width/2 + 2 * scale, y + 2 * scale)
        )
        pygame.draw.polygon(self.screen, (80, 70, 60), base_shadow)
        
        front_wall = (
            (x - base_width/2, y),
            (x + base_width/2, y),
            (x + base_width/2, y - wall_height),
            (x - base_width/2, y - wall_height)
        )
        pygame.draw.polygon(self.screen, wall_color, front_wall)
        pygame.draw.polygon(self.screen, (255, 255, 255), front_wall, 1)
        
        side_wall = (
            (x + base_width/2, y),
            (x + base_width/2 + 2 * scale, y + 2 * scale),
            (x + base_width/2 + 2 * scale, y - wall_height + 2 * scale),
            (x + base_width/2, y - wall_height)
        )
        pygame.draw.polygon(self.screen, (max(0, wall_color[0] - 30), max(0, wall_color[1] - 30), max(0, wall_color[2] - 30)), side_wall)
        
        roof_points = [
            (x, y - wall_height - 8 * scale),
            (x - base_width/2 - 3 * scale, y - wall_height),
            (x + base_width/2 + 3 * scale, y - wall_height)
        ]
        pygame.draw.polygon(self.screen, roof_color, roof_points)
        pygame.draw.polygon(self.screen, (255, 255, 255), roof_points, 1)
        
        door_rect = pygame.Rect(x - 3 * scale, y - 7 * scale, 6 * scale, 7 * scale)
        pygame.draw.rect(self.screen, door_color, door_rect)
        
        window_rect = pygame.Rect(x - 6 * scale, y - wall_height + 3 * scale, 4 * scale, 4 * scale)
        pygame.draw.rect(self.screen, window_color, window_rect)
        window_rect2 = pygame.Rect(x + 2 * scale, y - wall_height + 3 * scale, 4 * scale, 4 * scale)
        pygame.draw.rect(self.screen, window_color, window_rect2)
    
    def _draw_25d_barracks(self, x: float, y: float, owner_color: tuple, scale: float):
        detail_colors = BUILDING_DETAIL_COLORS.get('barracks', {})
        wall_color = detail_colors.get('wall', (120, 100, 80))
        roof_color = detail_colors.get('roof', (180, 120, 60))
        flag_color = detail_colors.get('flag', (200, 50, 50))
        pole_color = detail_colors.get('pole', (80, 60, 40))
        window_color = detail_colors.get('window', (255, 255, 200))
        
        base_width = 16 * scale
        wall_height = 14 * scale
        
        front_wall = (
            (x - base_width/2, y),
            (x + base_width/2, y),
            (x + base_width/2, y - wall_height),
            (x - base_width/2, y - wall_height)
        )
        pygame.draw.polygon(self.screen, wall_color, front_wall)
        pygame.draw.polygon(self.screen, (255, 255, 255), front_wall, 1)
        
        flag_x = x
        flag_top_y = y - wall_height - 6 * scale
        pygame.draw.line(self.screen, pole_color, (flag_x, y - wall_height), (flag_x, flag_top_y), int(2 * scale))
        
        flag_points = [
            (flag_x, flag_top_y),
            (flag_x + 8 * scale, flag_top_y + 4 * scale),
            (flag_x, flag_top_y + 8 * scale)
        ]
        pygame.draw.polygon(self.screen, flag_color, flag_points)
        pygame.draw.polygon(self.screen, (255, 255, 255), flag_points, 1)
        
        window_rect = pygame.Rect(x - 5 * scale, y - 5 * scale, 4 * scale, 4 * scale)
        pygame.draw.rect(self.screen, window_color, window_rect)
        window_rect2 = pygame.Rect(x + 1 * scale, y - 5 * scale, 4 * scale, 4 * scale)
        pygame.draw.rect(self.screen, window_color, window_rect2)
    
    def _draw_25d_farm(self, x: float, y: float, owner_color: tuple, scale: float):
        detail_colors = BUILDING_DETAIL_COLORS.get('farm', {})
        field_dark = detail_colors.get('field_dark', (60, 120, 40))
        field_light = detail_colors.get('field_light', (100, 160, 80))
        crop_color = detail_colors.get('crop', (255, 220, 50))
        barn_color = detail_colors.get('barn', (180, 140, 100))
        
        field_width = 16 * scale
        field_height = 8 * scale
        
        field_rect = pygame.Rect(x - field_width/2, y - field_height, field_width, field_height)
        pygame.draw.rect(self.screen, field_dark, field_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), field_rect, 1)
        
        for i in range(3):
            plant_x = x - 5 * scale + i * 5 * scale
            plant_y = y - field_height - 2 * scale
            pygame.draw.line(self.screen, field_light, (plant_x, plant_y + 2 * scale), (plant_x, plant_y - 3 * scale), int(1 * scale))
            pygame.draw.circle(self.screen, crop_color, (int(plant_x), int(plant_y - 4 * scale)), int(2 * scale))
        
        pygame.draw.rect(self.screen, barn_color, (x - 3 * scale, y - field_height - 8 * scale, 6 * scale, 6 * scale))
        pygame.draw.rect(self.screen, (255, 255, 255), (x - 3 * scale, y - field_height - 8 * scale, 6 * scale, 6 * scale), 1)
    
    def _draw_25d_tower(self, x: float, y: float, owner_color: tuple, scale: float):
        detail_colors = BUILDING_DETAIL_COLORS.get('tower', {})
        stone_dark = detail_colors.get('stone_dark', (100, 100, 100))
        stone_light = detail_colors.get('stone_light', (140, 140, 140))
        crenellation_color = detail_colors.get('crenellation', (80, 120, 200))
        window_color = detail_colors.get('window', (80, 80, 150))
        
        base_width = 10 * scale
        tower_height = 16 * scale
        
        tower_rect = pygame.Rect(x - base_width/2, y - tower_height, base_width, tower_height)
        pygame.draw.rect(self.screen, stone_dark, tower_rect)
        pygame.draw.rect(self.screen, stone_light, tower_rect, 1)
        
        top_width = 14 * scale
        top_height = 4 * scale
        top_rect = pygame.Rect(x - top_width/2, y - tower_height - top_height, top_width, top_height)
        pygame.draw.rect(self.screen, crenellation_color, top_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), top_rect, 1)
        
        for i in range(3):
            notch_x = x - top_width/2 + i * 6 * scale
            notch_rect = pygame.Rect(notch_x, y - tower_height - top_height - 3 * scale, 3 * scale, 3 * scale)
            pygame.draw.rect(self.screen, crenellation_color, notch_rect)
        
        window_rect = pygame.Rect(x - 2 * scale, y - 8 * scale, 4 * scale, 6 * scale)
        pygame.draw.rect(self.screen, window_color, window_rect)
    
    def _draw_25d_lumbermill(self, x: float, y: float, owner_color: tuple, scale: float):
        detail_colors = BUILDING_DETAIL_COLORS.get('lumbermill', {})
        wood_dark = detail_colors.get('wood_dark', (101, 67, 33))
        wood_light = detail_colors.get('wood_light', (139, 90, 43))
        roof_color = detail_colors.get('roof', (80, 50, 30))
        log_color = detail_colors.get('log', (101, 67, 33))
        
        base_width = 14 * scale
        wall_height = 10 * scale
        
        front_wall = (
            (x - base_width/2, y),
            (x + base_width/2, y),
            (x + base_width/2, y - wall_height),
            (x - base_width/2, y - wall_height)
        )
        pygame.draw.polygon(self.screen, wood_light, front_wall)
        pygame.draw.polygon(self.screen, (255, 255, 255), front_wall, 1)
        
        roof_points = [
            (x, y - wall_height - 6 * scale),
            (x - base_width/2 - 2 * scale, y - wall_height),
            (x + base_width/2 + 2 * scale, y - wall_height)
        ]
        pygame.draw.polygon(self.screen, roof_color, roof_points)
        pygame.draw.polygon(self.screen, (255, 255, 255), roof_points, 1)
        
        log_rect = pygame.Rect(x + 4 * scale, y - 6 * scale, 8 * scale, 3 * scale)
        pygame.draw.rect(self.screen, log_color, log_rect)
    
    def _draw_25d_default_building(self, x: float, y: float, owner_color: tuple, scale: float):
        base_width = 12 * scale
        wall_height = 8 * scale
        
        front_wall = (
            (x - base_width/2, y),
            (x + base_width/2, y),
            (x + base_width/2, y - wall_height),
            (x - base_width/2, y - wall_height)
        )
        pygame.draw.polygon(self.screen, owner_color, front_wall)
        pygame.draw.polygon(self.screen, (255, 255, 255), front_wall, 1)
        
        roof_points = [
            (x, y - wall_height - 5 * scale),
            (x - base_width/2 - 2 * scale, y - wall_height),
            (x + base_width/2 + 2 * scale, y - wall_height)
        ]
        pygame.draw.polygon(self.screen, (max(0, owner_color[0] - 30), max(0, owner_color[1] - 30), max(0, owner_color[2] - 30)), roof_points)
        pygame.draw.polygon(self.screen, (255, 255, 255), roof_points, 1)
    
    def _draw_25d_warrior(self, x: float, y: float, colors: dict, scale: float):
        armor_color = colors.get('armor', (80, 120, 200))
        helmet_color = colors.get('helmet', (100, 100, 120))
        sword_color = colors.get('sword', (200, 200, 200))
        hilt_color = colors.get('hilt', (180, 140, 80))
        
        body_width = 6 * scale
        body_height = 8 * scale
        
        body_rect = pygame.Rect(x - body_width/2, y - body_height, body_width, body_height)
        pygame.draw.rect(self.screen, armor_color, body_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), body_rect, 1)
        
        head_radius = 3 * scale
        pygame.draw.circle(self.screen, helmet_color, (int(x), int(y - body_height - head_radius)), int(head_radius))
        pygame.draw.circle(self.screen, (255, 255, 255), (int(x), int(y - body_height - head_radius)), int(head_radius), 1)
        
        sword_length = 8 * scale
        sword_x = x + 5 * scale
        sword_y = y - body_height + 2 * scale
        pygame.draw.line(self.screen, sword_color, (sword_x, sword_y), (sword_x, sword_y - sword_length), int(2 * scale))
        pygame.draw.rect(self.screen, hilt_color, (sword_x - 1 * scale, sword_y, 2 * scale, 2 * scale))
    
    def _draw_25d_archer(self, x: float, y: float, colors: dict, scale: float):
        body_color = colors.get('body', (100, 150, 100))
        hood_color = colors.get('hood', (80, 120, 80))
        bow_color = colors.get('bow', (139, 90, 43))
        arrow_color = colors.get('arrow', (200, 200, 200))
        
        body_width = 5 * scale
        body_height = 7 * scale
        
        body_rect = pygame.Rect(x - body_width/2, y - body_height, body_width, body_height)
        pygame.draw.rect(self.screen, body_color, body_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), body_rect, 1)
        
        head_radius = 3 * scale
        pygame.draw.circle(self.screen, hood_color, (int(x), int(y - body_height - head_radius)), int(head_radius))
        pygame.draw.circle(self.screen, (255, 255, 255), (int(x), int(y - body_height - head_radius)), int(head_radius), 1)
        
        bow_x = x + 6 * scale
        bow_y = y - body_height
        pygame.draw.arc(self.screen, bow_color, (bow_x - 3 * scale, bow_y - 6 * scale, 6 * scale, 12 * scale), -math.pi/2, math.pi/2, int(2 * scale))
        pygame.draw.line(self.screen, arrow_color, (bow_x, bow_y - 6 * scale), (bow_x, bow_y + 6 * scale), int(1 * scale))
    
    def _draw_25d_builder(self, x: float, y: float, colors: dict, scale: float):
        body_color = colors.get('body', (150, 120, 80))
        hat_color = colors.get('hat', (180, 140, 100))
        hammer_color = colors.get('hammer', (150, 150, 150))
        handle_color = colors.get('handle', (101, 67, 33))
        
        body_width = 5 * scale
        body_height = 7 * scale
        
        body_rect = pygame.Rect(x - body_width/2, y - body_height, body_width, body_height)
        pygame.draw.rect(self.screen, body_color, body_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), body_rect, 1)
        
        head_radius = 3 * scale
        pygame.draw.circle(self.screen, hat_color, (int(x), int(y - body_height - head_radius)), int(head_radius))
        pygame.draw.circle(self.screen, (255, 255, 255), (int(x), int(y - body_height - head_radius)), int(head_radius), 1)
        
        hammer_x = x + 5 * scale
        hammer_y = y - body_height + 2 * scale
        pygame.draw.line(self.screen, handle_color, (hammer_x, hammer_y), (hammer_x, hammer_y - 5 * scale), int(2 * scale))
        pygame.draw.rect(self.screen, hammer_color, (hammer_x - 2 * scale, hammer_y - 7 * scale, 4 * scale, 3 * scale))
    
    def _draw_25d_cavalry(self, x: float, y: float, colors: dict, scale: float):
        body_color = colors.get('body', (120, 80, 150))
        helmet_color = colors.get('helmet', (100, 80, 120))
        horse_color = colors.get('horse', (139, 90, 43))
        sword_color = colors.get('sword', (200, 200, 200))
        saddle_color = colors.get('saddle', (80, 60, 40))
        
        horse_body_width = 10 * scale
        horse_body_height = 6 * scale
        horse_leg_height = 6 * scale
        
        horse_rect = pygame.Rect(x - horse_body_width/2, y - horse_body_height - horse_leg_height, horse_body_width, horse_body_height)
        pygame.draw.rect(self.screen, horse_color, horse_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), horse_rect, 1)
        
        for i in range(4):
            leg_x = x - horse_body_width/2 + i * 3 * scale
            pygame.draw.line(self.screen, horse_color, (leg_x, y - horse_leg_height), (leg_x, y), int(2 * scale))
        
        head_x = x + horse_body_width/2 + 2 * scale
        head_y = y - horse_body_height - horse_leg_height
        pygame.draw.circle(self.screen, horse_color, (int(head_x), int(head_y)), int(3 * scale))
        pygame.draw.circle(self.screen, (255, 255, 255), (int(head_x), int(head_y)), int(3 * scale), 1)
        
        saddle_rect = pygame.Rect(x - 2 * scale, y - horse_body_height - horse_leg_height - 2 * scale, 4 * scale, 3 * scale)
        pygame.draw.rect(self.screen, saddle_color, saddle_rect)
        
        rider_body_width = 4 * scale
        rider_body_height = 5 * scale
        rider_rect = pygame.Rect(x - rider_body_width/2, y - horse_body_height - horse_leg_height - rider_body_height - 2 * scale, rider_body_width, rider_body_height)
        pygame.draw.rect(self.screen, body_color, rider_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), rider_rect, 1)
        
        rider_head_radius = 2 * scale
        pygame.draw.circle(self.screen, helmet_color, (int(x), int(y - horse_body_height - horse_leg_height - rider_body_height - 4 * scale)), int(rider_head_radius))
        pygame.draw.circle(self.screen, (255, 255, 255), (int(x), int(y - horse_body_height - horse_leg_height - rider_body_height - 4 * scale)), int(rider_head_radius), 1)
        
        sword_x = x + 5 * scale
        sword_y = y - horse_body_height - horse_leg_height - 3 * scale
        pygame.draw.line(self.screen, sword_color, (sword_x, sword_y), (sword_x, sword_y - 6 * scale), int(2 * scale))
    
    def _draw_25d_default_unit(self, x: float, y: float, colors: dict, scale: float):
        body_width = 5 * scale
        body_height = 7 * scale
        
        body_rect = pygame.Rect(x - body_width/2, y - body_height, body_width, body_height)
        pygame.draw.rect(self.screen, (150, 150, 150), body_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), body_rect, 1)
        
        head_radius = 3 * scale
        pygame.draw.circle(self.screen, (180, 180, 180), (int(x), int(y - body_height - head_radius)), int(head_radius))
        pygame.draw.circle(self.screen, (255, 255, 255), (int(x), int(y - body_height - head_radius)), int(head_radius), 1)
    
    def _draw_terrain_decoration(self, x: float, y: float, tile: HexTile):
        terrain = tile.terrain
        feature = tile.feature
        decoration_colors = TERRAIN_DECORATION_COLORS.get(terrain, {})
        scale = self.zoom_level
        
        if terrain == 'lake':
            wave_dark = decoration_colors.get('wave_dark', (20, 80, 130))
            wave_light = decoration_colors.get('wave_light', (60, 140, 200))
            foam = decoration_colors.get('foam', (200, 230, 250))
            
            pygame.draw.circle(self.screen, wave_dark, (int(x - 8 * scale), int(y + 2 * scale)), int(2 * scale))
            pygame.draw.circle(self.screen, wave_light, (int(x + 6 * scale), int(y - 4 * scale)), int(3 * scale))
            
            for i in range(3):
                offset_x = -8 * scale + i * 8 * scale
                pygame.draw.arc(self.screen, wave_light, 
                               (x + offset_x, y - 3 * scale, 10 * scale, 5 * scale),
                               0, math.pi, 1)
        
        elif terrain == 'mountain':
            decoration_colors = TERRAIN_DECORATION_COLORS.get('mountain', {})
            rock_dark = decoration_colors.get('rock_dark', (100, 90, 80))
            rock_light = decoration_colors.get('rock_light', (180, 170, 160))
            snow = decoration_colors.get('snow', (250, 250, 255))
            
            mountain_points = [
                (x, y - 15 * scale),
                (x - 12 * scale, y + 8 * scale),
                (x + 12 * scale, y + 8 * scale)
            ]
            pygame.draw.polygon(self.screen, rock_dark, mountain_points)
            pygame.draw.polygon(self.screen, rock_light, mountain_points, 1)
            
            snow_points = [
                (x, y - 15 * scale),
                (x - 6 * scale, y - 5 * scale),
                (x + 6 * scale, y - 5 * scale)
            ]
            pygame.draw.polygon(self.screen, snow, snow_points)
        
        elif terrain == 'plain':
            grass_dark = decoration_colors.get('grass_dark', (130, 160, 80))
            flower = decoration_colors.get('flower', (255, 220, 100))
            
            for i in range(2):
                gx = x + (-5 + i * 10) * scale
                pygame.draw.line(self.screen, grass_dark, 
                                (gx, y + 5 * scale), (gx, y - 3 * scale), int(1 * scale))
            
            pygame.draw.circle(self.screen, flower, (int(x + 8 * scale), int(y - 2 * scale)), int(2 * scale))
        
        elif terrain == 'hill':
            grass_dark = decoration_colors.get('grass_dark', (100, 130, 70))
            grass_medium = (
                min(255, grass_dark[0] + 15),
                min(255, grass_dark[1] + 15),
                min(255, grass_dark[2] + 15)
            )
            grass_light = (
                min(255, grass_dark[0] + 30),
                min(255, grass_dark[1] + 30),
                min(255, grass_dark[2] + 30)
            )
            rock = decoration_colors.get('rock', (120, 110, 100))
            rock_light = (
                min(255, rock[0] + 20),
                min(255, rock[1] + 20),
                min(255, rock[2] + 20)
            )
            
            main_hill = [
                (x, y - 10 * scale),
                (x - 12 * scale, y + 4 * scale),
                (x + 12 * scale, y + 4 * scale)
            ]
            pygame.draw.polygon(self.screen, grass_dark, main_hill)
            
            highlight = [
                (x, y - 10 * scale),
                (x - 3 * scale, y - 2 * scale),
                (x + 3 * scale, y - 2 * scale)
            ]
            pygame.draw.polygon(self.screen, grass_medium, highlight)
            
            peak_highlight = [
                (x, y - 10 * scale),
                (x - 1 * scale, y - 5 * scale),
                (x + 1 * scale, y - 5 * scale)
            ]
            pygame.draw.polygon(self.screen, grass_light, peak_highlight)
            
            rock_outcrop1 = [
                (x - 4 * scale, y),
                (x - 6 * scale, y + 3 * scale),
                (x - 2 * scale, y + 3 * scale)
            ]
            pygame.draw.polygon(self.screen, rock, rock_outcrop1)
            pygame.draw.polygon(self.screen, rock_light, rock_outcrop1, 1)
            
            rock_outcrop2 = [
                (x + 5 * scale, y + 1 * scale),
                (x + 3 * scale, y + 4 * scale),
                (x + 7 * scale, y + 4 * scale)
            ]
            pygame.draw.polygon(self.screen, rock, rock_outcrop2)
            pygame.draw.polygon(self.screen, rock_light, rock_outcrop2, 1)
            
            for i in range(3):
                grass_x = x + (-6 + i * 6) * scale
                pygame.draw.line(self.screen, grass_medium,
                                (grass_x, y + 2 * scale), (grass_x, y - 2 * scale), int(1 * scale))
            
            pygame.draw.polygon(self.screen, rock_light, main_hill, 1)
        
        if feature == 'river':
            self._draw_river_band(x, y, tile, scale)
        
        elif feature == 'forest':
            forest_colors = TERRAIN_DECORATION_COLORS.get('forest', {})
            tree_dark = forest_colors.get('tree_dark', (30, 80, 30))
            tree_light = forest_colors.get('tree_light', (70, 140, 70))
            trunk = forest_colors.get('trunk', (101, 67, 33))
            
            trunk_rect = pygame.Rect(x - 2 * scale, y + 3 * scale, 4 * scale, 6 * scale)
            pygame.draw.rect(self.screen, trunk, trunk_rect)
            
            foliage_y = y - 5 * scale
            pygame.draw.circle(self.screen, tree_dark, (int(x - 4 * scale), int(foliage_y)), int(6 * scale))
            pygame.draw.circle(self.screen, tree_light, (int(x + 2 * scale), int(foliage_y - 2 * scale)), int(5 * scale))
            pygame.draw.circle(self.screen, tree_dark, (int(x), int(foliage_y)), int(4 * scale))
    
    def _draw_river_polygon(self, curve_points, river_width, river_water, river_light, river_foam, scale):
        if len(curve_points) < 2:
            return
        
        def get_perpendicular(dx, dy):
            return -dy, dx
        
        upper_edge = []
        lower_edge = []
        
        for i, pt in enumerate(curve_points):
            if i < len(curve_points) - 1:
                next_pt = curve_points[i + 1]
                tangent_dx = next_pt[0] - pt[0]
                tangent_dy = next_pt[1] - pt[1]
                perp_dx, perp_dy = get_perpendicular(tangent_dx, tangent_dy)
                perp_len = math.sqrt(perp_dx * perp_dx + perp_dy * perp_dy)
                if perp_len > 0:
                    perp_dx /= perp_len
                    perp_dy /= perp_len
            else:
                prev_pt = curve_points[i - 1]
                tangent_dx = pt[0] - prev_pt[0]
                tangent_dy = pt[1] - prev_pt[1]
                perp_dx, perp_dy = get_perpendicular(tangent_dx, tangent_dy)
                perp_len = math.sqrt(perp_dx * perp_dx + perp_dy * perp_dy)
                if perp_len > 0:
                    perp_dx /= perp_len
                    perp_dy /= perp_len
            
            upper_edge.append((pt[0] + perp_dx * river_width / 2, pt[1] + perp_dy * river_width / 2))
            lower_edge.append((pt[0] - perp_dx * river_width / 2, pt[1] - perp_dy * river_width / 2))
        
        full_polygon = upper_edge + list(reversed(lower_edge))
        
        pygame.draw.polygon(self.screen, river_water, full_polygon)
        
        for i in range(len(upper_edge) - 1):
            pygame.draw.line(self.screen, river_light, upper_edge[i], upper_edge[i + 1], 1)
            pygame.draw.line(self.screen, river_light, lower_edge[i], lower_edge[i + 1], 1)
        
        if len(curve_points) >= 3:
            mid_idx = len(curve_points) // 2
            mid_x, mid_y = curve_points[mid_idx]
            pygame.draw.circle(self.screen, river_foam, (int(mid_x), int(mid_y)), int(2 * scale))
    
    def _draw_river_band(self, x: float, y: float, tile: HexTile, scale: float):
        river_water = RIVER_COLORS.get('water', (80, 160, 230))
        river_light = RIVER_COLORS.get('light_water', (120, 200, 255))
        river_foam = RIVER_COLORS.get('foam', (240, 250, 255))
        
        river_width = 8 * scale
        num_segments = 15
        scaled_hex_size = HEX_SIZE * self.zoom_level
        
        def get_edge_center_exact(center_x, center_y, direction, hex_size):
            angle = math.pi / 3 * direction
            edge_x = center_x + hex_size * math.cos(angle)
            edge_y = center_y + hex_size * math.sin(angle)
            return edge_x, edge_y
        
        if tile.river_from is not None and tile.river_to is not None:
            from_dir = tile.river_from
            to_dir = tile.river_to
            
            from_point = get_edge_center_exact(x, y, from_dir, scaled_hex_size)
            to_point = get_edge_center_exact(x, y, to_dir, scaled_hex_size)
            
            opposite_dir = (from_dir + 3) % 6
            is_straight = to_dir == opposite_dir
            
            curve_points = []
            
            if is_straight:
                from_dx, from_dy = HEX_DIRECTIONS[from_dir]
                to_dx, to_dy = HEX_DIRECTIONS[to_dir]
                
                cp1 = (from_point[0] - from_dx * scaled_hex_size * 0.2, 
                       from_point[1] - from_dy * scaled_hex_size * 0.2)
                cp2 = (to_point[0] - to_dx * scaled_hex_size * 0.2, 
                       to_point[1] - to_dy * scaled_hex_size * 0.2)
                
                for t in range(num_segments + 1):
                    t_val = t / num_segments
                    mt = 1 - t_val
                    pt_x = mt**3 * from_point[0] + 3 * mt**2 * t_val * cp1[0] + 3 * mt * t_val**2 * cp2[0] + t_val**3 * to_point[0]
                    pt_y = mt**3 * from_point[1] + 3 * mt**2 * t_val * cp1[1] + 3 * mt * t_val**2 * cp2[1] + t_val**3 * to_point[1]
                    curve_points.append((pt_x, pt_y))
            else:
                from_dx, from_dy = HEX_DIRECTIONS[from_dir]
                to_dx, to_dy = HEX_DIRECTIONS[to_dir]
                
                in_tangent_len = scaled_hex_size * 0.4
                out_tangent_len = scaled_hex_size * 0.4
                
                cp1 = (from_point[0] - from_dx * in_tangent_len, 
                       from_point[1] - from_dy * in_tangent_len)
                cp2 = (to_point[0] - to_dx * out_tangent_len, 
                       to_point[1] - to_dy * out_tangent_len)
                
                for t in range(num_segments + 1):
                    t_val = t / num_segments
                    mt = 1 - t_val
                    pt_x = mt**3 * from_point[0] + 3 * mt**2 * t_val * cp1[0] + 3 * mt * t_val**2 * cp2[0] + t_val**3 * to_point[0]
                    pt_y = mt**3 * from_point[1] + 3 * mt**2 * t_val * cp1[1] + 3 * mt * t_val**2 * cp2[1] + t_val**3 * to_point[1]
                    curve_points.append((pt_x, pt_y))
            
            self._draw_river_polygon(curve_points, river_width, river_water, river_light, river_foam, scale)
        
        elif tile.river_from is not None:
            from_dir = tile.river_from
            from_point = get_edge_center_exact(x, y, from_dir, scaled_hex_size)
            center_point = (x, y)
            
            curve_points = []
            for t in range(num_segments + 1):
                t_val = t / num_segments
                pt_x = from_point[0] + (center_point[0] - from_point[0]) * t_val
                pt_y = from_point[1] + (center_point[1] - from_point[1]) * t_val
                curve_points.append((pt_x, pt_y))
            
            self._draw_river_polygon(curve_points, river_width, river_water, river_light, river_foam, scale)
            
            pygame.draw.circle(self.screen, river_water, (int(x), int(y)), int(river_width / 2))
            pygame.draw.circle(self.screen, river_light, (int(x), int(y)), int(river_width / 2), 1)
        
        elif tile.river_to is not None:
            to_dir = tile.river_to
            to_point = get_edge_center_exact(x, y, to_dir, scaled_hex_size)
            center_point = (x, y)
            
            curve_points = []
            for t in range(num_segments + 1):
                t_val = t / num_segments
                pt_x = center_point[0] + (to_point[0] - center_point[0]) * t_val
                pt_y = center_point[1] + (to_point[1] - center_point[1]) * t_val
                curve_points.append((pt_x, pt_y))
            
            self._draw_river_polygon(curve_points, river_width, river_water, river_light, river_foam, scale)
            
            pygame.draw.circle(self.screen, river_water, (int(x), int(y)), int(river_width / 2))
            pygame.draw.circle(self.screen, river_light, (int(x), int(y)), int(river_width / 2), 1)
        
        else:
            pygame.draw.circle(self.screen, river_water, (int(x), int(y)), int(river_width / 2))
            pygame.draw.circle(self.screen, river_light, (int(x), int(y)), int(river_width / 2), 1)
    
    def _handle_edge_scroll(self):
        if self.game_state != GAME_STATES['PLAYING']:
            return
        
        mouse_x, mouse_y = self.mouse_pos
        
        if mouse_x < self.edge_threshold:
            self.map_offset_x += self.scroll_speed
        elif mouse_x > SCREEN_WIDTH - self.edge_threshold:
            self.map_offset_x -= self.scroll_speed
        
        if mouse_y < self.edge_threshold:
            self.map_offset_y += self.scroll_speed
        elif mouse_y > SCREEN_HEIGHT - self.edge_threshold:
            self.map_offset_y -= self.scroll_speed
        
        self._clamp_map_offset()
    
    def _draw_unit_detail_panel(self, screen: pygame.Surface):
        if not self.selected_unit:
            return
        
        unit = self.selected_unit
        panel_rect = self.unit_detail_panel_rect
        
        pygame.draw.rect(screen, UI_PANEL_COLOR, panel_rect)
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, panel_rect, 2)
        
        y_offset = panel_rect.y + 10
        x_offset = panel_rect.x + 15
        
        unit_name = self.loc.get_unit_name(unit.unit_type)
        title = self.ui.font_large.render(unit_name, True, unit.owner.color)
        screen.blit(title, (x_offset, y_offset))
        y_offset += 30
        
        owner_text = self.ui.font_medium.render(f"{self.loc.t('owner')}: {unit.owner.name}", True, TEXT_COLOR)
        screen.blit(owner_text, (x_offset, y_offset))
        y_offset += 25
        
        hp_text = self.ui.font_medium.render(
            f"{self.loc.t('health')}: {unit.health}/{unit.max_health}", 
            True, TEXT_COLOR
        )
        screen.blit(hp_text, (x_offset, y_offset))
        
        hp_bar_width = 100
        hp_bar_height = 8
        hp_x = x_offset
        hp_y = y_offset + 20
        hp_percent = unit.health / unit.max_health
        
        pygame.draw.rect(screen, (80, 80, 80), (hp_x, hp_y, hp_bar_width, hp_bar_height))
        hp_color = (100, 255, 100) if hp_percent > 0.5 else (255, 200, 50) if hp_percent > 0.25 else (255, 80, 80)
        pygame.draw.rect(screen, hp_color, (hp_x, hp_y, hp_bar_width * hp_percent, hp_bar_height))
        pygame.draw.rect(screen, (200, 200, 200), (hp_x, hp_y, hp_bar_width, hp_bar_height), 1)
        
        y_offset += 35
        
        stats = [
            (self.loc.t('attack'), unit.attack),
            (self.loc.t('defense'), unit.defense),
            (self.loc.t('movement'), unit.movement),
        ]
        
        for stat_name, stat_value in stats:
            stat_text = self.ui.font_medium.render(f"{stat_name}: {stat_value}", True, TEXT_COLOR)
            screen.blit(stat_text, (x_offset, y_offset))
            y_offset += 25
        
        y_offset += 5
        status_text = self.ui.font_small.render(self.loc.t('status') + ":", True, TEXT_COLOR)
        screen.blit(status_text, (x_offset, y_offset))
        y_offset += 20
        
        if unit.moved_this_turn:
            moved_text = self.ui.font_small.render(f"  - {self.loc.t('moved')}", True, (150, 150, 150))
        else:
            moved_text = self.ui.font_small.render(f"  - {self.loc.t('can_move')}", True, (100, 255, 100))
        screen.blit(moved_text, (x_offset, y_offset))
        y_offset += 18
        
        if unit.attacked_this_turn:
            attack_text = self.ui.font_small.render(f"  - {self.loc.t('attacked')}", True, (150, 150, 150))
        else:
            attack_text = self.ui.font_small.render(f"  - {self.loc.t('can_attack')}", True, (100, 255, 100))
        screen.blit(attack_text, (x_offset, y_offset))
        y_offset += 18
        
        if unit.can_build:
            build_text = self.ui.font_small.render(f"  - {self.loc.t('can_build')}", True, (100, 200, 255))
            screen.blit(build_text, (x_offset, y_offset))
        
        close_button_rect = pygame.Rect(
            panel_rect.right - 30, panel_rect.y + 5, 25, 25
        )
        pygame.draw.rect(screen, (200, 80, 80), close_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), close_button_rect, 1)
        
        close_text = self.ui.font_small.render("X", True, (255, 255, 255))
        text_rect = close_text.get_rect(center=close_button_rect.center)
        screen.blit(close_text, text_rect)
        
        self.unit_detail_close_button = close_button_rect
    
    def _draw_tile_detail_panel(self, screen: pygame.Surface):
        if not self.tile_detail_tile:
            return
        
        tile = self.tile_detail_tile
        panel_rect = self.tile_detail_panel_rect
        
        pygame.draw.rect(screen, UI_PANEL_COLOR, panel_rect)
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, panel_rect, 2)
        
        y_offset = panel_rect.y + 10
        x_offset = panel_rect.x + 15
        
        title = self.ui.font_large.render(self.loc.t('tile_info'), True, HIGHLIGHT_COLOR)
        screen.blit(title, (x_offset, y_offset))
        y_offset += 30
        
        coords_text = self.ui.font_medium.render(
            f"{self.loc.t('coordinates')}: ({tile.q}, {tile.r})", 
            True, TEXT_COLOR
        )
        screen.blit(coords_text, (x_offset, y_offset))
        y_offset += 25
        
        terrain_name = self.loc.get_terrain_name(tile.terrain)
        terrain_text = self.ui.font_medium.render(
            f"{self.loc.t('terrain')}: {terrain_name}", 
            True, TERRAIN_COLORS.get(tile.terrain, TEXT_COLOR)
        )
        screen.blit(terrain_text, (x_offset, y_offset))
        y_offset += 25
        
        terrain_info = TERRAIN_TYPES.get(tile.terrain, {})
        passable_text = self.ui.font_small.render(
            f"  {self.loc.t('passable')}: {self.loc.t('yes') if terrain_info.get('passable', True) else self.loc.t('no')}", 
            True, TEXT_COLOR
        )
        screen.blit(passable_text, (x_offset, y_offset))
        y_offset += 20
        
        defense_text = self.ui.font_small.render(
            f"  {self.loc.t('defense_bonus')}: +{terrain_info.get('defense_bonus', 0)}", 
            True, TEXT_COLOR
        )
        screen.blit(defense_text, (x_offset, y_offset))
        y_offset += 25
        
        feature_name = self.loc.get_feature_name(tile.feature)
        feature_text = self.ui.font_medium.render(
            f"{self.loc.t('feature')}: {feature_name}", 
            True, TEXT_COLOR
        )
        screen.blit(feature_text, (x_offset, y_offset))
        y_offset += 25
        
        if tile.feature == 'river':
            river_info_text = ""
            if tile.river_from is not None and tile.river_to is not None:
                river_info_text = self.loc.t('river_through')
            elif tile.river_from is not None:
                river_info_text = self.loc.t('river_end')
            elif tile.river_to is not None:
                river_info_text = self.loc.t('river_start')
            
            if river_info_text:
                info_text = self.ui.font_small.render(f"  {river_info_text}", True, TEXT_COLOR)
                screen.blit(info_text, (x_offset, y_offset))
                y_offset += 20
        
        y_offset += 5
        owner_title = self.ui.font_medium.render(f"{self.loc.t('owner')}:", True, TEXT_COLOR)
        screen.blit(owner_title, (x_offset, y_offset))
        y_offset += 25
        
        if tile.owner:
            owner_text = self.ui.font_small.render(f"  {tile.owner.name}", True, tile.owner.color)
            screen.blit(owner_text, (x_offset, y_offset))
            y_offset += 20
            
            tiles_text = self.ui.font_small.render(
                f"  {self.loc.t('tiles_owned')}: {tile.owner.tiles_owned}", 
                True, TEXT_COLOR
            )
            screen.blit(tiles_text, (x_offset, y_offset))
        else:
            owner_text = self.ui.font_small.render(f"  {self.loc.t('neutral')}", True, (150, 150, 150))
            screen.blit(owner_text, (x_offset, y_offset))
        
        y_offset += 25
        if tile.building:
            building_name = self.loc.get_building_name(tile.building.building_type)
            building_text = self.ui.font_medium.render(
                f"{self.loc.t('building')}: {building_name}", 
                True, tile.building.owner.color
            )
            screen.blit(building_text, (x_offset, y_offset))
        
        close_button_rect = pygame.Rect(
            panel_rect.right - 30, panel_rect.y + 5, 25, 25
        )
        pygame.draw.rect(screen, (200, 80, 80), close_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), close_button_rect, 1)
        
        close_text = self.ui.font_small.render("X", True, (255, 255, 255))
        text_rect = close_text.get_rect(center=close_button_rect.center)
        screen.blit(close_text, text_rect)
        
        self.tile_detail_close_button = close_button_rect
    
    def draw_building_icon(self, x: float, y: float, building: Building):
        color = building.owner.color
        building_type = building.building_type
        
        if building_type == 'town':
            self._draw_town_icon(x, y, color)
        elif building_type == 'barracks':
            self._draw_barracks_icon(x, y, color)
        elif building_type == 'farm':
            self._draw_farm_icon(x, y, color)
        elif building_type == 'tower':
            self._draw_tower_icon(x, y, color)
        elif building_type == 'lumbermill':
            self._draw_lumbermill_icon(x, y, color)
        else:
            self._draw_default_building_icon(x, y, color)
    
    def _draw_town_icon(self, x: float, y: float, color: tuple):
        scale = self.zoom_level
        detail_colors = BUILDING_DETAIL_COLORS.get('town', {})
        
        roof_color = detail_colors.get('roof', (200, 100, 80))
        wall_color = detail_colors.get('wall', (180, 160, 140))
        door_color = detail_colors.get('door', (100, 60, 40))
        window_color = detail_colors.get('window', (255, 255, 200))
        
        base_y = y - 5 * scale
        base_width = 20 * scale
        base_height = 12 * scale
        roof_height = 8 * scale
        
        base_rect = pygame.Rect(x - base_width//2, base_y - base_height//2 + roof_height, base_width, base_height)
        pygame.draw.rect(self.screen, wall_color, base_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), base_rect, 1)
        
        roof_points = [
            (x, base_y - base_height//2 - roof_height + 2 * scale),
            (x - base_width//2 - 2 * scale, base_y - base_height//2 + roof_height),
            (x + base_width//2 + 2 * scale, base_y - base_height//2 + roof_height)
        ]
        pygame.draw.polygon(self.screen, roof_color, roof_points)
        pygame.draw.polygon(self.screen, (255, 255, 255), roof_points, 1)
        
        window_rect = pygame.Rect(x - 6 * scale, base_y - base_height//2 + roof_height + 2 * scale, 4 * scale, 4 * scale)
        pygame.draw.rect(self.screen, window_color, window_rect)
        
        window_rect2 = pygame.Rect(x + 2 * scale, base_y - base_height//2 + roof_height + 2 * scale, 4 * scale, 4 * scale)
        pygame.draw.rect(self.screen, window_color, window_rect2)
        
        door_rect = pygame.Rect(x - 3 * scale, base_y - base_height//2 + roof_height + 5 * scale, 6 * scale, 7 * scale)
        pygame.draw.rect(self.screen, door_color, door_rect)
    
    def _draw_barracks_icon(self, x: float, y: float, color: tuple):
        scale = self.zoom_level
        detail_colors = BUILDING_DETAIL_COLORS.get('barracks', {})
        
        wall_color = detail_colors.get('wall', (120, 100, 80))
        roof_color = detail_colors.get('roof', (180, 120, 60))
        flag_color = detail_colors.get('flag', (200, 50, 50))
        pole_color = detail_colors.get('pole', (80, 60, 40))
        window_color = detail_colors.get('window', (255, 255, 200))
        
        base_y = y - 5 * scale
        base_width = 18 * scale
        base_height = 14 * scale
        
        base_rect = pygame.Rect(x - base_width//2, base_y - base_height//2, base_width, base_height)
        pygame.draw.rect(self.screen, wall_color, base_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), base_rect, 1)
        
        flag_x = x
        flag_top_y = base_y - base_height//2 - 6 * scale
        pygame.draw.line(self.screen, pole_color, (flag_x, base_y - base_height//2), (flag_x, flag_top_y), int(2 * scale))
        
        flag_points = [
            (flag_x, flag_top_y),
            (flag_x + 8 * scale, flag_top_y + 4 * scale),
            (flag_x, flag_top_y + 8 * scale)
        ]
        pygame.draw.polygon(self.screen, flag_color, flag_points)
        pygame.draw.polygon(self.screen, (255, 255, 255), flag_points, 1)
        
        window_rect = pygame.Rect(x - 5 * scale, base_y - 3 * scale, 4 * scale, 4 * scale)
        pygame.draw.rect(self.screen, window_color, window_rect)
        window_rect2 = pygame.Rect(x + 1 * scale, base_y - 3 * scale, 4 * scale, 4 * scale)
        pygame.draw.rect(self.screen, window_color, window_rect2)
    
    def _draw_farm_icon(self, x: float, y: float, color: tuple):
        scale = self.zoom_level
        detail_colors = BUILDING_DETAIL_COLORS.get('farm', {})
        
        field_dark = detail_colors.get('field_dark', (60, 120, 40))
        field_light = detail_colors.get('field_light', (100, 160, 80))
        crop_color = detail_colors.get('crop', (255, 220, 50))
        barn_color = detail_colors.get('barn', (180, 140, 100))
        
        base_y = y - 5 * scale
        field_width = 18 * scale
        field_height = 8 * scale
        
        field_rect = pygame.Rect(x - field_width//2, base_y, field_width, field_height)
        pygame.draw.rect(self.screen, field_dark, field_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), field_rect, 1)
        
        for i in range(3):
            plant_x = x - 5 * scale + i * 5 * scale
            plant_y = base_y - 2 * scale
            pygame.draw.line(self.screen, field_light, (plant_x, plant_y + 2 * scale), (plant_x, plant_y - 3 * scale), int(1 * scale))
            pygame.draw.circle(self.screen, crop_color, (int(plant_x), int(plant_y - 4 * scale)), int(2 * scale))
        
        pygame.draw.rect(self.screen, barn_color, (x - 3 * scale, base_y - 8 * scale, 6 * scale, 6 * scale))
        pygame.draw.rect(self.screen, (255, 255, 255), (x - 3 * scale, base_y - 8 * scale, 6 * scale, 6 * scale), 1)
    
    def _draw_tower_icon(self, x: float, y: float, color: tuple):
        scale = self.zoom_level
        detail_colors = BUILDING_DETAIL_COLORS.get('tower', {})
        
        stone_dark = detail_colors.get('stone_dark', (100, 100, 100))
        stone_light = detail_colors.get('stone_light', (140, 140, 140))
        crenellation_color = detail_colors.get('crenellation', (80, 120, 200))
        window_color = detail_colors.get('window', (80, 80, 150))
        
        base_y = y - 5 * scale
        base_width = 12 * scale
        base_height = 16 * scale
        
        base_rect = pygame.Rect(x - base_width//2, base_y - base_height//2, base_width, base_height)
        pygame.draw.rect(self.screen, stone_dark, base_rect)
        pygame.draw.rect(self.screen, stone_light, base_rect, 1)
        
        top_width = 16 * scale
        top_height = 4 * scale
        top_rect = pygame.Rect(x - top_width//2, base_y - base_height//2 - top_height, top_width, top_height)
        pygame.draw.rect(self.screen, crenellation_color, top_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), top_rect, 1)
        
        for i in range(3):
            notch_x = x - top_width//2 + i * 8 * scale
            notch_rect = pygame.Rect(notch_x, base_y - base_height//2 - top_height - 3 * scale, 4 * scale, 3 * scale)
            pygame.draw.rect(self.screen, crenellation_color, notch_rect)
        
        window_rect = pygame.Rect(x - 2 * scale, base_y - 2 * scale, 4 * scale, 6 * scale)
        pygame.draw.rect(self.screen, window_color, window_rect)
    
    def _draw_lumbermill_icon(self, x: float, y: float, color: tuple):
        scale = self.zoom_level
        detail_colors = BUILDING_DETAIL_COLORS.get('lumbermill', {})
        
        wood_dark = detail_colors.get('wood_dark', (101, 67, 33))
        wood_light = detail_colors.get('wood_light', (139, 90, 43))
        roof_color = detail_colors.get('roof', (80, 50, 30))
        log_color = detail_colors.get('log', (101, 67, 33))
        
        base_y = y - 5 * scale
        base_width = 16 * scale
        base_height = 10 * scale
        
        base_rect = pygame.Rect(x - base_width//2, base_y - base_height//2, base_width, base_height)
        pygame.draw.rect(self.screen, wood_light, base_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), base_rect, 1)
        
        roof_points = [
            (x, base_y - base_height//2 - 6 * scale),
            (x - base_width//2 - 2 * scale, base_y - base_height//2),
            (x + base_width//2 + 2 * scale, base_y - base_height//2)
        ]
        pygame.draw.polygon(self.screen, roof_color, roof_points)
        pygame.draw.polygon(self.screen, (255, 255, 255), roof_points, 1)
        
        log_y = base_y + base_height//2 + 2 * scale
        pygame.draw.ellipse(self.screen, log_color, (x - 8 * scale, log_y, 16 * scale, 4 * scale))
        pygame.draw.ellipse(self.screen, (255, 255, 255), (x - 8 * scale, log_y, 16 * scale, 4 * scale), 1)
        
        pygame.draw.rect(self.screen, wood_dark, (x - 2 * scale, base_y - 3 * scale, 4 * scale, 4 * scale))
    
    def _draw_default_building_icon(self, x: float, y: float, color: tuple):
        icon_size = 16
        icon_rect = pygame.Rect(x - icon_size//2, y - icon_size//2 - 5, icon_size, icon_size)
        pygame.draw.rect(self.screen, color, icon_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), icon_rect, 1)
        
        text = self.ui.font_small.render("?", True, (255, 255, 255))
        text_rect = text.get_rect(center=icon_rect.center)
        self.screen.blit(text, text_rect)
    
    def draw_unit_icon(self, x: float, y: float, unit: Unit):
        color = unit.owner.color
        unit_type = unit.unit_type
        
        if unit_type == 'warrior':
            self._draw_warrior_icon(x, y, color, unit)
        elif unit_type == 'archer':
            self._draw_archer_icon(x, y, color, unit)
        elif unit_type == 'builder':
            self._draw_builder_icon(x, y, color, unit)
        elif unit_type == 'cavalry':
            self._draw_cavalry_icon(x, y, color, unit)
        else:
            self._draw_default_unit_icon(x, y, color, unit)
    
    def _draw_warrior_icon(self, x: float, y: float, color: tuple, unit: Unit):
        scale = self.zoom_level
        detail_colors = UNIT_DETAIL_COLORS.get('warrior', {})
        
        armor_color = detail_colors.get('armor', (80, 120, 200))
        helmet_color = detail_colors.get('helmet', (100, 100, 120))
        sword_color = detail_colors.get('sword', (200, 200, 200))
        hilt_color = detail_colors.get('hilt', (180, 140, 80))
        
        base_y = y + 12 * scale
        
        pygame.draw.circle(self.screen, helmet_color, (int(x), int(base_y - 4 * scale)), int(5 * scale))
        pygame.draw.circle(self.screen, (255, 255, 255), (int(x), int(base_y - 4 * scale)), int(5 * scale), 1)
        
        pygame.draw.circle(self.screen, (200, 200, 220), (int(x), int(base_y - 6 * scale)), int(2 * scale))
        
        body_rect = pygame.Rect(x - 4 * scale, base_y, 8 * scale, 8 * scale)
        pygame.draw.rect(self.screen, armor_color, body_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), body_rect, 1)
        
        shield_rect = pygame.Rect(x - 8 * scale, base_y + 2 * scale, 4 * scale, 6 * scale)
        pygame.draw.rect(self.screen, (150, 120, 80), shield_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), shield_rect, 1)
        
        sword_x = x + 6 * scale
        pygame.draw.line(self.screen, sword_color, (sword_x, base_y - 2 * scale), (sword_x, base_y + 6 * scale), int(2 * scale))
        pygame.draw.line(self.screen, hilt_color, (sword_x - 2 * scale, base_y - 2 * scale), (sword_x + 2 * scale, base_y - 2 * scale), int(3 * scale))
        
        self._draw_health_bar(x, y, unit)
    
    def _draw_archer_icon(self, x: float, y: float, color: tuple, unit: Unit):
        scale = self.zoom_level
        detail_colors = UNIT_DETAIL_COLORS.get('archer', {})
        
        body_color = detail_colors.get('body', (100, 150, 100))
        hood_color = detail_colors.get('hood', (80, 120, 80))
        bow_color = detail_colors.get('bow', (139, 90, 43))
        arrow_color = detail_colors.get('arrow', (200, 200, 200))
        
        base_y = y + 12 * scale
        
        pygame.draw.circle(self.screen, hood_color, (int(x), int(base_y - 4 * scale)), int(6 * scale))
        pygame.draw.circle(self.screen, (255, 255, 255), (int(x), int(base_y - 4 * scale)), int(6 * scale), 1)
        
        pygame.draw.polygon(self.screen, hood_color, [
            (x, base_y - 10 * scale),
            (x - 5 * scale, base_y - 4 * scale),
            (x + 5 * scale, base_y - 4 * scale)
        ])
        
        body_rect = pygame.Rect(x - 4 * scale, base_y, 8 * scale, 8 * scale)
        pygame.draw.rect(self.screen, body_color, body_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), body_rect, 1)
        
        quiver_rect = pygame.Rect(x - 7 * scale, base_y - 2 * scale, 3 * scale, 10 * scale)
        pygame.draw.rect(self.screen, (101, 67, 33), quiver_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), quiver_rect, 1)
        
        bow_x = x + 7 * scale
        pygame.draw.arc(self.screen, bow_color, 
                       (bow_x - 4 * scale, base_y - 6 * scale, 8 * scale, 14 * scale),
                       -math.pi/2, math.pi/2, int(2 * scale))
        pygame.draw.line(self.screen, arrow_color, 
                        (bow_x, base_y - 6 * scale), (bow_x, base_y + 8 * scale), int(1 * scale))
        
        self._draw_health_bar(x, y, unit)
    
    def _draw_builder_icon(self, x: float, y: float, color: tuple, unit: Unit):
        scale = self.zoom_level
        detail_colors = UNIT_DETAIL_COLORS.get('builder', {})
        
        body_color = detail_colors.get('body', (150, 120, 80))
        hat_color = detail_colors.get('hat', (180, 140, 100))
        hammer_color = detail_colors.get('hammer', (150, 150, 150))
        handle_color = detail_colors.get('handle', (101, 67, 33))
        
        base_y = y + 12 * scale
        
        pygame.draw.circle(self.screen, hat_color, (int(x), int(base_y - 4 * scale)), int(5 * scale))
        pygame.draw.circle(self.screen, (255, 255, 255), (int(x), int(base_y - 4 * scale)), int(5 * scale), 1)
        
        pygame.draw.polygon(self.screen, hat_color, [
            (x, base_y - 10 * scale),
            (x - 6 * scale, base_y - 2 * scale),
            (x + 6 * scale, base_y - 2 * scale)
        ])
        
        body_rect = pygame.Rect(x - 4 * scale, base_y, 8 * scale, 8 * scale)
        pygame.draw.rect(self.screen, body_color, body_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), body_rect, 1)
        
        toolbelt_rect = pygame.Rect(x - 5 * scale, base_y + 5 * scale, 10 * scale, 2 * scale)
        pygame.draw.rect(self.screen, (101, 67, 33), toolbelt_rect)
        
        hammer_x = x + 6 * scale
        pygame.draw.line(self.screen, handle_color, (hammer_x, base_y - 4 * scale), (hammer_x, base_y + 6 * scale), int(2 * scale))
        pygame.draw.rect(self.screen, hammer_color, (hammer_x - 3 * scale, base_y - 6 * scale, 6 * scale, 4 * scale))
        
        if unit.can_build:
            pygame.draw.circle(self.screen, (100, 255, 100), (int(x + 8 * scale), int(base_y - 6 * scale)), int(3 * scale))
            pygame.draw.circle(self.screen, (255, 255, 255), (int(x + 8 * scale), int(base_y - 6 * scale)), int(3 * scale), 1)
        
        self._draw_health_bar(x, y, unit)
    
    def _draw_cavalry_icon(self, x: float, y: float, color: tuple, unit: Unit):
        scale = self.zoom_level
        detail_colors = UNIT_DETAIL_COLORS.get('cavalry', {})
        
        body_color = detail_colors.get('body', (120, 80, 150))
        helmet_color = detail_colors.get('helmet', (100, 80, 120))
        horse_color = detail_colors.get('horse', (139, 90, 43))
        sword_color = detail_colors.get('sword', (200, 200, 200))
        saddle_color = detail_colors.get('saddle', (80, 60, 40))
        
        base_y = y + 12 * scale
        
        pygame.draw.ellipse(self.screen, horse_color, (x - 8 * scale, base_y - 2 * scale, 16 * scale, 8 * scale))
        pygame.draw.ellipse(self.screen, (255, 255, 255), (x - 8 * scale, base_y - 2 * scale, 16 * scale, 8 * scale), 1)
        
        pygame.draw.circle(self.screen, horse_color, (int(x - 6 * scale), int(base_y - 6 * scale)), int(4 * scale))
        pygame.draw.circle(self.screen, (255, 255, 255), (int(x - 6 * scale), int(base_y - 6 * scale)), int(4 * scale), 1)
        
        pygame.draw.rect(self.screen, saddle_color, (x - 3 * scale, base_y - 3 * scale, 6 * scale, 3 * scale))
        
        pygame.draw.rect(self.screen, body_color, (x - 2 * scale, base_y - 10 * scale, 4 * scale, 7 * scale))
        pygame.draw.rect(self.screen, (255, 255, 255), (x - 2 * scale, base_y - 10 * scale, 4 * scale, 7 * scale), 1)
        
        pygame.draw.circle(self.screen, helmet_color, (int(x), int(base_y - 13 * scale)), int(3 * scale))
        pygame.draw.circle(self.screen, (255, 255, 255), (int(x), int(base_y - 13 * scale)), int(3 * scale), 1)
        
        sword_x = x + 5 * scale
        pygame.draw.line(self.screen, sword_color, (sword_x, base_y - 8 * scale), (sword_x, base_y), int(1 * scale))
        
        self._draw_health_bar(x, y, unit)
    
    def _draw_default_unit_icon(self, x: float, y: float, color: tuple, unit: Unit):
        scale = self.zoom_level
        icon_size = 14 * scale
        pygame.draw.circle(self.screen, color, (int(x), int(y + 15 * scale)), int(icon_size//2))
        pygame.draw.circle(self.screen, (255, 255, 255), (int(x), int(y + 15 * scale)), int(icon_size//2), 1)
        self._draw_health_bar(x, y, unit)
    
    def _draw_health_bar(self, x: float, y: float, unit: Unit):
        scale = self.zoom_level
        hp_percent = unit.health / unit.max_health
        hp_bar_width = 18 * scale
        hp_bar_height = 3 * scale
        hp_x = x - hp_bar_width//2
        hp_y = y + 22 * scale
        
        pygame.draw.rect(self.screen, (80, 80, 80), (hp_x, hp_y, hp_bar_width, hp_bar_height))
        hp_color = (100, 255, 100) if hp_percent > 0.5 else (255, 200, 50) if hp_percent > 0.25 else (255, 80, 80)
        pygame.draw.rect(self.screen, hp_color, (hp_x, hp_y, hp_bar_width * hp_percent, hp_bar_height))
    
    def _handle_zoom(self, scroll_amount: int, mouse_pos: Tuple[int, int]):
        old_zoom = self.zoom_level
        
        if scroll_amount > 0:
            self.zoom_level = min(self.zoom_level + self.zoom_step, self.max_zoom)
        else:
            self.zoom_level = max(self.zoom_level - self.zoom_step, self.min_zoom)
        
        if old_zoom != self.zoom_level:
            mouse_x, mouse_y = mouse_pos
            old_offset_x = mouse_x - self.map_offset_x
            old_offset_y = mouse_y - self.map_offset_y
            
            new_offset_x = old_offset_x * (self.zoom_level / old_zoom)
            new_offset_y = old_offset_y * (self.zoom_level / old_zoom)
            
            self.map_offset_x = mouse_x - new_offset_x
            self.map_offset_y = mouse_y - new_offset_y
    
    def _get_map_bounds(self):
        if not self.hex_map:
            return 0, 0, 0, 0
        
        map_width = HEX_SIZE * 3/2 * self.hex_map.cols
        map_height = HEX_SIZE * math.sqrt(3) * (self.hex_map.rows + 0.5)
        
        scaled_width = map_width * self.zoom_level
        scaled_height = map_height * self.zoom_level
        
        return scaled_width, scaled_height, map_width, map_height
    
    def _clamp_map_offset(self):
        if not self.hex_map:
            return
        
        scaled_width, scaled_height, _, _ = self._get_map_bounds()
        
        max_offset_x = SCREEN_WIDTH - scaled_width * 0.5
        min_offset_x = -scaled_width * 0.5
        max_offset_y = SCREEN_HEIGHT - scaled_height * 0.5
        min_offset_y = -scaled_height * 0.5
        
        self.map_offset_x = max(min_offset_x, min(max_offset_x, self.map_offset_x))
        self.map_offset_y = max(min_offset_y, min(max_offset_y, self.map_offset_y))
    
    def _center_map(self):
        if not self.hex_map:
            return
        
        scaled_width, scaled_height, _, _ = self._get_map_bounds()
        
        self.map_offset_x = (SCREEN_WIDTH - scaled_width) / 2
        self.map_offset_y = (SCREEN_HEIGHT - scaled_height) / 2
    
    def _toggle_unit_detail_panel(self):
        if self.selected_unit:
            self.unit_detail_panel_visible = not self.unit_detail_panel_visible
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
                
                if self.game_state == GAME_STATES['MENU']:
                    self.main_menu.set_mouse_state(event.pos, self.mouse_buttons_pressed.get(1, False))
                elif self.game_state == GAME_STATES['SETTINGS']:
                    self.settings_menu.set_mouse_state(event.pos, self.mouse_buttons_pressed.get(1, False))
                elif self.game_state == GAME_STATES['HELP']:
                    self.help_menu.set_mouse_state(event.pos, self.mouse_buttons_pressed.get(1, False))
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_buttons_pressed[event.button] = True
                
                if event.button == 3:
                    if self.game_state == GAME_STATES['PLAYING']:
                        if self.unit_detail_panel_visible:
                            self.unit_detail_panel_visible = False
                        elif self.tile_detail_panel_visible:
                            if hasattr(self, 'tile_detail_close_button') and self.tile_detail_close_button.collidepoint(event.pos):
                                self.tile_detail_panel_visible = False
                            else:
                                q, r = self.get_screen_to_hex(event.pos[0], event.pos[1])
                                tile = self.hex_map.get_tile(q, r) if self.hex_map else None
                                if tile:
                                    self.tile_detail_tile = tile
                                else:
                                    self.tile_detail_panel_visible = False
                        else:
                            q, r = self.get_screen_to_hex(event.pos[0], event.pos[1])
                            tile = self.hex_map.get_tile(q, r) if self.hex_map else None
                            if tile:
                                self.tile_detail_tile = tile
                                self.tile_detail_panel_visible = True
                
                if event.button == 1:
                    self.mouse_pos = event.pos
                    
                    if self.game_state == GAME_STATES['MENU']:
                        self.main_menu.set_mouse_state(event.pos, True)
                        action = self.main_menu.handle_click()
                        if action:
                            self._handle_menu_action(action)
                    
                    elif self.game_state == GAME_STATES['PLAYING']:
                        settings_visible = self.settings_popup and self.settings_popup.visible
                        build_visible = self.build_popup and self.build_popup.visible
                        train_visible = self.train_popup and self.train_popup.visible
                        
                        if self.tile_detail_panel_visible:
                            if hasattr(self, 'tile_detail_close_button') and self.tile_detail_close_button.collidepoint(event.pos):
                                self.tile_detail_panel_visible = False
                                continue
                        
                        if self.unit_detail_panel_visible:
                            if hasattr(self, 'unit_detail_close_button') and self.unit_detail_close_button.collidepoint(event.pos):
                                self.unit_detail_panel_visible = False
                                continue
                            if self.unit_detail_panel_rect.collidepoint(event.pos):
                                continue
                        
                        if self.unit_selection_pending:
                            unit_selection_action = self._handle_unit_selection_click(event.pos)
                            if unit_selection_action:
                                self._select_specific_unit(unit_selection_action)
                            else:
                                if not (settings_visible or build_visible or train_visible):
                                    q, r = self.get_screen_to_hex(event.pos[0], event.pos[1])
                                    self.handle_tile_click(q, r)
                            continue
                        
                        popup_action = None
                        if settings_visible:
                            self.settings_popup.set_mouse_state(event.pos, True)
                            popup_action = self.settings_popup.handle_click()
                        elif build_visible:
                            self.build_popup.set_mouse_state(event.pos, True)
                            popup_action = self.build_popup.handle_click()
                        elif train_visible:
                            self.train_popup.set_mouse_state(event.pos, True)
                            popup_action = self.train_popup.handle_click()
                        
                        if popup_action:
                            self._handle_popup_action(popup_action)
                        else:
                            action = self.ui.handle_click(event.pos, self.ui.buttons)
                            
                            if action:
                                if action == 'end_turn':
                                    self.end_turn()
                                elif action == 'open_settings_popup':
                                    if self.settings_popup:
                                        self.settings_popup.show()
                                elif action == 'open_build_popup':
                                    if self.build_popup:
                                        if self.players:
                                            self.build_popup.update_player(self.get_current_player())
                                        if self.selected_tile:
                                            self.build_popup.set_selected_tile(self.selected_tile)
                                        self.build_popup.show()
                                elif action == 'open_train_popup':
                                    if self.train_popup:
                                        if self.players:
                                            self.train_popup.update_player(self.get_current_player())
                                        if self.selected_tile:
                                            self.train_popup.set_selected_tile(self.selected_tile)
                                        self.train_popup.show()
                                elif action == 'expand_territory':
                                    self.expand_territory()
                                elif action == 'return_to_menu':
                                    if self.settings_popup:
                                        self.settings_popup.hide()
                                    if self.build_popup:
                                        self.build_popup.hide()
                                    if self.train_popup:
                                        self.train_popup.hide()
                                    self.game_state = GAME_STATES['MENU']
                            else:
                                if not (settings_visible or build_visible or train_visible):
                                    q, r = self.get_screen_to_hex(event.pos[0], event.pos[1])
                                    self.handle_tile_click(q, r)
                    
                    elif self.game_state == GAME_STATES['SETTINGS']:
                        self.settings_menu.set_mouse_state(event.pos, True)
                        action = self.settings_menu.handle_click()
                        if action:
                            self._handle_menu_action(action)
                    
                    elif self.game_state == GAME_STATES['HELP']:
                        self.help_menu.set_mouse_state(event.pos, True)
                        action = self.help_menu.handle_click()
                        if action:
                            self._handle_menu_action(action)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_buttons_pressed[event.button] = False
                
                if self.game_state == GAME_STATES['MENU']:
                    self.main_menu.set_mouse_state(self.mouse_pos, False)
                elif self.game_state == GAME_STATES['PLAYING']:
                    settings_visible = self.settings_popup and self.settings_popup.visible
                    build_visible = self.build_popup and self.build_popup.visible
                    train_visible = self.train_popup and self.train_popup.visible
                    
                    popup_action = None
                    if settings_visible:
                        self.settings_popup.set_mouse_state(event.pos, False)
                        popup_action = self.settings_popup.handle_click()
                    elif build_visible:
                        self.build_popup.set_mouse_state(event.pos, False)
                        popup_action = self.build_popup.handle_click()
                    elif train_visible:
                        self.train_popup.set_mouse_state(event.pos, False)
                        popup_action = self.train_popup.handle_click()
                    
                    if popup_action:
                        self._handle_popup_action(popup_action)
                elif self.game_state == GAME_STATES['SETTINGS']:
                    self.settings_menu.set_mouse_state(self.mouse_pos, False)
                elif self.game_state == GAME_STATES['HELP']:
                    self.help_menu.set_mouse_state(self.mouse_pos, False)
            
            elif event.type == pygame.MOUSEWHEEL:
                if self.game_state == GAME_STATES['HELP']:
                    self.help_menu.handle_scroll(event.y)
                elif self.game_state == GAME_STATES['PLAYING']:
                    self._handle_zoom(event.y, self.mouse_pos)
            
            elif event.type == pygame.KEYDOWN:
                if self.game_state == GAME_STATES['PLAYING']:
                    if event.key == pygame.K_SPACE:
                        self._center_map()
        
        if self.game_state == GAME_STATES['PLAYING']:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.map_offset_x += 5
            if keys[pygame.K_RIGHT]:
                self.map_offset_x -= 5
            if keys[pygame.K_UP]:
                self.map_offset_y += 5
            if keys[pygame.K_DOWN]:
                self.map_offset_y -= 5
            
            self._clamp_map_offset()
            
            if keys[pygame.K_ESCAPE]:
                self.game_state = GAME_STATES['MENU']
    
    def _draw_popups(self):
        if not self._popup_initialized:
            return
        
        dt = self.animation_manager.get_dt() if self.animation_manager else 0.016
        
        settings_visible = self.settings_popup and self.settings_popup.visible
        build_visible = self.build_popup and self.build_popup.visible
        train_visible = self.train_popup and self.train_popup.visible
        
        if settings_visible:
            self.settings_popup.set_mouse_state(self.mouse_pos, self.mouse_buttons_pressed.get(1, False))
            self.settings_popup.update(dt)
            self.settings_popup.draw(self.screen)
        
        elif build_visible:
            self.build_popup.set_mouse_state(self.mouse_pos, self.mouse_buttons_pressed.get(1, False))
            if self.players:
                self.build_popup.update_player(self.get_current_player())
            self.build_popup.update(dt)
            self.build_popup.draw(self.screen)
        
        elif train_visible:
            self.train_popup.set_mouse_state(self.mouse_pos, self.mouse_buttons_pressed.get(1, False))
            if self.players:
                self.train_popup.update_player(self.get_current_player())
            self.train_popup.update(dt)
            self.train_popup.draw(self.screen)
    
    def _handle_popup_action(self, action: str):
        if action == 'close':
            if self.settings_popup and self.settings_popup.visible:
                self.settings_popup.hide()
            if self.build_popup and self.build_popup.visible:
                self.build_popup.hide()
            if self.train_popup and self.train_popup.visible:
                self.train_popup.hide()
        
        elif action == 'set_language_en':
            self.set_language('en')
            if self.settings_popup:
                self.settings_popup.hide()
        
        elif action == 'set_language_zh':
            if self.ui.get_font_manager().is_chinese_available():
                self.set_language('zh')
                if self.settings_popup:
                    self.settings_popup.hide()
            else:
                self.add_message("Chinese font not found. Put .ttf file in 'fonts/' folder.")
        
        elif action == 'show_font_help':
            self.add_message("To use Chinese:")
            self.add_message("1. Create 'fonts/' folder in game directory")
            self.add_message("2. Put Chinese .ttf font file in it")
            self.add_message("3. Restart the game")
        
        elif action.startswith('build_'):
            building_type = action[6:]
            self.build_structure(building_type)
            if self.build_popup:
                self.build_popup.hide()
        
        elif action.startswith('train_'):
            unit_type = action[6:]
            self.train_unit(unit_type)
    
    def _handle_menu_action(self, action: str):
        if action == 'start_game':
            self.new_game()
            self.game_state = GAME_STATES['PLAYING']
        
        elif action == 'show_help':
            self.previous_state = self.game_state
            self.game_state = GAME_STATES['HELP']
        
        elif action == 'show_settings':
            self.previous_state = self.game_state
            self.game_state = GAME_STATES['SETTINGS']
        
        elif action == 'quit_game':
            self.running = False
        
        elif action == 'back_to_menu':
            self.game_state = GAME_STATES['MENU']
        
        elif action == 'set_language_en':
            self.set_language('en')
            self.game_state = GAME_STATES['MENU']
        
        elif action == 'set_language_zh':
            if self.ui.get_font_manager().is_chinese_available():
                self.set_language('zh')
                self.game_state = GAME_STATES['MENU']
            else:
                print("Chinese font not available")
        
        elif action == 'show_font_help':
            pass
    
    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


def main():
    game = Game(default_language='en')
    game.run()


if __name__ == '__main__':
    main()
