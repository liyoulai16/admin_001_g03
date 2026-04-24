from typing import Dict, Any

TRANSLATIONS: Dict[str, Dict[str, Any]] = {
    'en': {
        'game_title': 'Turn-based Strategy - Hex Map',
        'game_subtitle': 'A Hex-Based Strategy Game',
        
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
        'river': 'River',
        'lake': 'Lake',
        
        'town': 'Town',
        'barracks': 'Barracks',
        'farm': 'Farm',
        'tower': 'Tower',
        'lumbermill': 'Lumbermill',
        
        'warrior': 'Warrior',
        'archer': 'Archer',
        'builder': 'Builder',
        'cavalry': 'Cavalry',
        'settler': 'Settler',
        
        'tile_info': 'Tile Info',
        'no_tile_selected': 'No tile selected',
        'terrain': 'Terrain',
        'feature': 'Feature',
        'owner': 'Owner',
        'building': 'Building',
        'unit': 'Unit',
        'none': 'None',
        'neutral': 'Neutral',
        'coordinates': 'Coordinates',
        'passable': 'Passable',
        'yes': 'Yes',
        'no': 'No',
        'defense_bonus': 'Defense Bonus',
        'tiles_owned': 'Tiles Owned',
        'river_through': 'River flows through',
        'river_start': 'River starts here',
        'river_end': 'River ends here',
        
        'end_turn': 'End Turn',
        'build': 'Build',
        'train': 'Train Unit',
        'expand_territory': 'Expand Territory',
        'clear_enemy_tile': 'Clear Enemy Tile',
        'destroy_building': 'Destroy Building',
        'found_town': 'Found Town',
        'cancel': 'Cancel',
        'select_building': 'Select Building:',
        'select_unit': 'Select Unit:',
        
        'moved': 'Moved',
        'can_move': 'Can move',
        'attacked': 'Attacked',
        'can_attack': 'Can attack',
        'can_build': 'Can build',
        'status': 'Status',
        'health': 'Health',
        'attack': 'Attack',
        'defense': 'Defense',
        'movement': 'Movement',
        
        'combat_log': 'Combat Log',
        
        'msg_game_start': 'Game started! You are Player 1 (Blue)',
        'msg_captured_enemy_tile': 'captured enemy tile!',
        'msg_cleared_enemy_tile': 'cleared enemy tile, it is now neutral',
        'msg_captured_neutral_tile': 'captured neutral tile',
        'msg_attacked': 'attacked',
        'msg_damage': 'damage',
        'msg_destroyed': 'destroyed!',
        'msg_took': 'took',
        'msg_counter_damage': 'counter damage',
        'msg_can_only_build_own': 'Can only build on your own tiles!',
        'msg_tile_has_building': 'Tile already has a building!',
        'msg_not_enough_resources': 'Not enough resources!',
        'msg_built': 'Built',
        'msg_trained': 'Trained',
        'msg_can_only_train_own': 'Can only train units in your own buildings!',
        'msg_need_barracks': 'Need a barracks to train military units!',
        'msg_need_training_building': 'Need a building that can train units!',
        'msg_cannot_train_this_unit': 'This building cannot train this type of unit!',
        'msg_need_builder': 'Need a builder unit to construct buildings!',
        'msg_tile_has_unit': 'Tile already has a military unit!',
        'msg_tile_has_builder': 'Tile already has a builder!',
        'msg_no_territory_to_expand': 'No adjacent territory to expand!',
        'msg_already_expanded_this_turn': 'Already expanded territory this turn!',
        'msg_already_own_territory': 'Already own this territory!',
        'msg_cannot_expand_impassable': 'Cannot expand to impassable terrain!',
        'msg_no_adjacent_ally_territory': 'No adjacent ally territory!',
        'msg_no_expandable_territory': 'No expandable territory nearby!',
        'msg_cannot_expand_from_own_tile': 'Cannot expand while standing on your own territory!',
        'msg_cannot_clear_with_building': 'Cannot clear tile with enemy building!',
        'msg_cannot_clear_with_builder': 'Cannot clear tile with enemy builder!',
        'msg_destroyed_building': 'destroyed enemy building!',
        'msg_cannot_destroy_own_building': 'Cannot destroy your own building!',
        'msg_no_building_to_destroy': 'No enemy building on this tile!',
        'msg_cannot_settle_here': 'Cannot found town on this tile!',
        'msg_tile_not_neutral': 'Tile is not neutral!',
        'msg_settler_founded_town': 'Settler founded a new town!',
        'msg_tile_impassable': 'Cannot build on impassable terrain!',
        'msg_victory_all_enemies_defeated': 'All enemy units and territories eliminated!',
        'msg_ai_turn': 'AI Turn',
        'msg_new_turn_gained': 'New turn! Gained:',
        'msg_game_over': 'Game over!',
        'msg_wins': 'wins!',
        
        'settings': 'Settings',
        'language': 'Language',
        'language_en': 'English',
        'language_zh': '中文',
        
        'start_game': 'Start Game',
        'game_help': 'Game Help',
        'quit_game': 'Quit Game',
        'back_to_menu': 'Back to Menu',
        'prev_page': 'Previous',
        'next_page': 'Next',
        
        'difficulty': 'Difficulty',
        'difficulty_easy': 'Easy',
        'difficulty_normal': 'Normal',
        'difficulty_hard': 'Hard',
        'select_difficulty': 'Select Difficulty:',
        
        'help_title_welcome': 'Welcome to Hex Strategy',
        'help_title_controls': 'Controls & Interface',
        'help_title_terrain': 'Terrain Types',
        'help_title_buildings': 'Buildings',
        'help_title_units': 'Units & Combat',
        'help_title_strategy': 'Strategy Tips',
        
        'help_section_overview': 'Game Overview',
        'help_text_overview_1': 'Hex Strategy is a turn-based strategy game played on a hexagonal grid.',
        'help_text_overview_2': 'Each player controls units, builds structures, and expands their territory.',
        'help_text_overview_3': 'The goal is to defeat the opponent by capturing all their tiles or destroying all their units.',
        
        'help_section_game_goal': 'How to Win',
        'help_text_goal_1': 'Capture enemy tiles by moving your units onto them.',
        'help_text_goal_2': 'Destroy all enemy units and buildings to win the game.',
        
        'help_section_mouse': 'Mouse Controls',
        'help_ctrl_left_click': 'Left Click - Select tiles, units, and buttons',
        'help_ctrl_select_unit': 'Click your unit to select it, then click a reachable tile to move',
        'help_ctrl_buttons': 'Click buttons in the right panel to take actions',
        
        'help_section_keyboard': 'Keyboard Controls',
        'help_ctrl_arrow_keys': 'Arrow Keys - Scroll the map view',
        
        'help_section_indicators': 'Color Indicators',
        'help_indicator_green': 'Green border - Tile is reachable for movement',
        'help_indicator_red': 'Red border - Tile can be attacked',
        'help_indicator_yellow': 'Yellow border - Currently selected tile',
        
        'help_section_terrain_types': 'Terrain Effects',
        'help_terrain_plain': 'Basic terrain, no special effects',
        'help_terrain_forest': 'May provide defensive bonus',
        'help_terrain_hill': 'Elevated terrain, may affect vision',
        'help_terrain_mountain': 'Impassable - Units cannot move through',
        'help_terrain_water': 'Impassable - Units cannot move through',
        
        'help_section_building_info': 'Building Guide',
        'help_text_building_1': 'Buildings can only be constructed on your own tiles.',
        'help_building_town': 'Core building that produces gold and food each turn',
        'help_building_barracks': 'Military building for training units',
        'help_building_farm': 'Produces food for your civilization',
        'help_building_lumbermill': 'Produces wood for construction',
        'help_building_tower': 'Defensive structure that provides protection',
        
        'help_section_unit_info': 'Unit Guide',
        'help_text_unit_1': 'Units can move and attack each turn.',
        'help_text_unit_2': 'Each unit has movement, attack, defense, and health stats.',
        'help_unit_warrior': 'Melee unit with balanced stats',
        'help_unit_archer': 'Ranged unit with high attack but low defense',
        
        'help_section_combat': 'Combat System',
        'help_text_combat_1': 'When attacking, damage is calculated as: Attack - (Defense / 2)',
        'help_text_combat_2': 'Units can attack adjacent enemy units or buildings.',
        'help_text_combat_3': 'A unit can move and attack in the same turn if it hasn\'t done either yet.',
        
        'help_section_tips': 'Strategy Tips',
        'help_tip_1': 'Expand your territory early to gain more resource income',
        'help_tip_2': 'Build farms and lumbermills to sustain your economy',
        'help_tip_3': 'Protect your units - losing them puts you at a disadvantage',
        'help_tip_4': 'Use terrain to your advantage - position units strategically',
        'help_tip_5': 'Watch the AI\'s movements and anticipate their attacks',
        
        'help_section_ai': 'AI Opponent',
        'help_text_ai_1': 'The AI will try to expand its territory and attack your units.',
        'help_text_ai_2': 'Be prepared for counter-attacks after you make aggressive moves.',
        
        'help_cost': 'Cost',
        'help_production': 'Produces per turn',
        'help_stat_attack': 'ATK',
        'help_stat_defense': 'DEF',
        'help_stat_health': 'HP',
        'help_stat_movement': 'MOV',
        'help_page': 'Page',
    },
    'zh': {
        'game_title': '回合制策略游戏 - 六边形地图',
        'game_subtitle': '六边形策略游戏',
        
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
        'river': '河流',
        'lake': '湖泊',
        
        'town': '城镇',
        'barracks': '兵营',
        'farm': '农场',
        'tower': '防御塔',
        'lumbermill': '伐木场',
        
        'warrior': '战士',
        'archer': '弓箭手',
        'builder': '建造者',
        'cavalry': '骑兵',
        'settler': '开拓者',
        
        'tile_info': '地块信息',
        'no_tile_selected': '未选中地块',
        'terrain': '地形',
        'feature': '特征',
        'owner': '所有者',
        'building': '建筑',
        'unit': '单位',
        'none': '无',
        'neutral': '中立',
        'coordinates': '坐标',
        'passable': '可通行',
        'yes': '是',
        'no': '否',
        'defense_bonus': '防御加成',
        'tiles_owned': '拥有地块数',
        'river_through': '河流穿过',
        'river_start': '河流起点',
        'river_end': '河流终点',
        
        'end_turn': '结束回合',
        'build': '建造建筑',
        'train': '训练单位',
        'expand_territory': '扩充领地',
        'clear_enemy_tile': '清扫敌方地块',
        'destroy_building': '破坏建筑',
        'found_town': '建立城镇',
        'cancel': '取消',
        'select_building': '选择建筑:',
        'select_unit': '选择单位:',
        
        'moved': '已移动',
        'can_move': '可移动',
        'attacked': '已攻击',
        'can_attack': '可攻击',
        'can_build': '可建造',
        'status': '单位状态',
        'health': '生命值',
        'attack': '攻击力',
        'defense': '防御力',
        'movement': '移动力',
        
        'combat_log': '战斗日志',
        
        'msg_game_start': '游戏开始！你是玩家1 (蓝色)',
        'msg_captured_enemy_tile': '占领了敌方地块！',
        'msg_cleared_enemy_tile': '清扫了敌方地块，现在变为中立地块',
        'msg_captured_neutral_tile': '占领了中立地块',
        'msg_attacked': '攻击',
        'msg_damage': '点伤害',
        'msg_destroyed': '被消灭！',
        'msg_took': '受到',
        'msg_counter_damage': '点反击伤害',
        'msg_can_only_build_own': '只能在自己的地块上建造！',
        'msg_tile_has_building': '该地块已有建筑！',
        'msg_not_enough_resources': '资源不足！',
        'msg_built': '建造了',
        'msg_trained': '训练了',
        'msg_can_only_train_own': '只能在自己的建筑中训练单位！',
        'msg_need_barracks': '需要军营才能训练军事单位！',
        'msg_need_training_building': '需要可以训练单位的建筑！',
        'msg_cannot_train_this_unit': '该建筑无法训练此类型的单位！',
        'msg_need_builder': '需要建造者单位才能建造建筑！',
        'msg_tile_has_unit': '该地块已有军队单位！',
        'msg_tile_has_builder': '该地块已有建造者！',
        'msg_no_territory_to_expand': '没有可扩充的相邻领地！',
        'msg_already_expanded_this_turn': '本回合已扩充过领地！',
        'msg_already_own_territory': '已经拥有该领地！',
        'msg_cannot_expand_impassable': '无法扩充到不可通行的地形！',
        'msg_no_adjacent_ally_territory': '没有相邻的友方领地！',
        'msg_no_expandable_territory': '附近没有可扩充的领地！',
        'msg_cannot_expand_from_own_tile': '站在己方领地上时无法扩充！',
        'msg_cannot_clear_with_building': '无法清扫有敌方建筑的地块！',
        'msg_cannot_clear_with_builder': '无法清扫有敌方建造者的地块！',
        'msg_destroyed_building': '摧毁了敌方建筑！',
        'msg_cannot_destroy_own_building': '无法破坏自己的建筑！',
        'msg_no_building_to_destroy': '该地块没有敌方建筑！',
        'msg_cannot_settle_here': '无法在此地块建立城镇！',
        'msg_tile_not_neutral': '该地块不是中立地块！',
        'msg_settler_founded_town': '开拓者建立了新城镇！',
        'msg_tile_impassable': '无法在不可通行的地形上建造！',
        'msg_victory_all_enemies_defeated': '所有敌方单位和领地已被消灭！',
        'msg_ai_turn': 'AI 回合',
        'msg_new_turn_gained': '新回合！获得资源:',
        'msg_game_over': '游戏结束！',
        'msg_wins': '获胜！',
        
        'settings': '设置',
        'language': '语言',
        'language_en': 'English',
        'language_zh': '中文',
        
        'start_game': '开始游戏',
        'game_help': '游戏帮助',
        'quit_game': '退出游戏',
        'back_to_menu': '返回菜单',
        'prev_page': '上一页',
        'next_page': '下一页',
        
        'difficulty': '难度',
        'difficulty_easy': '简单',
        'difficulty_normal': '普通',
        'difficulty_hard': '困难',
        'select_difficulty': '选择难度：',
        
        'help_title_welcome': '欢迎来到六边形策略游戏',
        'help_title_controls': '操作与界面',
        'help_title_terrain': '地形类型',
        'help_title_buildings': '建筑系统',
        'help_title_units': '单位与战斗',
        'help_title_strategy': '策略提示',
        
        'help_section_overview': '游戏简介',
        'help_text_overview_1': '六边形策略游戏是一款在六边形网格上进行的回合制策略游戏。',
        'help_text_overview_2': '每个玩家控制单位、建造建筑、扩展领土。',
        'help_text_overview_3': '游戏目标是通过占领所有敌方地块或消灭所有敌方单位来击败对手。',
        
        'help_section_game_goal': '如何获胜',
        'help_text_goal_1': '通过移动单位到敌方地块上来占领它们。',
        'help_text_goal_2': '消灭所有敌方单位和建筑即可获胜。',
        
        'help_section_mouse': '鼠标操作',
        'help_ctrl_left_click': '左键点击 - 选择地块、单位和按钮',
        'help_ctrl_select_unit': '点击你的单位选中它，然后点击可达地块移动',
        'help_ctrl_buttons': '点击右侧面板的按钮执行操作',
        
        'help_section_keyboard': '键盘操作',
        'help_ctrl_arrow_keys': '方向键 - 滚动地图视图',
        
        'help_section_indicators': '颜色指示',
        'help_indicator_green': '绿色边框 - 该地块可移动到达',
        'help_indicator_red': '红色边框 - 该地块可攻击',
        'help_indicator_yellow': '黄色边框 - 当前选中地块',
        
        'help_section_terrain_types': '地形效果',
        'help_terrain_plain': '基础地形，无特殊效果',
        'help_terrain_forest': '可能提供防御加成',
        'help_terrain_hill': '高地地形，可能影响视野',
        'help_terrain_mountain': '不可通行 - 单位无法穿越',
        'help_terrain_water': '不可通行 - 单位无法穿越',
        
        'help_section_building_info': '建筑指南',
        'help_text_building_1': '建筑只能在自己的地块上建造。',
        'help_building_town': '核心建筑，每回合生产金币和食物',
        'help_building_barracks': '军事建筑，用于训练单位',
        'help_building_farm': '为你的文明生产食物',
        'help_building_lumbermill': '生产木材用于建设',
        'help_building_tower': '防御建筑，提供保护',
        
        'help_section_unit_info': '单位指南',
        'help_text_unit_1': '单位每回合可以移动和攻击。',
        'help_text_unit_2': '每个单位有移动力、攻击力、防御力和生命值属性。',
        'help_unit_warrior': '近战单位，属性均衡',
        'help_unit_archer': '远程单位，高攻击但低防御',
        
        'help_section_combat': '战斗系统',
        'help_text_combat_1': '攻击时，伤害计算为：攻击力 - (防御力 / 2)',
        'help_text_combat_2': '单位可以攻击相邻的敌方单位或建筑。',
        'help_text_combat_3': '如果单位还没有移动或攻击，可以在同一回合内同时进行移动和攻击。',
        
        'help_section_tips': '策略提示',
        'help_tip_1': '尽早扩展领土以获得更多资源收入',
        'help_tip_2': '建造农场和伐木场来维持经济',
        'help_tip_3': '保护好你的单位 - 损失单位会让你处于劣势',
        'help_tip_4': '善用地形 - 战略性地布置单位',
        'help_tip_5': '观察AI的动向，预判它们的攻击',
        
        'help_section_ai': 'AI对手',
        'help_text_ai_1': 'AI会尝试扩展领土并攻击你的单位。',
        'help_text_ai_2': '在你采取激进行动后，要准备好应对反击。',
        
        'help_cost': '消耗',
        'help_production': '每回合产出',
        'help_stat_attack': '攻击',
        'help_stat_defense': '防御',
        'help_stat_health': '生命',
        'help_stat_movement': '移动',
        'help_page': '页',
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
    
    def get_feature_name(self, feature: str) -> str:
        if feature == 'none':
            return self.t('none')
        return self.t(feature)
    
    def get_resource_icon(self, resource_type: str) -> str:
        icons = {
            'gold': 'G',
            'wood': 'W',
            'food': 'F',
        }
        return icons.get(resource_type, resource_type)
