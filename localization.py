from typing import Dict, Any

TRANSLATIONS: Dict[str, Dict[str, Any]] = {
    'en': {
        'game_title': 'Turn-based Strategy - Hex Map',
        
        'turn': 'Turn',
        'current_player': 'Current',
        
        'player': 'Player',
        'ai': 'AI',
        
        'gold': 'Gold',
        'wood': 'Wood',
        'food': 'Food',
        
        'plain': 'Plain',
        'forest': 'Forest',
        'mountain': 'Mountain',
        'water': 'Water',
        'hill': 'Hill',
        
        'town': 'Town',
        'barracks': 'Barracks',
        'farm': 'Farm',
        'tower': 'Tower',
        'lumbermill': 'Lumbermill',
        
        'warrior': 'Warrior',
        'archer': 'Archer',
        
        'tile_info': 'Tile Info',
        'no_tile_selected': 'No tile selected',
        'terrain': 'Terrain',
        'owner': 'Owner',
        'building': 'Building',
        'unit': 'Unit',
        'none': 'None',
        
        'end_turn': 'End Turn',
        'build': 'Build',
        'cancel': 'Cancel',
        'select_building': 'Select Building:',
        
        'moved': 'Moved',
        'can_move': 'Can move',
        'attacked': 'Attacked',
        'can_attack': 'Can attack',
        'status': 'Status',
        
        'combat_log': 'Combat Log',
        
        'msg_game_start': 'Game started! You are Player 1 (Blue)',
        'msg_captured_enemy_tile': 'captured enemy tile!',
        'msg_captured_neutral_tile': 'captured neutral tile',
        'msg_attacked': 'attacked',
        'msg_damage': 'damage',
        'msg_destroyed': 'destroyed!',
        'msg_can_only_build_own': 'Can only build on your own tiles!',
        'msg_tile_has_building': 'Tile already has a building!',
        'msg_not_enough_resources': 'Not enough resources!',
        'msg_built': 'Built',
        'msg_ai_turn': 'AI Turn',
        'msg_new_turn_gained': 'New turn! Gained:',
        'msg_game_over': 'Game over!',
        'msg_wins': 'wins!',
        
        'settings': 'Settings',
        'language': 'Language',
        'language_en': 'English',
        'language_zh': '中文',
    },
    'zh': {
        'game_title': '回合制策略游戏 - 六边形地图',
        
        'turn': '回合',
        'current_player': '当前',
        
        'player': '玩家',
        'ai': 'AI',
        
        'gold': '金币',
        'wood': '木材',
        'food': '食物',
        
        'plain': '平原',
        'forest': '森林',
        'mountain': '山脉',
        'water': '水域',
        'hill': '丘陵',
        
        'town': '城镇',
        'barracks': '兵营',
        'farm': '农场',
        'tower': '防御塔',
        'lumbermill': '伐木场',
        
        'warrior': '战士',
        'archer': '弓箭手',
        
        'tile_info': '地块信息',
        'no_tile_selected': '未选中地块',
        'terrain': '地形',
        'owner': '所有者',
        'building': '建筑',
        'unit': '单位',
        'none': '无',
        
        'end_turn': '结束回合',
        'build': '建造建筑',
        'cancel': '取消',
        'select_building': '选择建筑:',
        
        'moved': '已移动',
        'can_move': '可移动',
        'attacked': '已攻击',
        'can_attack': '可攻击',
        'status': '单位状态',
        
        'combat_log': '战斗日志',
        
        'msg_game_start': '游戏开始！你是玩家1 (蓝色)',
        'msg_captured_enemy_tile': '占领了敌方地块！',
        'msg_captured_neutral_tile': '占领了中立地块',
        'msg_attacked': '攻击',
        'msg_damage': '点伤害',
        'msg_destroyed': '被消灭！',
        'msg_can_only_build_own': '只能在自己的地块上建造！',
        'msg_tile_has_building': '该地块已有建筑！',
        'msg_not_enough_resources': '资源不足！',
        'msg_built': '建造了',
        'msg_ai_turn': 'AI 回合',
        'msg_new_turn_gained': '新回合！获得资源:',
        'msg_game_over': '游戏结束！',
        'msg_wins': '获胜！',
        
        'settings': '设置',
        'language': '语言',
        'language_en': 'English',
        'language_zh': '中文',
    }
}


class Localization:
    def __init__(self, language: str = 'en'):
        self.language = language
        self.fallback_language = 'en'
    
    def set_language(self, language: str):
        if language in TRANSLATIONS:
            self.language = language
    
    def get_language(self) -> str:
        return self.language
    
    def get_available_languages(self) -> list:
        return list(TRANSLATIONS.keys())
    
    def t(self, key: str) -> str:
        if key in TRANSLATIONS.get(self.language, {}):
            return TRANSLATIONS[self.language][key]
        
        if key in TRANSLATIONS.get(self.fallback_language, {}):
            return TRANSLATIONS[self.fallback_language][key]
        
        return key
    
    def get_terrain_name(self, terrain: str) -> str:
        return self.t(terrain)
    
    def get_building_name(self, building_type: str) -> str:
        return self.t(building_type)
    
    def get_unit_name(self, unit_type: str) -> str:
        return self.t(unit_type)
    
    def get_resource_name(self, resource_type: str) -> str:
        return self.t(resource_type)
    
    def get_resource_icon(self, resource_type: str) -> str:
        icons = {
            'gold': 'G',
            'wood': 'W',
            'food': 'F',
        }
        return icons.get(resource_type, resource_type)
