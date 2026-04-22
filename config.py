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
    'plain': '平原',
    'forest': '森林',
    'mountain': '山脉',
    'water': '水域',
    'hill': '丘陵',
}

BUILDING_INFO = {
    'town': {
        'name': '城镇',
        'cost': {'gold': 100, 'wood': 50},
        'production': {'gold': 10, 'wood': 0, 'food': 5},
        'description': '每回合产出金币和食物',
    },
    'barracks': {
        'name': '兵营',
        'cost': {'gold': 80, 'wood': 60},
        'production': {'gold': 0, 'wood': 0, 'food': 0},
        'description': '允许训练军队',
    },
    'farm': {
        'name': '农场',
        'cost': {'gold': 50, 'wood': 30},
        'production': {'gold': 0, 'wood': 0, 'food': 10},
        'description': '每回合产出食物',
    },
    'tower': {
        'name': '防御塔',
        'cost': {'gold': 60, 'wood': 40},
        'production': {'gold': 0, 'wood': 0, 'food': 0},
        'description': '提供防御加成',
    },
    'lumbermill': {
        'name': '伐木场',
        'cost': {'gold': 40, 'wood': 20},
        'production': {'gold': 0, 'wood': 8, 'food': 0},
        'description': '每回合产出木材',
    },
}

UNIT_INFO = {
    'warrior': {
        'name': '战士',
        'cost': {'gold': 30, 'wood': 10, 'food': 20},
        'attack': 10,
        'defense': 8,
        'health': 100,
        'movement': 2,
    },
    'archer': {
        'name': '弓箭手',
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
    'gold': '💰',
    'wood': '🪵',
    'food': '🍖',
}

RESOURCE_NAMES = {
    'gold': '金币',
    'wood': '木材',
    'food': '食物',
}
