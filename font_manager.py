import pygame
import os
import sys
from typing import Dict, Optional, Tuple, List
from config import (
    UI_PANEL_COLOR, TEXT_COLOR, HIGHLIGHT_COLOR, SELECTED_COLOR,
    BUILDING_INFO
)
from player import Player, Building, Unit
from hex_map import HexMap, HexTile
from localization import Localization


class FontManager:
    def __init__(self):
        self.chinese_fonts_available = False
        self._chinese_font_name = None
        self._chinese_font_path = None
        self._font_search_paths = self._get_font_search_paths()
        self._check_chinese_fonts()
        self._test_chinese_rendering()
    
    def _get_font_search_paths(self) -> List[str]:
        paths = []
        
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        fonts_dir = os.path.join(base_path, 'fonts')
        paths.append(fonts_dir)
        
        paths.append(base_path)
        
        return paths
    
    def _find_chinese_font_files(self) -> List[str]:
        font_files = []
        
        font_extensions = ['.ttf', '.otf', '.ttc', '.OTF', '.TTF', '.TTC']
        
        chinese_font_keywords = [
            'chinese',
            'simhei',
            'simhei',
            'msyh',
            'yahei',
            'simsun',
            'simsun',
            'noto',
            'notosans',
            'wenquanyi',
            'wqy',
            'sourcehansans',
            'sourcehanserif',
            'pingfang',
            'hiragino',
        ]
        
        for search_path in self._font_search_paths:
            if not os.path.exists(search_path):
                continue
            
            try:
                for filename in os.listdir(search_path):
                    filepath = os.path.join(search_path, filename)
                    
                    if os.path.isfile(filepath):
                        ext = os.path.splitext(filename)[1].lower()
                        if ext in ['.ttf', '.otf', '.ttc']:
                            filename_lower = filename.lower()
                            
                            for keyword in chinese_font_keywords:
                                if keyword in filename_lower:
                                    if filepath not in font_files:
                                        font_files.append(filepath)
                                    break
            except Exception as e:
                continue
        
        return font_files
    
    def _check_chinese_fonts(self) -> bool:
        chinese_font_files = self._find_chinese_font_files()
        
        for font_path in chinese_font_files:
            try:
                font = pygame.font.Font(font_path, 24)
                if font:
                    if self._test_font_renders_chinese(font):
                        self.chinese_fonts_available = True
                        self._chinese_font_path = font_path
                        self._chinese_font_name = os.path.basename(font_path)
                        return True
            except Exception as e:
                continue
        
        chinese_font_names = [
            'simhei',
            'SimHei',
            'msyh',
            'Microsoft YaHei',
            'simsun',
            'SimSun',
            'microsoftyahei',
            'mingliu',
            'MingLiU',
            'notosanscjksc',
            'Source Han Sans SC',
            'WenQuanYi Micro Hei',
            'wqy-microhei',
        ]
        
        for font_name in chinese_font_names:
            try:
                font = pygame.font.SysFont(font_name, 24)
                if font:
                    if self._test_font_renders_chinese(font):
                        self.chinese_fonts_available = True
                        self._chinese_font_name = font_name
                        return True
            except Exception as e:
                continue
        
        return False
    
    def _test_font_renders_chinese(self, font) -> bool:
        try:
            test_texts = ["中文", "测试", "中国", "游戏"]
            
            for test_text in test_texts:
                surface = font.render(test_text, True, (255, 255, 255))
                width, height = surface.get_size()
                
                if width < 10 or height < 10:
                    return False
                
                min_expected_width = len(test_text) * 12
                if width < min_expected_width:
                    return False
            
            return True
        except:
            return False
    
    def _test_chinese_rendering(self) -> bool:
        if not self.chinese_fonts_available:
            try:
                default_font = pygame.font.Font(None, 24)
                test_text = "中文"
                surface = default_font.render(test_text, True, (255, 255, 255))
                width, height = surface.get_size()
                
                if width > 20 and height > 10:
                    if width >= 24:
                        self.chinese_fonts_available = True
                        return True
            except:
                pass
        
        return self.chinese_fonts_available
    
    def get_font(self, size: int, language: str = 'en'):
        if language == 'zh' and self.chinese_fonts_available:
            if self._chinese_font_path:
                try:
                    font = pygame.font.Font(self._chinese_font_path, size)
                    if font:
                        return font
                except:
                    pass
            
            if self._chinese_font_name:
                try:
                    font = pygame.font.SysFont(self._chinese_font_name, size)
                    if font:
                        return font
                except:
                    pass
            
            chinese_font_names = [
                'simhei',
                'msyh',
                'simsun',
                'microsoftyahei',
            ]
            
            for font_name in chinese_font_names:
                try:
                    font = pygame.font.SysFont(font_name, size)
                    if font:
                        return font
                except:
                    continue
        
        return pygame.font.Font(None, size)
    
    def is_chinese_available(self) -> bool:
        return self.chinese_fonts_available
    
    def get_chinese_font_info(self) -> Dict:
        return {
            'available': self.chinese_fonts_available,
            'font_name': self._chinese_font_name,
            'font_path': self._chinese_font_path,
            'search_paths': self._font_search_paths,
        }
    
    def try_load_font_file(self, font_path: str) -> bool:
        try:
            font = pygame.font.Font(font_path, 24)
            if font and self._test_font_renders_chinese(font):
                self._chinese_font_path = font_path
                self._chinese_font_name = os.path.basename(font_path)
                self.chinese_fonts_available = True
                return True
        except:
            pass
        return False
