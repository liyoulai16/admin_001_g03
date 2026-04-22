import pygame
import sys
from typing import Dict, Tuple, Optional, List
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BACKGROUND_COLOR, 
    HEX_SIZE, MAP_ROWS, MAP_COLS,
    BUILDING_INFO, SELECTED_COLOR, GAME_STATES, UI_COLORS
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
from popup import SettingsPopup, BuildPopup


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
        
        self.game_messages: List[str] = []
        self.running = True
        
        self.mouse_pos = (0, 0)
        self.mouse_down = False
        self.mouse_buttons_pressed = {1: False, 2: False, 3: False}
        
        self.settings_popup = None
        self.build_popup = None
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
                300, 350, self.loc, self.ui.get_font_manager(),
                self.get_current_player()
            )
            self.build_popup.update_position(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        self._popup_initialized = True
    
    def _refresh_popups(self):
        if self._popup_initialized:
            if self.players:
                self.settings_popup = SettingsPopup(
                    300, 280, self.loc, self.ui.get_font_manager()
                )
                self.settings_popup.update_position(SCREEN_WIDTH, SCREEN_HEIGHT)
                
                self.build_popup = BuildPopup(
                    300, 350, self.loc, self.ui.get_font_manager(),
                    self.get_current_player()
                )
                self.build_popup.update_position(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    def set_language(self, language: str):
        self.loc.set_language(language)
        self.ui.set_localization(self.loc)
        pygame.display.set_caption(self.loc.t('game_title'))
        
        self.main_menu = MainMenu(self.screen, self.loc, self.animation_manager)
        self.settings_menu = SettingsMenu(self.screen, self.loc, self.animation_manager)
        self.help_menu = HelpMenu(self.screen, self.loc)
        
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
        x = screen_x - self.map_offset_x
        y = screen_y - self.map_offset_y
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
        
        if tile.unit and tile.unit.owner == self.get_current_player():
            self.selected_unit = tile.unit
            self.show_unit_range(tile.unit)
    
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
    
    def move_unit(self, unit: Unit, target_tile: HexTile):
        source_tile = self.hex_map.get_tile(unit.tile_q, unit.tile_r)
        if not source_tile:
            return
        
        if self.animation_manager:
            start_x, start_y = self.hex_map.hex_to_pixel(unit.tile_q, unit.tile_r)
            end_x, end_y = self.hex_map.hex_to_pixel(target_tile.q, target_tile.r)
            start_screen_x = start_x + self.map_offset_x
            start_screen_y = start_y + self.map_offset_y
            end_screen_x = end_x + self.map_offset_x
            end_screen_y = end_y + self.map_offset_y
            
            unit_id = id(unit)
            self.animation_manager.add_unit_move(unit_id, (start_screen_x, start_screen_y), 
                                                    (end_screen_x, end_screen_y))
        
        source_tile.unit = None
        unit.tile_q = target_tile.q
        unit.tile_r = target_tile.r
        target_tile.unit = unit
        unit.moved_this_turn = True
        
        old_owner = target_tile.owner
        if target_tile.owner != unit.owner:
            if target_tile.owner:
                target_tile.owner.tiles_owned -= 1
            
            target_tile.owner = unit.owner
            unit.owner.tiles_owned += 1
            
            unit_name = self.loc.get_unit_name(unit.unit_type)
            if old_owner:
                msg = f"{unit_name} {self._get_msg('msg_captured_enemy_tile')}"
            else:
                msg = f"{unit_name} {self._get_msg('msg_captured_neutral_tile')}"
            self.add_message(msg)
            
            if self.animation_manager:
                x, y = self.hex_map.hex_to_pixel(target_tile.q, target_tile.r)
                screen_x = x + self.map_offset_x
                screen_y = y + self.map_offset_y
                self.animation_manager.particle_system.emit(
                    screen_x, screen_y, unit.owner.color, count=20, spread=100
                )
        
        self.select_tile(target_tile)
    
    def attack_with_unit(self, unit: Unit, target_tile: HexTile):
        unit.attacked_this_turn = True
        unit_name = self.loc.get_unit_name(unit.unit_type)
        
        if self.animation_manager:
            start_x, start_y = self.hex_map.hex_to_pixel(unit.tile_q, unit.tile_r)
            target_x, target_y = self.hex_map.hex_to_pixel(target_tile.q, target_tile.r)
            start_screen_x = start_x + self.map_offset_x
            start_screen_y = start_y + self.map_offset_y
            target_screen_x = target_x + self.map_offset_x
            target_screen_y = target_y + self.map_offset_y
            
            unit_id = id(unit)
            self.animation_manager.add_unit_attack(unit_id, (start_screen_x, start_screen_y),
                                                      (target_screen_x, target_screen_y))
        
        if target_tile.unit and target_tile.unit.owner != unit.owner:
            target = target_tile.unit
            target_name = self.loc.get_unit_name(target.unit_type)
            damage = max(1, unit.attack - target.defense // 2)
            target.health -= damage
            
            msg = f"{unit_name} {self._get_msg('msg_attacked')} {target_name}, {damage} {self._get_msg('msg_damage')}"
            
            if target.health <= 0:
                target.owner.remove_unit(target)
                target_tile.unit = None
                msg += f", {target_name} {self._get_msg('msg_destroyed')}"
                
                if self.animation_manager:
                    x, y = self.hex_map.hex_to_pixel(target_tile.q, target_tile.r)
                    screen_x = x + self.map_offset_x
                    screen_y = y + self.map_offset_y
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
                
                target_tile.owner = unit.owner
                unit.owner.tiles_owned += 1
                self.add_message(f"{unit_name} {self._get_msg('msg_captured_enemy_tile')}")
        
        self.select_tile(target_tile)
    
    def build_structure(self, building_type: str):
        if not self.selected_tile:
            return
        
        player = self.get_current_player()
        if self.selected_tile.owner != player:
            self.add_message(self._get_msg('msg_can_only_build_own'))
            return
        
        if self.selected_tile.building:
            self.add_message(self._get_msg('msg_tile_has_building'))
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
                screen_x = x + self.map_offset_x
                screen_y = y + self.map_offset_y
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
        
        if self.hex_map:
            for (q, r), tile in self.hex_map.tiles.items():
                x, y = self.hex_map.hex_to_pixel(q, r)
                screen_x = x + self.map_offset_x
                screen_y = y + self.map_offset_y
                
                corners = self.hex_map.get_hex_corners(screen_x, screen_y)
                
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
                
                pygame.draw.polygon(self.screen, tile.get_color(), corners)
                pygame.draw.polygon(self.screen, tile.get_border_color(), corners, 2)
                
                if tile.building:
                    self.draw_building_icon(screen_x, screen_y, tile.building)
                
                if tile.unit:
                    unit_id = id(tile.unit)
                    if self.animation_manager and self.animation_manager.is_unit_animating(unit_id):
                        anim_pos = self.animation_manager.get_unit_position(unit_id, (screen_x, screen_y))
                        self.draw_unit_icon(anim_pos[0], anim_pos[1], tile.unit)
                    else:
                        self.draw_unit_icon(screen_x, screen_y, tile.unit)
        
        if self.animation_manager:
            self.animation_manager.particle_system.draw(self.screen)
        
        self.ui.set_mouse_state(self.mouse_pos, self.mouse_buttons_pressed.get(1, False))
        
        self.ui.draw_resource_panel(self.screen, self.get_current_player(), self.turn)
        self.ui.draw_tile_info(self.screen, self.selected_tile)
        buttons = self.ui.draw_action_buttons(self.screen, self.selected_tile, self.get_current_player())
        self.ui.draw_combat_log(self.screen, self.game_messages)
        
        turn_indicator = self.ui.font_large.render(
            f"{self.loc.t('current_player')}: {self.get_current_player().name}", 
            True, self.get_current_player().color
        )
        self.screen.blit(turn_indicator, (10, 10))
        
        self._draw_popups()
    
    def draw_building_icon(self, x: float, y: float, building: Building):
        color = building.owner.color
        icon_size = 16
        
        icon_rect = pygame.Rect(x - icon_size//2, y - icon_size//2 - 5, icon_size, icon_size)
        pygame.draw.rect(self.screen, color, icon_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), icon_rect, 1)
        
        text = self.ui.font_small.render("B", True, (255, 255, 255))
        text_rect = text.get_rect(center=icon_rect.center)
        self.screen.blit(text, text_rect)
    
    def draw_unit_icon(self, x: float, y: float, unit: Unit):
        color = unit.owner.color
        icon_size = 14
        
        icon_rect = pygame.Rect(x - icon_size//2, y + 8, icon_size, icon_size)
        pygame.draw.circle(self.screen, color, (int(x), int(y + 15)), icon_size//2)
        pygame.draw.circle(self.screen, (255, 255, 255), (int(x), int(y + 15)), icon_size//2, 1)
        
        hp_percent = unit.health / unit.max_health
        hp_bar_width = 18
        hp_bar_height = 3
        hp_x = x - hp_bar_width//2
        hp_y = y + 22
        
        pygame.draw.rect(self.screen, (80, 80, 80), (hp_x, hp_y, hp_bar_width, hp_bar_height))
        hp_color = (100, 255, 100) if hp_percent > 0.5 else (255, 200, 50) if hp_percent > 0.25 else (255, 80, 80)
        pygame.draw.rect(self.screen, hp_color, (hp_x, hp_y, hp_bar_width * hp_percent, hp_bar_height))
    
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
                        
                        popup_action = None
                        if settings_visible:
                            self.settings_popup.set_mouse_state(event.pos, True)
                            popup_action = self.settings_popup.handle_click()
                        elif build_visible:
                            self.build_popup.set_mouse_state(event.pos, True)
                            popup_action = self.build_popup.handle_click()
                        
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
                                        self.build_popup.show()
                                elif action == 'return_to_menu':
                                    if self.settings_popup:
                                        self.settings_popup.hide()
                                    if self.build_popup:
                                        self.build_popup.hide()
                                    self.game_state = GAME_STATES['MENU']
                            else:
                                if not (settings_visible or build_visible):
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
                elif self.game_state == GAME_STATES['SETTINGS']:
                    self.settings_menu.set_mouse_state(self.mouse_pos, False)
                elif self.game_state == GAME_STATES['HELP']:
                    self.help_menu.set_mouse_state(self.mouse_pos, False)
            
            elif event.type == pygame.MOUSEWHEEL:
                if self.game_state == GAME_STATES['HELP']:
                    self.help_menu.handle_scroll(event.y)
        
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
            
            if keys[pygame.K_ESCAPE]:
                self.game_state = GAME_STATES['MENU']
    
    def _draw_popups(self):
        if not self._popup_initialized:
            return
        
        dt = self.animation_manager.get_dt() if self.animation_manager else 0.016
        
        settings_visible = self.settings_popup and self.settings_popup.visible
        build_visible = self.build_popup and self.build_popup.visible
        
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
    
    def _handle_popup_action(self, action: str):
        if action == 'close':
            if self.settings_popup and self.settings_popup.visible:
                self.settings_popup.hide()
            if self.build_popup and self.build_popup.visible:
                self.build_popup.hide()
        
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
