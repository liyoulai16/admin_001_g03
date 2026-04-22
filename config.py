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

TERRAIN_COLORS = {
    'plain': (150, 180, 100),
    'forest': (50, 120, 50),
    'mountain': (150, 140, 130),
    'water': (60, 140, 200),
    'hill': (120, 150, 90),
}

TERRAIN_NAMES = {
    'plain': 'Plain',
    'forest': 'Forest',
    'mountain': 'Mountain',
    'water': 'Water',
    'hill': 'Hill',
}

BUILDING_INFO = {
    'town': {
        'name': 'Town',
        'cost': {'gold': 100, 'wood': 50},
        'production': {'gold': 10, 'wood': 0, 'food': 5},
        'description': 'Produces gold and food per turn',
    },
    'barracks': {
        'name': 'Barracks',
        'cost': {'gold': 80, 'wood': 60},
        'production': {'gold': 0, 'wood': 0, 'food': 0},
        'description': 'Allows training units',
    },
    'farm': {
        'name': 'Farm',
        'cost': {'gold': 50, 'wood': 30},
        'production': {'gold': 0, 'wood': 0, 'food': 10},
        'description': 'Produces food per turn',
    },
    'tower': {
        'name': 'Tower',
        'cost': {'gold': 60, 'wood': 40},
        'production': {'gold': 0, 'wood': 0, 'food': 0},
        'description': 'Provides defense bonus',
    },
    'lumbermill': {
        'name': 'Lumbermill',
        'cost': {'gold': 40, 'wood': 20},
        'production': {'gold': 0, 'wood': 8, 'food': 0},
        'description': 'Produces wood per turn',
    },
}

UNIT_INFO = {
    'warrior': {
        'name': 'Warrior',
        'cost': {'gold': 30, 'wood': 10, 'food': 20},
        'attack': 10,
        'defense': 8,
        'health': 100,
        'movement': 2,
    },
    'archer': {
        'name': 'Archer',
        'cost': {'gold': 25, 'wood': 20, 'food': 15},
        'attack': 12,
        'defense': 5,
        'health': 70,
        'movement': 3,
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
    'unit_move': 0.3,
    'unit_attack': 0.4,
    'tile_select': 0.2,
    'button_click': 0.15,
    'menu_transition': 0.3,
}

BUTTON_ANIMATION = {
    'hover_scale': 1.05,
    'click_scale': 0.95,
    'hover_color_shift': 20,
    'click_color_shift': 30,
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
    'PLAYING': 'playing',
    'PAUSED': 'paused',
    'GAME_OVER': 'game_over',
}
