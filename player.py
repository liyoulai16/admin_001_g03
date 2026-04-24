from typing import Dict, Any, Optional
from config import PLAYER_START_RESOURCES, AI_START_RESOURCES, BUILDING_INFO, UNIT_INFO, TERRAIN_TYPES


class Player:
    def __init__(self, player_id: int, is_ai: bool = False, color: tuple = None):
        self.player_id = player_id
        self.is_ai = is_ai
        self.resources: Dict[str, int] = {}
        self.color = color if color else self._get_default_color(player_id)
        self.tiles_owned = 0
        self.buildings = []
        self.units = []
        self.name = f"Player {player_id}" if not is_ai else f"AI {player_id}"
        
        self._init_resources(is_ai)
    
    def _get_default_color(self, player_id: int) -> tuple:
        colors = [
            (80, 120, 200),
            (200, 80, 80),
            (80, 200, 120),
            (200, 180, 80),
        ]
        return colors[(player_id - 1) % len(colors)]
    
    def _init_resources(self, is_ai: bool):
        start_res = AI_START_RESOURCES if is_ai else PLAYER_START_RESOURCES
        self.resources = start_res.copy()
    
    def add_resources(self, resources: Dict[str, int]):
        for res_type, amount in resources.items():
            self.resources[res_type] = self.resources.get(res_type, 0) + amount
    
    def spend_resources(self, cost: Dict[str, int]) -> bool:
        for res_type, amount in cost.items():
            if self.resources.get(res_type, 0) < amount:
                return False
        
        for res_type, amount in cost.items():
            self.resources[res_type] -= amount
        
        return True
    
    def can_afford(self, cost: Dict[str, int]) -> bool:
        for res_type, amount in cost.items():
            if self.resources.get(res_type, 0) < amount:
                return False
        return True
    
    def calculate_income(self) -> Dict[str, int]:
        income = {'gold': 0, 'wood': 0, 'food': 0}
        base_income = 5
        
        income['gold'] += base_income
        
        for building in self.buildings:
            if building.building_type in BUILDING_INFO:
                prod = BUILDING_INFO[building.building_type]['production']
                for res_type, amount in prod.items():
                    income[res_type] += amount
        
        return income
    
    def add_building(self, building):
        self.buildings.append(building)
        self.tiles_owned += 1
    
    def add_unit(self, unit):
        self.units.append(unit)
    
    def remove_unit(self, unit):
        if unit in self.units:
            self.units.remove(unit)
    
    def remove_building(self, building):
        if building in self.buildings:
            self.buildings.remove(building)
            self.tiles_owned -= 1


class Building:
    def __init__(self, building_type: str, tile_q: int, tile_r: int, owner: Player):
        self.building_type = building_type
        self.tile_q = tile_q
        self.tile_r = tile_r
        self.owner = owner
        self.health = 100
        self.max_health = 100
        
        if building_type in BUILDING_INFO:
            self.name = BUILDING_INFO[building_type]['name']
        else:
            self.name = building_type


class Unit:
    def __init__(self, unit_type: str, tile_q: int, tile_r: int, owner: Player):
        self.unit_type = unit_type
        self.tile_q = tile_q
        self.tile_r = tile_r
        self.owner = owner
        self.moved_this_turn = False
        self.attacked_this_turn = False
        self.expanded_territory_this_turn = False
        
        if unit_type in UNIT_INFO:
            info = UNIT_INFO[unit_type]
            self.name = info['name']
            self.attack = info['attack']
            self.defense = info['defense']
            self.health = info['health']
            self.max_health = info['health']
            self.movement = info['movement']
            self.can_build = info.get('can_build', False)
            self.can_expand_territory = info.get('can_expand_territory', False)
        else:
            self.name = unit_type
            self.attack = 10
            self.defense = 5
            self.health = 100
            self.max_health = 100
            self.movement = 2
            self.can_build = False
            self.can_expand_territory = False
    
    def reset_for_new_turn(self):
        self.moved_this_turn = False
        self.attacked_this_turn = False
        self.expanded_territory_this_turn = False
    
    def can_move_to(self, hex_map, target_q: int, target_r: int) -> bool:
        if self.moved_this_turn:
            return False
        
        target_tile = hex_map.get_tile(target_q, target_r)
        if not target_tile:
            return False
        
        terrain_info = TERRAIN_TYPES.get(target_tile.terrain, {})
        if not terrain_info.get('passable', True):
            return False
        
        distance = hex_map.hex_distance(self.tile_q, self.tile_r, target_q, target_r)
        if distance > self.movement:
            return False
        
        if self.can_build:
            if target_tile.builder_unit:
                return False
        else:
            if target_tile.unit and target_tile.unit.owner == self.owner:
                return False
            if target_tile.unit and target_tile.unit.owner != self.owner:
                return False
        
        return True
    
    def can_attack(self, hex_map, target_q: int, target_r: int) -> bool:
        if self.attacked_this_turn:
            return False
        
        target_tile = hex_map.get_tile(target_q, target_r)
        if not target_tile:
            return False
        
        distance = hex_map.hex_distance(self.tile_q, self.tile_r, target_q, target_r)
        if distance > 1:
            return False
        
        if target_tile.unit and target_tile.unit.owner == self.owner:
            return False
        
        if target_tile.builder_unit and target_tile.builder_unit.owner == self.owner:
            return False
        
        if target_tile.building and target_tile.building.owner == self.owner:
            return False
        
        if not target_tile.unit and not target_tile.builder_unit and not target_tile.building and target_tile.owner != self.owner:
            return True
        
        if target_tile.unit and target_tile.unit.owner != self.owner:
            return True
        
        if target_tile.builder_unit and target_tile.builder_unit.owner != self.owner:
            return True
        
        if target_tile.building and target_tile.building.owner != self.owner:
            return True
        
        return False
