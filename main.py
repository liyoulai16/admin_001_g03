import pygame
import sys
from typing import Dict, Tuple, Optional, List
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BACKGROUND_COLOR, 
    HEX_SIZE, MAP_ROWS, MAP_COLS, TERRAIN_NAMES,
    BUILDING_INFO, UNIT_INFO, SELECTED_COLOR
)
from hex_map import HexMap, HexTile
from terrain_generator import TerrainGenerator
from player import Player, Building, Unit
from ai import SimpleAI
from ui import UI


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Turn-based Strategy - Hex Map")
        self.clock = pygame.time.Clock()
        
        self.ui = UI(SCREEN_WIDTH, SCREEN_HEIGHT)
        
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
        
    def new_game(self):
        self.hex_map = HexMap(MAP_ROWS, MAP_COLS)
        terrain_gen = TerrainGenerator(seed=42)
        terrain_gen.generate_random_map(self.hex_map, MAP_ROWS, MAP_COLS)
        
        player1 = Player(player_id=1, is_ai=False)
        player2 = Player(player_id=2, is_ai=True)
        
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
        self.game_messages = ["Game started! You are Player 1 (Blue)"]
        self.ui.close_build_menu()
    
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
            
            if old_owner:
                msg = f"{unit.name} captured enemy tile!"
            else:
                msg = f"{unit.name} captured neutral tile"
            self.add_message(msg)
        
        self.select_tile(target_tile)
    
    def attack_with_unit(self, unit: Unit, target_tile: HexTile):
        unit.attacked_this_turn = True
        
        if target_tile.unit and target_tile.unit.owner != unit.owner:
            target = target_tile.unit
            damage = max(1, unit.attack - target.defense // 2)
            target.health -= damage
            
            msg = f"{unit.name} attacked {target.name}, {damage} damage"
            
            if target.health <= 0:
                target.owner.remove_unit(target)
                target_tile.unit = None
                msg += f", {target.name} destroyed!"
            
            self.add_message(msg)
        
        elif target_tile.building and target_tile.building.owner != unit.owner:
            target = target_tile.building
            damage = max(1, unit.attack - 5)
            target.health -= damage
            
            msg = f"{unit.name} attacked {target.name}, {damage} damage"
            
            if target.health <= 0:
                target.owner.remove_building(target)
                target_tile.building = None
                msg += f", {target.name} destroyed!"
            
            self.add_message(msg)
        
        elif target_tile.owner and target_tile.owner != unit.owner:
            if not target_tile.unit and not target_tile.building:
                if target_tile.owner:
                    target_tile.owner.tiles_owned -= 1
                
                target_tile.owner = unit.owner
                unit.owner.tiles_owned += 1
                self.add_message(f"{unit.name} captured enemy tile!")
        
        self.select_tile(target_tile)
    
    def build_structure(self, building_type: str):
        if not self.selected_tile:
            return
        
        player = self.get_current_player()
        if self.selected_tile.owner != player:
            self.add_message("Can only build on your own tiles!")
            return
        
        if self.selected_tile.building:
            self.add_message("Tile already has a building!")
            return
        
        if building_type not in BUILDING_INFO:
            return
        
        cost = BUILDING_INFO[building_type]['cost']
        if not player.can_afford(cost):
            self.add_message("Not enough resources!")
            return
        
        if player.spend_resources(cost):
            building = Building(building_type, self.selected_tile.q, self.selected_tile.r, player)
            self.selected_tile.building = building
            player.add_building(building)
            
            name = BUILDING_INFO[building_type]['name']
            self.add_message(f"Built {name}")
            self.ui.close_build_menu()
    
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
            self.add_message(f"--- AI {next_player.player_id} Turn ---")
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
                self.add_message(f"New turn! Gained: {income_str}")
        else:
            if self.current_player_idx == 0:
                self.turn += 1
            
            income = next_player.calculate_income()
            next_player.add_resources(income)
            
            income_str = ", ".join([f"{k}+{v}" for k, v in income.items() if v > 0])
            if income_str:
                self.add_message(f"New turn! Gained: {income_str}")
        
        self.check_game_end()
    
    def check_game_end(self):
        for player in self.players:
            if player.tiles_owned <= 0 and len(player.units) <= 0:
                winner = [p for p in self.players if p != player][0]
                self.add_message(f"Game over! {winner.name} wins!")
                self.running = False
                return
    
    def add_message(self, msg: str):
        self.game_messages.append(msg)
        if len(self.game_messages) > 50:
            self.game_messages = self.game_messages[-50:]
    
    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        if self.hex_map:
            for (q, r), tile in self.hex_map.tiles.items():
                x, y = self.hex_map.hex_to_pixel(q, r)
                screen_x = x + self.map_offset_x
                screen_y = y + self.map_offset_y
                
                corners = self.hex_map.get_hex_corners(screen_x, screen_y)
                
                pygame.draw.polygon(self.screen, tile.get_color(), corners)
                pygame.draw.polygon(self.screen, tile.get_border_color(), corners, 2)
                
                if tile.building:
                    self.draw_building_icon(screen_x, screen_y, tile.building)
                
                if tile.unit:
                    self.draw_unit_icon(screen_x, screen_y, tile.unit)
        
        self.ui.draw_resource_panel(self.screen, self.get_current_player(), self.turn)
        self.ui.draw_tile_info(self.screen, self.selected_tile)
        buttons = self.ui.draw_action_buttons(self.screen, self.selected_tile, self.get_current_player())
        self.ui.draw_combat_log(self.screen, self.game_messages)
        
        turn_indicator = self.ui.font_large.render(
            f"Current: {self.get_current_player().name}", 
            True, self.get_current_player().color
        )
        self.screen.blit(turn_indicator, (10, 10))
        
        pygame.display.flip()
    
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
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    action = self.ui.handle_click(mouse_pos, self.ui.buttons)
                    
                    if action:
                        if action == 'end_turn':
                            self.end_turn()
                        elif action == 'open_build_menu':
                            self.ui.open_build_menu()
                        elif action == 'close_build_menu':
                            self.ui.close_build_menu()
                        elif action.startswith('build_'):
                            building_type = action[6:]
                            self.build_structure(building_type)
                    else:
                        q, r = self.get_screen_to_hex(mouse_pos[0], mouse_pos[1])
                        self.handle_tile_click(q, r)
            
            elif event.type == pygame.MOUSEMOTION:
                pass
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.map_offset_x += 5
        if keys[pygame.K_RIGHT]:
            self.map_offset_x -= 5
        if keys[pygame.K_UP]:
            self.map_offset_y += 5
        if keys[pygame.K_DOWN]:
            self.map_offset_y -= 5
    
    def run(self):
        self.new_game()
        
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


def main():
    game = Game()
    game.run()


if __name__ == '__main__':
    main()
