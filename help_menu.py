import pygame
import math
from typing import Dict, List, Optional, Tuple
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, UI_COLORS, BACKGROUND_COLOR,
    TERRAIN_COLORS, BUILDING_INFO, UNIT_INFO
)
from localization import Localization
from font_manager import FontManager
from menu import MenuButton


class HelpPage:
    def __init__(self, title: str, content: List[Dict]):
        self.title = title
        self.content = content
        self.scroll_offset = 0.0
        self.max_scroll = 0.0


class HelpMenu:
    def __init__(self, screen: pygame.Surface, localization: Localization):
        self.screen = screen
        self.loc = localization
        
        if not pygame.font.get_init():
            pygame.font.init()
        
        self.font_manager = FontManager()
        self._init_fonts()
        
        self.buttons: List[MenuButton] = []
        self.page_buttons: List[MenuButton] = []
        self._create_buttons()
        
        self.current_page_idx = 0
        self.pages = self._create_pages()
        
        self.mouse_pos = (0, 0)
        self.mouse_down = False
        self.last_time = pygame.time.get_ticks() / 1000.0
        
        self.scroll_speed = 0.0
        self.is_scrolling = False
    
    def _init_fonts(self):
        language = self.loc.get_language()
        self.font_title = self.font_manager.get_font(40, language)
        self.font_page_title = self.font_manager.get_font(32, language)
        self.font_section = self.font_manager.get_font(24, language)
        self.font_text = self.font_manager.get_font(20, language)
        self.font_small = self.font_manager.get_font(16, language)
        self.font_button = self.font_manager.get_font(22, language)
    
    def _create_buttons(self):
        button_width = 150
        button_height = 45
        bottom_y = SCREEN_HEIGHT - 80
        
        back_button = MenuButton(
            pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, bottom_y, button_width, button_height),
            self.loc.t('back_to_menu'),
            'back_to_menu',
            (120, 80, 80)
        )
        self.buttons.append(back_button)
        
        prev_button = MenuButton(
            pygame.Rect(50, bottom_y, button_width, button_height),
            self.loc.t('prev_page'),
            'prev_page',
            (80, 100, 150)
        )
        self.buttons.append(prev_button)
        
        next_button = MenuButton(
            pygame.Rect(SCREEN_WIDTH - 50 - button_width, bottom_y, button_width, button_height),
            self.loc.t('next_page'),
            'next_page',
            (80, 100, 150)
        )
        self.buttons.append(next_button)
    
    def _create_pages(self) -> List[HelpPage]:
        pages = []
        
        pages.append(HelpPage(
            self.loc.t('help_title_welcome'),
            [
                {'type': 'section', 'text': self.loc.t('help_section_overview')},
                {'type': 'text', 'text': self.loc.t('help_text_overview_1')},
                {'type': 'text', 'text': self.loc.t('help_text_overview_2')},
                {'type': 'text', 'text': self.loc.t('help_text_overview_3')},
                {'type': 'section', 'text': self.loc.t('help_section_game_goal')},
                {'type': 'text', 'text': self.loc.t('help_text_goal_1')},
                {'type': 'text', 'text': self.loc.t('help_text_goal_2')},
            ]
        ))
        
        pages.append(HelpPage(
            self.loc.t('help_title_controls'),
            [
                {'type': 'section', 'text': self.loc.t('help_section_mouse')},
                {'type': 'bullet', 'text': self.loc.t('help_ctrl_left_click')},
                {'type': 'bullet', 'text': self.loc.t('help_ctrl_select_unit')},
                {'type': 'bullet', 'text': self.loc.t('help_ctrl_buttons')},
                {'type': 'section', 'text': self.loc.t('help_section_keyboard')},
                {'type': 'bullet', 'text': self.loc.t('help_ctrl_arrow_keys')},
                {'type': 'section', 'text': self.loc.t('help_section_indicators')},
                {'type': 'bullet', 'text': self.loc.t('help_indicator_green')},
                {'type': 'bullet', 'text': self.loc.t('help_indicator_red')},
                {'type': 'bullet', 'text': self.loc.t('help_indicator_yellow')},
            ]
        ))
        
        pages.append(HelpPage(
            self.loc.t('help_title_terrain'),
            [
                {'type': 'section', 'text': self.loc.t('help_section_terrain_types')},
                {'type': 'terrain', 'terrain': 'plain', 'name': self.loc.t('plain'), 'desc': self.loc.t('help_terrain_plain')},
                {'type': 'terrain', 'terrain': 'forest', 'name': self.loc.t('forest'), 'desc': self.loc.t('help_terrain_forest')},
                {'type': 'terrain', 'terrain': 'hill', 'name': self.loc.t('hill'), 'desc': self.loc.t('help_terrain_hill')},
                {'type': 'terrain', 'terrain': 'mountain', 'name': self.loc.t('mountain'), 'desc': self.loc.t('help_terrain_mountain')},
                {'type': 'terrain', 'terrain': 'water', 'name': self.loc.t('water'), 'desc': self.loc.t('help_terrain_water')},
            ]
        ))
        
        pages.append(HelpPage(
            self.loc.t('help_title_buildings'),
            [
                {'type': 'section', 'text': self.loc.t('help_section_building_info')},
                {'type': 'text', 'text': self.loc.t('help_text_building_1')},
                {'type': 'building', 'building': 'town', 'name': self.loc.t('town'), 
                 'cost': BUILDING_INFO['town']['cost'], 
                 'prod': BUILDING_INFO['town']['production'],
                 'desc': self.loc.t('help_building_town')},
                {'type': 'building', 'building': 'barracks', 'name': self.loc.t('barracks'), 
                 'cost': BUILDING_INFO['barracks']['cost'], 
                 'prod': BUILDING_INFO['barracks']['production'],
                 'desc': self.loc.t('help_building_barracks')},
                {'type': 'building', 'building': 'farm', 'name': self.loc.t('farm'), 
                 'cost': BUILDING_INFO['farm']['cost'], 
                 'prod': BUILDING_INFO['farm']['production'],
                 'desc': self.loc.t('help_building_farm')},
                {'type': 'building', 'building': 'lumbermill', 'name': self.loc.t('lumbermill'), 
                 'cost': BUILDING_INFO['lumbermill']['cost'], 
                 'prod': BUILDING_INFO['lumbermill']['production'],
                 'desc': self.loc.t('help_building_lumbermill')},
                {'type': 'building', 'building': 'tower', 'name': self.loc.t('tower'), 
                 'cost': BUILDING_INFO['tower']['cost'], 
                 'prod': BUILDING_INFO['tower']['production'],
                 'desc': self.loc.t('help_building_tower')},
            ]
        ))
        
        pages.append(HelpPage(
            self.loc.t('help_title_units'),
            [
                {'type': 'section', 'text': self.loc.t('help_section_unit_info')},
                {'type': 'text', 'text': self.loc.t('help_text_unit_1')},
                {'type': 'text', 'text': self.loc.t('help_text_unit_2')},
                {'type': 'unit', 'unit': 'warrior', 'name': self.loc.t('warrior'), 
                 'stats': UNIT_INFO['warrior'],
                 'desc': self.loc.t('help_unit_warrior')},
                {'type': 'unit', 'unit': 'archer', 'name': self.loc.t('archer'), 
                 'stats': UNIT_INFO['archer'],
                 'desc': self.loc.t('help_unit_archer')},
                {'type': 'section', 'text': self.loc.t('help_section_combat')},
                {'type': 'text', 'text': self.loc.t('help_text_combat_1')},
                {'type': 'text', 'text': self.loc.t('help_text_combat_2')},
                {'type': 'text', 'text': self.loc.t('help_text_combat_3')},
            ]
        ))
        
        pages.append(HelpPage(
            self.loc.t('help_title_strategy'),
            [
                {'type': 'section', 'text': self.loc.t('help_section_tips')},
                {'type': 'bullet', 'text': self.loc.t('help_tip_1')},
                {'type': 'bullet', 'text': self.loc.t('help_tip_2')},
                {'type': 'bullet', 'text': self.loc.t('help_tip_3')},
                {'type': 'bullet', 'text': self.loc.t('help_tip_4')},
                {'type': 'bullet', 'text': self.loc.t('help_tip_5')},
                {'type': 'section', 'text': self.loc.t('help_section_ai')},
                {'type': 'text', 'text': self.loc.t('help_text_ai_1')},
                {'type': 'text', 'text': self.loc.t('help_text_ai_2')},
            ]
        ))
        
        return pages
    
    def set_mouse_state(self, mouse_pos: Tuple[int, int], mouse_down: bool):
        self.mouse_pos = mouse_pos
        self.mouse_down = mouse_down
    
    def handle_scroll(self, delta: int):
        current_page = self.pages[self.current_page_idx]
        scroll_amount = delta * 30
        current_page.scroll_offset = max(0, min(current_page.max_scroll, 
                                                   current_page.scroll_offset + scroll_amount))
    
    def update(self):
        current_time = pygame.time.get_ticks() / 1000.0
        dt = current_time - self.last_time
        self.last_time = current_time
        
        for button in self.buttons:
            button.update(self.mouse_pos, self.mouse_down, dt)
    
    def _draw_hex_preview(self, x: int, y: int, color: Tuple[int, int, int], size: int = 20):
        corners = []
        for i in range(6):
            angle = math.pi / 3 * i
            cx = x + size * math.cos(angle)
            cy = y + size * math.sin(angle)
            corners.append((cx, cy))
        
        pygame.draw.polygon(self.screen, color, corners)
        pygame.draw.polygon(self.screen, (50, 60, 70), corners, 1)
    
    def _draw_page_content(self, page: HelpPage):
        content_area_x = 80
        content_area_y = 120
        content_width = SCREEN_WIDTH - 160
        content_height = SCREEN_HEIGHT - 220
        
        clip_rect = pygame.Rect(content_area_x, content_area_y, content_width, content_height)
        old_clip = self.screen.get_clip()
        self.screen.set_clip(clip_rect)
        
        y_offset = content_area_y - page.scroll_offset
        line_height = 30
        section_spacing = 15
        
        for item in page.content:
            item_type = item.get('type', 'text')
            
            if item_type == 'section':
                y_offset += section_spacing
                try:
                    text_surface = self.font_section.render(item['text'], True, UI_COLORS['menu_title'])
                except Exception:
                    fallback_font = pygame.font.Font(None, 24)
                    text_surface = fallback_font.render(item['text'], True, UI_COLORS['menu_title'])
                self.screen.blit(text_surface, (content_area_x, y_offset))
                y_offset += line_height
            
            elif item_type == 'text':
                try:
                    text_surface = self.font_text.render(item['text'], True, UI_COLORS['help_text'])
                except Exception:
                    fallback_font = pygame.font.Font(None, 20)
                    text_surface = fallback_font.render(item['text'], True, UI_COLORS['help_text'])
                self.screen.blit(text_surface, (content_area_x + 20, y_offset))
                y_offset += line_height
            
            elif item_type == 'bullet':
                bullet_text = f"• {item['text']}"
                try:
                    text_surface = self.font_text.render(bullet_text, True, UI_COLORS['help_text'])
                except Exception:
                    fallback_font = pygame.font.Font(None, 20)
                    text_surface = fallback_font.render(bullet_text, True, UI_COLORS['help_text'])
                self.screen.blit(text_surface, (content_area_x + 30, y_offset))
                y_offset += line_height
            
            elif item_type == 'terrain':
                terrain_color = TERRAIN_COLORS.get(item['terrain'], (150, 150, 150))
                self._draw_hex_preview(content_area_x + 20, y_offset + 15, terrain_color, size=18)
                
                name_text = item['name']
                try:
                    name_surface = self.font_section.render(name_text, True, UI_COLORS['menu_text'])
                except Exception:
                    fallback_font = pygame.font.Font(None, 22)
                    name_surface = fallback_font.render(name_text, True, UI_COLORS['menu_text'])
                self.screen.blit(name_surface, (content_area_x + 60, y_offset))
                
                try:
                    desc_surface = self.font_small.render(item['desc'], True, UI_COLORS['help_text'])
                except Exception:
                    fallback_font = pygame.font.Font(None, 16)
                    desc_surface = fallback_font.render(item['desc'], True, UI_COLORS['help_text'])
                self.screen.blit(desc_surface, (content_area_x + 60, y_offset + 25))
                y_offset += line_height + 15
            
            elif item_type == 'building':
                name_text = item['name']
                try:
                    name_surface = self.font_section.render(name_text, True, UI_COLORS['menu_text'])
                except Exception:
                    fallback_font = pygame.font.Font(None, 22)
                    name_surface = fallback_font.render(name_text, True, UI_COLORS['menu_text'])
                self.screen.blit(name_surface, (content_area_x + 20, y_offset))
                y_offset += 25
                
                cost_text = self.loc.t('help_cost') + ': '
                cost_items = []
                for res, amount in item['cost'].items():
                    if amount > 0:
                        res_name = self.loc.t(res)
                        cost_items.append(f"{res_name}: {amount}")
                cost_text += ', '.join(cost_items)
                
                try:
                    cost_surface = self.font_small.render(cost_text, True, (200, 200, 100))
                except Exception:
                    fallback_font = pygame.font.Font(None, 16)
                    cost_surface = fallback_font.render(cost_text, True, (200, 200, 100))
                self.screen.blit(cost_surface, (content_area_x + 40, y_offset))
                y_offset += 20
                
                if item['prod']:
                    prod_items = []
                    for res, amount in item['prod'].items():
                        if amount > 0:
                            res_name = self.loc.t(res)
                            prod_items.append(f"{res_name} +{amount}")
                    if prod_items:
                        prod_text = self.loc.t('help_production') + ': ' + ', '.join(prod_items)
                        try:
                            prod_surface = self.font_small.render(prod_text, True, (100, 200, 100))
                        except Exception:
                            fallback_font = pygame.font.Font(None, 16)
                            prod_surface = fallback_font.render(prod_text, True, (100, 200, 100))
                        self.screen.blit(prod_surface, (content_area_x + 40, y_offset))
                        y_offset += 20
                
                try:
                    desc_surface = self.font_small.render(item['desc'], True, UI_COLORS['help_text'])
                except Exception:
                    fallback_font = pygame.font.Font(None, 16)
                    desc_surface = fallback_font.render(item['desc'], True, UI_COLORS['help_text'])
                self.screen.blit(desc_surface, (content_area_x + 40, y_offset))
                y_offset += line_height + 5
            
            elif item_type == 'unit':
                name_text = item['name']
                try:
                    name_surface = self.font_section.render(name_text, True, UI_COLORS['menu_text'])
                except Exception:
                    fallback_font = pygame.font.Font(None, 22)
                    name_surface = fallback_font.render(name_text, True, UI_COLORS['menu_text'])
                self.screen.blit(name_surface, (content_area_x + 20, y_offset))
                y_offset += 25
                
                stats = item['stats']
                stats_text = (f"{self.loc.t('help_stat_attack')}: {stats['attack']}  "
                              f"{self.loc.t('help_stat_defense')}: {stats['defense']}  "
                              f"{self.loc.t('help_stat_health')}: {stats['health']}  "
                              f"{self.loc.t('help_stat_movement')}: {stats['movement']}")
                try:
                    stats_surface = self.font_small.render(stats_text, True, (150, 200, 255))
                except Exception:
                    fallback_font = pygame.font.Font(None, 16)
                    stats_surface = fallback_font.render(stats_text, True, (150, 200, 255))
                self.screen.blit(stats_surface, (content_area_x + 40, y_offset))
                y_offset += 20
                
                try:
                    desc_surface = self.font_small.render(item['desc'], True, UI_COLORS['help_text'])
                except Exception:
                    fallback_font = pygame.font.Font(None, 16)
                    desc_surface = fallback_font.render(item['desc'], True, UI_COLORS['help_text'])
                self.screen.blit(desc_surface, (content_area_x + 40, y_offset))
                y_offset += line_height + 5
        
        total_content_height = y_offset - (content_area_y - page.scroll_offset)
        page.max_scroll = max(0, total_content_height - content_height)
        
        self.screen.set_clip(old_clip)
        
        if page.max_scroll > 0:
            scroll_bar_x = SCREEN_WIDTH - 60
            scroll_bar_height = content_height
            scroll_bar_y = content_area_y
            
            thumb_height = max(30, scroll_bar_height * (content_height / (content_height + page.max_scroll)))
            thumb_y = scroll_bar_y + (page.scroll_offset / page.max_scroll) * (scroll_bar_height - thumb_height)
            
            pygame.draw.rect(self.screen, (60, 70, 80), 
                           (scroll_bar_x, scroll_bar_y, 10, scroll_bar_height))
            pygame.draw.rect(self.screen, UI_COLORS['highlight_border'], 
                           (scroll_bar_x, int(thumb_y), 10, int(thumb_height)))
    
    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        current_page = self.pages[self.current_page_idx]
        
        page_title = current_page.title
        try:
            title_surface = self.font_title.render(page_title, True, UI_COLORS['menu_title'])
        except Exception:
            fallback_font = pygame.font.Font(None, 40)
            title_surface = fallback_font.render(page_title, True, UI_COLORS['menu_title'])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 70))
        self.screen.blit(title_surface, title_rect)
        
        page_indicator = f"{self.loc.t('help_page')} {self.current_page_idx + 1} / {len(self.pages)}"
        try:
            page_surface = self.font_small.render(page_indicator, True, UI_COLORS['help_text'])
        except Exception:
            fallback_font = pygame.font.Font(None, 16)
            page_surface = fallback_font.render(page_indicator, True, UI_COLORS['help_text'])
        page_rect = page_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(page_surface, page_rect)
        
        self._draw_page_content(current_page)
        
        for button in self.buttons:
            button.draw(self.screen, self.font_button)
    
    def handle_click(self) -> Optional[str]:
        for button in self.buttons:
            if button.enabled and button.rect.collidepoint(self.mouse_pos):
                action = button.action
                if action == 'prev_page':
                    if self.current_page_idx > 0:
                        self.current_page_idx -= 1
                        self.pages[self.current_page_idx].scroll_offset = 0
                    return None
                elif action == 'next_page':
                    if self.current_page_idx < len(self.pages) - 1:
                        self.current_page_idx += 1
                        self.pages[self.current_page_idx].scroll_offset = 0
                    return None
                return action
        return None
