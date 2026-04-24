from typing import Dict, List, Tuple, Optional
import random
from hex_map import HexMap
from player import Player, Unit, Building
from config import BUILDING_INFO, UNIT_INFO


class SimpleAI:
    def __init__(self, player: Player):
        self.player = player
    
    def take_turn(self, hex_map: HexMap) -> Dict[str, str]:
        actions = []
        
        income = self.player.calculate_income()
        self.player.add_resources(income)
        
        build_action = self._try_build(hex_map)
        if build_action:
            actions.append(build_action)
        
        recruit_action = self._try_recruit(hex_map)
        if recruit_action:
            actions.append(recruit_action)
        
        move_actions = self._move_units(hex_map)
        actions.extend(move_actions)
        
        attack_actions = self._attack_enemies(hex_map)
        actions.extend(attack_actions)
        
        return {'actions': str(actions)}
    
    def _try_build(self, hex_map: HexMap) -> Optional[str]:
        owned_tiles = []
        for (q, r), tile in hex_map.tiles.items():
            if tile.owner == self.player and not tile.building:
                if tile.terrain not in ['mountain', 'water']:
                    owned_tiles.append((q, r, tile))
        
        if not owned_tiles:
            return None
        
        build_priority = ['town', 'farm', 'lumbermill', 'barracks', 'tower']
        
        for building_type in build_priority:
            if building_type not in BUILDING_INFO:
                continue
            
            cost = BUILDING_INFO[building_type]['cost']
            if self.player.can_afford(cost):
                if building_type == 'town':
                    existing_towns = [b for b in self.player.buildings if b.building_type == 'town']
                    if len(existing_towns) >= 3:
                        continue
                
                if building_type == 'barracks':
                    existing_barracks = [b for b in self.player.buildings if b.building_type == 'barracks']
                    if len(existing_barracks) >= 2:
                        continue
                
                for q, r, tile in owned_tiles:
                    if self.player.spend_resources(cost):
                        building = Building(building_type, q, r, self.player)
                        tile.building = building
                        self.player.add_building(building)
                        return f"建造了{BUILDING_INFO[building_type]['name']}"
        
        return None
    
    def _try_recruit(self, hex_map: HexMap) -> Optional[str]:
        barracks = [b for b in self.player.buildings if b.building_type == 'barracks']
        if not barracks:
            return None
        
        if len(self.player.units) >= 8:
            return None
        
        for unit_type in ['warrior', 'archer']:
            if unit_type not in UNIT_INFO:
                continue
            
            cost = UNIT_INFO[unit_type]['cost']
            if self.player.can_afford(cost):
                for barrack in barracks:
                    tile = hex_map.get_tile(barrack.tile_q, barrack.tile_r)
                    if tile and not tile.unit:
                        if self.player.spend_resources(cost):
                            unit = Unit(unit_type, barrack.tile_q, barrack.tile_r, self.player)
                            tile.unit = unit
                            self.player.add_unit(unit)
                            return f"训练了{UNIT_INFO[unit_type]['name']}"
        
        return None
    
    def _move_units(self, hex_map: HexMap) -> List[str]:
        actions = []
        
        for unit in self.player.units[:]:
            if unit.moved_this_turn:
                continue
            
            current_tile = hex_map.get_tile(unit.tile_q, unit.tile_r)
            if not current_tile:
                continue
            
            neighbors = hex_map.get_neighbors(unit.tile_q, unit.tile_r)
            reachable_tiles = []
            
            for nq, nr in neighbors:
                if unit.can_move_to(hex_map, nq, nr):
                    target_tile = hex_map.get_tile(nq, nr)
                    if target_tile:
                        dist_to_enemy = self._distance_to_enemy_owned(hex_map, nq, nr)
                        reachable_tiles.append((nq, nr, target_tile, dist_to_enemy))
            
            if reachable_tiles:
                reachable_tiles.sort(key=lambda x: (x[3], x[2].owner is not None and x[2].owner != self.player))
                best = reachable_tiles[0]
                
                target_tile = best[2]
                current_tile.unit = None
                unit.tile_q = best[0]
                unit.tile_r = best[1]
                target_tile.unit = unit
                unit.moved_this_turn = True
                
                if target_tile.owner is not None and target_tile.owner != self.player:
                    if not unit.can_build:
                        target_tile.owner.tiles_owned -= 1
                        target_tile.owner = None
                        actions.append(f"清扫了敌方地块({best[0]}, {best[1]})，变为中立")
                    else:
                        actions.append(f"移动了单位到({best[0]}, {best[1]})")
                elif target_tile.owner is None and unit.can_build:
                    has_adjacent_ally = False
                    neighbors = hex_map.get_neighbors(target_tile.q, target_tile.r)
                    for nq, nr in neighbors:
                        neighbor_tile = hex_map.get_tile(nq, nr)
                        if neighbor_tile and neighbor_tile.owner == self.player:
                            has_adjacent_ally = True
                            break
                    if has_adjacent_ally:
                        target_tile.owner = self.player
                        self.player.tiles_owned += 1
                        actions.append(f"扩充了领地到地块({best[0]}, {best[1]})")
                    else:
                        actions.append(f"移动了单位到({best[0]}, {best[1]})")
                else:
                    actions.append(f"移动了单位到({best[0]}, {best[1]})")
        
        return actions
    
    def _attack_enemies(self, hex_map: HexMap) -> List[str]:
        actions = []
        
        for unit in self.player.units[:]:
            if unit.attacked_this_turn:
                continue
            
            neighbors = hex_map.get_neighbors(unit.tile_q, unit.tile_r)
            for nq, nr in neighbors:
                if unit.can_attack(hex_map, nq, nr):
                    target_tile = hex_map.get_tile(nq, nr)
                    if target_tile:
                        if target_tile.unit and target_tile.unit.owner != self.player:
                            target = target_tile.unit
                            damage = max(1, unit.attack - target.defense // 2)
                            target.health -= damage
                            
                            if target.health <= 0:
                                target.owner.remove_unit(target)
                                target_tile.unit = None
                                actions.append(f"消灭了敌方{target.name}")
                            else:
                                actions.append(f"攻击了敌方{target.name}，造成{damage}点伤害")
                            
                            unit.attacked_this_turn = True
                            break
                        
                        elif target_tile.building and target_tile.building.owner != self.player:
                            target = target_tile.building
                            damage = max(1, unit.attack - 5)
                            target.health -= damage
                            
                            if target.health <= 0:
                                target.owner.remove_building(target)
                                target_tile.building = None
                                actions.append(f"摧毁了敌方{target.name}")
                            else:
                                actions.append(f"攻击了敌方{target.name}，造成{damage}点伤害")
                            
                            unit.attacked_this_turn = True
                            break
        
        return actions
    
    def _distance_to_enemy_owned(self, hex_map: HexMap, q: int, r: int) -> int:
        min_distance = 999
        
        for (eq, er), tile in hex_map.tiles.items():
            if tile.owner and tile.owner != self.player:
                dist = hex_map.hex_distance(q, r, eq, er)
                min_distance = min(min_distance, dist)
        
        return min_distance
