import pygame
from typing import Dict, Optional, Tuple, List
from config import (
    UI_PANEL_COLOR, TEXT_COLOR, HIGHLIGHT_COLOR, SELECTED_COLOR,
    RESOURCE_ICONS, RESOURCE_NAMES, BUILDING_INFO, UNIT_INFO, TERRAIN_NAMES
)
from player import Player, Building, Unit
from hex_map import HexMap, HexTile


class UI:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.panel_width = 250
        self.panel_x = screen_width - self.panel_width
        
        try:
            self.font_large = pygame.font.SysFont('simhei', 20)
            self.font_medium = pygame.font.SysFont('simhei', 16)
            self.font_small = pygame.font.SysFont('simhei', 14)
        except:
            self.font_large = pygame.font.Font(None, 24)
            self.font_medium = pygame.font.Font(None, 20)
            self.font_small = pygame.font.Font(None, 18)
        
        self.buttons: List[Dict] = []
        self.build_menu_open = False
        self.unit_menu_open = False
    
    def draw_resource_panel(self, screen: pygame.Surface, player: Player, turn: int):
        panel_rect = pygame.Rect(self.panel_x, 0, self.panel_width, 120)
        pygame.draw.rect(screen, UI_PANEL_COLOR, panel_rect)
        pygame.draw.line(screen, (100, 100, 100), 
                        (self.panel_x, 0), (self.panel_x, self.screen_height), 2)
        
        turn_text = self.font_large.render(f"回合: {turn}", True, TEXT_COLOR)
        screen.blit(turn_text, (self.panel_x + 10, 10))
        
        y_offset = 45
        for res_type, amount in player.resources.items():
            icon = RESOURCE_ICONS.get(res_type, '')
            name = RESOURCE_NAMES.get(res_type, res_type)
            text = self.font_medium.render(f"{icon} {name}: {amount}", True, TEXT_COLOR)
            screen.blit(text, (self.panel_x + 10, y_offset))
            y_offset += 25
    
    def draw_tile_info(self, screen: pygame.Surface, tile: Optional[HexTile]):
        panel_rect = pygame.Rect(self.panel_x, 130, self.panel_width, 180)
        pygame.draw.rect(screen, UI_PANEL_COLOR, panel_rect)
        
        title = self.font_large.render("地块信息", True, TEXT_COLOR)
        screen.blit(title, (self.panel_x + 10, 140))
        
        if tile is None:
            no_info = self.font_medium.render("未选中地块", True, (150, 150, 150))
            screen.blit(no_info, (self.panel_x + 10, 170))
            return
        
        terrain_name = TERRAIN_NAMES.get(tile.terrain, tile.terrain)
        terrain_text = self.font_medium.render(f"地形: {terrain_name}", True, TEXT_COLOR)
        screen.blit(terrain_text, (self.panel_x + 10, 170))
        
        owner_text = self.font_medium.render(f"所有者: {tile.owner.name if tile.owner else '无'}", 
                                             True, TEXT_COLOR)
        screen.blit(owner_text, (self.panel_x + 10, 195))
        
        if tile.building:
            building_text = self.font_medium.render(f"建筑: {tile.building.name}", True, TEXT_COLOR)
            screen.blit(building_text, (self.panel_x + 10, 220))
            hp_text = self.font_small.render(f"HP: {tile.building.health}/{tile.building.max_health}", 
                                             True, TEXT_COLOR)
            screen.blit(hp_text, (self.panel_x + 20, 245))
        
        if tile.unit:
            unit_text = self.font_medium.render(f"单位: {tile.unit.name}", True, TEXT_COLOR)
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
            'text': '结束回合',
            'action': 'end_turn',
            'color': (80, 150, 100)
        }
        self.buttons.append(end_turn_button)
        self._draw_button(screen, end_turn_button)
        
        button_y += button_height + 10
        
        if selected_tile and selected_tile.owner == current_player:
            if not selected_tile.building and selected_tile.terrain not in ['mountain', 'water']:
                build_button = {
                    'rect': pygame.Rect(self.panel_x + 10, button_y, button_width, button_height),
                    'text': '建造建筑',
                    'action': 'open_build_menu',
                    'color': (100, 100, 180)
                }
                self.buttons.append(build_button)
                self._draw_button(screen, build_button)
                button_y += button_height + 10
            
            if selected_tile.unit:
                move_text = '已移动' if selected_tile.unit.moved_this_turn else '可移动'
                attack_text = '已攻击' if selected_tile.unit.attacked_this_turn else '可攻击'
                info_text = f"单位状态: {move_text}, {attack_text}"
                info_surface = self.font_small.render(info_text, True, TEXT_COLOR)
                screen.blit(info_surface, (self.panel_x + 10, button_y + 5))
        
        if self.build_menu_open and selected_tile:
            self._draw_build_menu(screen, current_player, selected_tile)
        
        return self.buttons
    
    def _draw_build_menu(self, screen: pygame.Surface, player: Player, tile: HexTile):
        menu_y = 400
        menu_height = 30
        menu_width = self.panel_width - 30
        
        title = self.font_medium.render("选择建筑:", True, TEXT_COLOR)
        screen.blit(title, (self.panel_x + 15, menu_y))
        menu_y += 35
        
        for building_type, info in BUILDING_INFO.items():
            cost = info['cost']
            can_afford = player.can_afford(cost)
            
            button_color = (80, 80, 150) if can_afford else (80, 80, 80)
            
            cost_str = ", ".join([f"{RESOURCE_ICONS.get(k, k)}{v}" for k, v in cost.items()])
            button_text = f"{info['name']} ({cost_str})"
            
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
            'text': '取消',
            'action': 'close_build_menu',
            'color': (120, 80, 80)
        }
        self.buttons.append(close_button)
        self._draw_button(screen, close_button, small=True)
    
    def _draw_button(self, screen: pygame.Surface, button: Dict, small: bool = False):
        pygame.draw.rect(screen, button['color'], button['rect'])
        pygame.draw.rect(screen, (50, 50, 50), button['rect'], 2)
        
        font = self.font_small if small else self.font_medium
        text_surface = font.render(button['text'], True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=button['rect'].center)
        screen.blit(text_surface, text_rect)
    
    def handle_click(self, mouse_pos: Tuple[int, int], buttons: List[Dict]) -> Optional[str]:
        for button in buttons:
            if button.get('enabled', True) and button['rect'].collidepoint(mouse_pos):
                return button['action']
        return None
    
    def open_build_menu(self):
        self.build_menu_open = True
    
    def close_build_menu(self):
        self.build_menu_open = False
    
    def draw_combat_log(self, screen: pygame.Surface, messages: List[str], max_messages: int = 5):
        log_y = self.screen_height - 150
        log_height = 140
        
        panel_rect = pygame.Rect(10, log_y, self.screen_width - self.panel_width - 30, log_height)
        pygame.draw.rect(screen, (30, 35, 45), panel_rect)
        pygame.draw.rect(screen, (80, 80, 80), panel_rect, 1)
        
        title = self.font_medium.render("战斗日志", True, TEXT_COLOR)
        screen.blit(title, (20, log_y + 5))
        
        start_idx = max(0, len(messages) - max_messages)
        display_messages = messages[start_idx:]
        
        y_offset = log_y + 30
        for msg in display_messages:
            text_surface = self.font_small.render(msg, True, (200, 200, 200))
            screen.blit(text_surface, (20, y_offset))
            y_offset += 22
