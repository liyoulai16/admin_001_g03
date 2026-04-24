import pygame

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

HEX_SIZE = 35
MAP_ROWS = 15
MAP_COLS = 20

BACKGROUND_COLOR = (20, 30, 40)
UI_PANEL_COLOR = (40, 50, 60)
TEXT_COLOR = (220, 220, 220)
HIGHLIGHT_COLOR = (100, 200, 255)
SELECTED_COLOR = (255, 200, 100)

TERRAIN_TYPES = {
    'plain': {
        'name': 'Plain',
        'color': (120, 200, 80),
        'passable': True,
    },
    'hill': {
        'name': 'Hill',
        'color': (100, 170, 60),
        'passable': True,
    },
    'mountain': {
        'name': 'Mountain',
        'color': (160, 150, 140),
        'passable': False,
    },
    'lake': {
        'name': 'Lake',
        'color': (60, 150, 220),
        'passable': False,
    },
}

RIVER_COLORS = {
    'water': (80, 160, 230),
    'dark_water': (50, 120, 190),
    'light_water': (120, 200, 255),
    'foam': (240, 250, 255),
}

HEX_DIRECTIONS = [
    (1, 0),
    (1, -1),
    (0, -1),
    (-1, 0),
    (-1, 1),
    (0, 1),
]

FEATURE_TYPES = {
    'forest': {
        'name': 'Forest',
        'color': (30, 140, 30),
    },
    'river': {
        'name': 'River',
        'color': (80, 160, 230),
    },
    'none': {
        'name': 'None',
        'color': None,
    },
}

TERRAIN_COLORS = {
    'plain': (120, 200, 80),
    'forest': (30, 140, 30),
    'mountain': (160, 150, 140),
    'water': (80, 160, 230),
    'hill': (100, 170, 60),
    'river': (80, 160, 230),
    'lake': (60, 150, 220),
}

TERRAIN_DECORATION_COLORS = {
    'plain': {
        'grass_dark': (100, 180, 60),
        'grass_light': (150, 220, 100),
        'flower': (255, 240, 80),
    },
    'forest': {
        'tree_dark': (20, 100, 20),
        'tree_light': (60, 160, 60),
        'trunk': (120, 80, 40),
        'foliage': (40, 150, 40),
    },
    'mountain': {
        'rock_dark': (80, 70, 60),
        'rock_light': (200, 190, 180),
        'snow': (255, 255, 255),
    },
    'water': {
        'wave_dark': (30, 100, 160),
        'wave_light': (120, 200, 255),
        'foam': (240, 250, 255),
    },
    'hill': {
        'grass_dark': (80, 150, 50),
        'grass_light': (120, 190, 90),
        'rock': (140, 130, 120),
    },
    'lake': {
        'wave_dark': (30, 90, 150),
        'wave_light': (80, 170, 240),
        'foam': (220, 240, 255),
    },
}

BUILDING_DETAIL_COLORS = {
    'town': {
        'roof': (200, 100, 80),
        'wall': (180, 160, 140),
        'door': (100, 60, 40),
        'window': (255, 255, 200),
    },
    'barracks': {
        'wall': (120, 100, 80),
        'roof': (180, 120, 60),
        'flag': (200, 50, 50),
        'pole': (80, 60, 40),
        'window': (255, 255, 200),
    },
    'farm': {
        'field_dark': (60, 120, 40),
        'field_light': (100, 160, 80),
        'crop': (255, 220, 50),
        'barn': (180, 140, 100),
    },
    'tower': {
        'stone_dark': (100, 100, 100),
        'stone_light': (140, 140, 140),
        'crenellation': (80, 120, 200),
        'window': (80, 80, 150),
    },
    'lumbermill': {
        'wood_dark': (101, 67, 33),
        'wood_light': (139, 90, 43),
        'roof': (80, 50, 30),
        'log': (101, 67, 33),
    },
}

UNIT_DETAIL_COLORS = {
    'warrior': {
        'armor': (80, 120, 200),
        'helmet': (100, 100, 120),
        'sword': (200, 200, 200),
        'hilt': (180, 140, 80),
    },
    'archer': {
        'body': (100, 150, 100),
        'hood': (80, 120, 80),
        'bow': (139, 90, 43),
        'arrow': (200, 200, 200),
    },
    'builder': {
        'body': (150, 120, 80),
        'hat': (180, 140, 100),
        'hammer': (150, 150, 150),
        'handle': (101, 67, 33),
    },
    'cavalry': {
        'body': (120, 80, 150),
        'helmet': (100, 80, 120),
        'horse': (139, 90, 43),
        'sword': (200, 200, 200),
        'saddle': (80, 60, 40),
    },
    'settler': {
        'body': (140, 110, 90),
        'hat': (200, 180, 140),
        'flag': (80, 120, 200),
        'pack': (160, 140, 120),
    },
}

TERRAIN_NAMES = {
    'plain': 'Plain',
    'forest': 'Forest',
    'mountain': 'Mountain',
    'water': 'Water',
    'hill': 'Hill',
    'lake': 'Lake',
}

FEATURE_NAMES = {
    'forest': 'Forest',
    'river': 'River',
    'none': 'None',
}

BUILDING_INFO = {
    'town': {
        'name': 'Town',
        'cost': {'gold': 100, 'wood': 50},
        'production': {'gold': 10, 'wood': 0, 'food': 5},
        'description': 'Produces gold and food per turn',
        'can_train': ['builder', 'settler'],
    },
    'barracks': {
        'name': 'Barracks',
        'cost': {'gold': 80, 'wood': 60},
        'production': {'gold': 0, 'wood': 0, 'food': 0},
        'description': 'Allows training military units',
        'can_train': ['warrior', 'archer', 'cavalry'],
    },
    'farm': {
        'name': 'Farm',
        'cost': {'gold': 50, 'wood': 30},
        'production': {'gold': 0, 'wood': 0, 'food': 10},
        'description': 'Produces food per turn',
        'can_train': [],
    },
    'tower': {
        'name': 'Tower',
        'cost': {'gold': 60, 'wood': 40},
        'production': {'gold': 0, 'wood': 0, 'food': 0},
        'description': 'Provides defense bonus',
        'can_train': [],
    },
    'lumbermill': {
        'name': 'Lumbermill',
        'cost': {'gold': 40, 'wood': 20},
        'production': {'gold': 0, 'wood': 8, 'food': 0},
        'description': 'Produces wood per turn',
        'can_train': [],
        'required_feature': ['forest'],
    },
}

UNIT_INFO = {
    'warrior': {
        'name': 'Warrior',
        'cost': {'gold': 30, 'wood': 10, 'food': 20},
        'attack': 20,
        'defense': 8,
        'health': 100,
        'movement': 2,
        'can_build': False,
        'is_melee': True,
    },
    'archer': {
        'name': 'Archer',
        'cost': {'gold': 25, 'wood': 20, 'food': 15},
        'attack': 24,
        'defense': 5,
        'health': 70,
        'movement': 3,
        'can_build': False,
        'is_melee': False,
    },
    'builder': {
        'name': 'Builder',
        'cost': {'gold': 20, 'wood': 15, 'food': 10},
        'attack': 4,
        'defense': 3,
        'health': 50,
        'movement': 2,
        'can_build': True,
        'can_expand_territory': True,
        'is_melee': True,
    },
    'cavalry': {
        'name': 'Cavalry',
        'cost': {'gold': 40, 'wood': 15, 'food': 30},
        'attack': 16,
        'defense': 6,
        'health': 80,
        'movement': 4,
        'can_build': False,
        'is_melee': True,
    },
    'settler': {
        'name': 'Settler',
        'cost': {'gold': 50, 'wood': 40, 'food': 30},
        'attack': 2,
        'defense': 2,
        'health': 40,
        'movement': 2,
        'can_build': False,
        'can_settle': True,
        'is_melee': True,
    },
}

PLAYER_START_RESOURCES = {
    'gold': 200,
    'wood': 150,
    'food': 100,
}

AI_START_RESOURCES = {
    'gold': 200,
    'wood': 150,
    'food': 100,
}

EXPAND_TERRITORY_COST = {
    'gold': 20,
    'wood': 10,
    'food': 10,
}

RESOURCE_ICONS = {
    'gold': 'G',
    'wood': 'W',
    'food': 'F',
}

RESOURCE_NAMES = {
    'gold': 'Gold',
    'wood': 'Wood',
    'food': 'Food',
}

ANIMATION_DURATION = {
    'unit_move': 0.6,
    'unit_attack': 0.5,
    'tile_select': 0.3,
    'button_click': 0.2,
    'menu_transition': 0.4,
}

BUTTON_ANIMATION = {
    'hover_scale': 1.05,
    'click_scale': 0.90,
    'hover_color_shift': 20,
    'click_color_shift': 40,
    'click_release_speed': 4.0,
    'menu_expand_duration': 0.3,
}

UI_COLORS = {
    'menu_background': (30, 40, 50),
    'menu_title': (220, 200, 100),
    'menu_text': (200, 200, 200),
    'menu_button_normal': (80, 100, 120),
    'menu_button_hover': (100, 120, 140),
    'menu_button_click': (60, 80, 100),
    'help_text': (180, 180, 180),
    'highlight_border': (100, 200, 255),
}

GAME_STATES = {
    'MENU': 'menu',
    'HELP': 'help',
    'SETTINGS': 'settings',
    'DIFFICULTY': 'difficulty',
    'PLAYING': 'playing',
    'PAUSED': 'paused',
    'GAME_OVER': 'game_over',
}

ZOOM_CONFIG = {
    'min_zoom': 0.5,
    'max_zoom': 2.0,
    'zoom_step': 0.1,
    'default_zoom': 1.0,
}

EDGE_SCROLL_CONFIG = {
    'scroll_speed': 5,
    'edge_threshold': 50,
}
