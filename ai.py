from typing import Dict, List, Tuple, Optional
import random
from hex_map import HexMap
from player import Player, Unit, Building
from config import BUILDING_INFO, UNIT_INFO


class Difficulty:
    EASY = 'easy'
    NORMAL = 'normal'
    HARD = 'hard'


class SimpleAI:
    def __init__(self, player: Player, difficulty: str = Difficulty.NORMAL):
        self.player = player
        self.difficulty = difficulty
        self._configure_difficulty()
    
    def _configure_difficulty(self):
        if self.difficulty == Difficulty.EASY:
            self.build_chance = 0.4
            self.recruit_chance = 0.3
            self.attack_chance = 0.4
            self.max_units = 4
            self.max_towns = 2
            self.max_barracks = 1
            self.unit_priority = ['warrior']
            self.building_priority = ['farm', 'lumbermill', 'barracks', 'town', 'tower']
            self.attack_preference = 'weakest'
            self.move_aggressiveness = 0.3
            
        elif self.difficulty == Difficulty.HARD:
            self.build_chance = 0.9
            self.recruit_chance = 0.8
            self.attack_chance = 0.9
            self.max_units = 12
            self.max_towns = 4
            self.max_barracks = 3
            self.unit_priority = ['cavalry', 'archer', 'warrior']
            self.building_priority = ['barracks', 'town', 'farm', 'lumbermill', 'tower']
            self.attack_preference = 'strategic'
            self.move_aggressiveness = 0.9
            
        else:
            self.build_chance = 0.6
            self.recruit_chance = 0.5
            self.attack_chance = 0.6
            self.max_units = 8
            self.max_towns = 3
            self.max_barracks = 2
            self.unit_priority = ['warrior', 'archer']
            self.building_priority = ['town', 'farm', 'lumbermill', 'barracks', 'tower']
            self.attack_preference = 'nearest'
            self.move_aggressiveness = 0.6
    
    def take_turn(self, hex_map: HexMap) -> Dict[str, str]:
        actions = []
        
        income = self.player.calculate_income()
        if self.difficulty == Difficulty.HARD:
            income = {k: int(v * 1.3) for k, v in income.items()}
        elif self.difficulty == Difficulty.EASY:
            income = {k: int(v * 0.7) for k, v in income.items()}
        
        self.player.add_resources(income)
        
        if random.random() < self.build_chance:
            build_action = self._try_build(hex_map)
            if build_action:
                actions.append(build_action)
        
        if random.random() < self.recruit_chance:
            recruit_action = self._try_recruit(hex_map)
            if recruit_action:
                actions.append(recruit_action)
        
        move_actions = self._move_units(hex_map)
        actions.extend(move_actions)
        
        if random.random() < self.attack_chance:
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
        
        for building_type in self.building_priority:
            if building_type not in BUILDING_INFO:
                continue
            
            cost = BUILDING_INFO[building_type]['cost']
            if self.difficulty == Difficulty.HARD:
                cost = {k: int(v * 0.8) for k, v in cost.items()}
            elif self.difficulty == Difficulty.EASY:
                cost = {k: int(v * 1.2) for k, v in cost.items()}
            
            if self.player.can_afford(cost):
                if building_type == 'town':
                    existing_towns = [b for b in self.player.buildings if b.building_type == 'town']
                    if len(existing_towns) >= self.max_towns:
                        continue
                
                if building_type == 'barracks':
                    existing_barracks = [b for b in self.player.buildings if b.building_type == 'barracks']
                    if len(existing_barracks) >= self.max_barracks:
                        continue
                
                best_tile = self._select_best_build_tile(owned_tiles, hex_map, building_type)
                if best_tile:
                    q, r, tile = best_tile
                    if self.player.spend_resources(cost):
                        building = Building(building_type, q, r, self.player)
                        tile.building = building
                        self.player.add_building(building)
                        return f"建造了{BUILDING_INFO[building_type]['name']}"
        
        return None
    
    def _select_best_build_tile(self, owned_tiles: List[Tuple], hex_map: HexMap, building_type: str) -> Optional[Tuple]:
        if not owned_tiles:
            return None
        
        if self.difficulty == Difficulty.HARD:
            enemy_tiles = []
            for (eq, er), tile in hex_map.tiles.items():
                if tile.owner and tile.owner != self.player:
                    enemy_tiles.append((eq, er))
            
            if enemy_tiles:
                owned_tiles_with_dist = []
                for q, r, tile in owned_tiles:
                    min_dist = min([hex_map.hex_distance(q, r, eq, er) for eq, er in enemy_tiles])
                    owned_tiles_with_dist.append((q, r, tile, min_dist))
                
                if building_type in ['barracks', 'tower']:
                    owned_tiles_with_dist.sort(key=lambda x: x[3])
                else:
                    owned_tiles_with_dist.sort(key=lambda x: -x[3])
                
                return (owned_tiles_with_dist[0][0], owned_tiles_with_dist[0][1], owned_tiles_with_dist[0][2])
        
        return random.choice(owned_tiles)
    
    def _try_recruit(self, hex_map: HexMap) -> Optional[str]:
        barracks = [b for b in self.player.buildings if b.building_type == 'barracks']
        if not barracks:
            return None
        
        if len(self.player.units) >= self.max_units:
            return None
        
        for unit_type in self.unit_priority:
            if unit_type not in UNIT_INFO:
                continue
            
            cost = UNIT_INFO[unit_type]['cost']
            if self.difficulty == Difficulty.HARD:
                cost = {k: int(v * 0.8) for k, v in cost.items()}
            elif self.difficulty == Difficulty.EASY:
                cost = {k: int(v * 1.2) for k, v in cost.items()}
            
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
            
            if unit.can_build or unit.can_settle:
                if self.difficulty == Difficulty.EASY and random.random() > 0.5:
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
                if self.difficulty == Difficulty.HARD:
                    reachable_tiles = self._rank_tiles_for_movement(reachable_tiles, unit, hex_map)
                elif self.difficulty == Difficulty.EASY:
                    if random.random() > self.move_aggressiveness:
                        random.shuffle(reachable_tiles)
                    else:
                        reachable_tiles.sort(key=lambda x: x[3])
                else:
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
    
    def _rank_tiles_for_movement(self, reachable_tiles: List[Tuple], unit: Unit, hex_map: HexMap) -> List[Tuple]:
        ranked = []
        
        for tile_info in reachable_tiles:
            nq, nr, target_tile, dist_to_enemy = tile_info
            score = 0
            
            if target_tile.owner and target_tile.owner != self.player:
                if not unit.can_build and not target_tile.building:
                    score += 100
            
            if target_tile.owner is None and unit.can_build:
                neighbors = hex_map.get_neighbors(nq, nr)
                for nq2, nr2 in neighbors:
                    neighbor_tile = hex_map.get_tile(nq2, nr2)
                    if neighbor_tile and neighbor_tile.owner == self.player:
                        score += 50
            
            if target_tile.building and target_tile.building.owner != self.player:
                if not unit.can_build:
                    score += 80
            
            score += (100 - dist_to_enemy * 10)
            
            ranked.append((nq, nr, target_tile, dist_to_enemy, score))
        
        ranked.sort(key=lambda x: -x[4])
        return [(r[0], r[1], r[2], r[3]) for r in ranked]
    
    def _attack_enemies(self, hex_map: HexMap) -> List[str]:
        actions = []
        
        attackable_units = [u for u in self.player.units[:] if not u.attacked_this_turn]
        
        if self.difficulty == Difficulty.HARD:
            attackable_units = self._prioritize_attackers(attackable_units)
        
        for unit in attackable_units:
            if unit.attacked_this_turn:
                continue
            
            neighbors = hex_map.get_neighbors(unit.tile_q, unit.tile_r)
            potential_targets = []
            
            for nq, nr in neighbors:
                if unit.can_attack(hex_map, nq, nr):
                    target_tile = hex_map.get_tile(nq, nr)
                    if target_tile:
                        if target_tile.unit and target_tile.unit.owner != self.player:
                            potential_targets.append(('unit', nq, nr, target_tile, target_tile.unit))
                        elif target_tile.building and target_tile.building.owner != self.player:
                            potential_targets.append(('building', nq, nr, target_tile, target_tile.building))
            
            if potential_targets:
                best_target = self._select_best_target(potential_targets, unit)
                
                if best_target:
                    target_type, nq, nr, target_tile, target = best_target
                    
                    if target_type == 'unit':
                        damage = max(1, unit.attack - target.defense // 2)
                        if self.difficulty == Difficulty.HARD:
                            damage = int(damage * 1.2)
                        elif self.difficulty == Difficulty.EASY:
                            damage = int(damage * 0.8)
                        
                        target.health -= damage
                        
                        if unit.is_melee and target.health > 0:
                            counter_damage = max(1, (target.attack // 3) - unit.defense // 4)
                            unit.health -= counter_damage
                            
                            if unit.health <= 0:
                                unit.owner.remove_unit(unit)
                                source_tile = hex_map.get_tile(unit.tile_q, unit.tile_r)
                                if source_tile:
                                    if unit.can_build:
                                        source_tile.builder_unit = None
                                    elif unit.can_settle:
                                        source_tile.settler_unit = None
                                    else:
                                        source_tile.unit = None
                        
                        if target.health <= 0:
                            target.owner.remove_unit(target)
                            target_tile.unit = None
                            actions.append(f"消灭了敌方{target.name}")
                        else:
                            actions.append(f"攻击了敌方{target.name}，造成{damage}点伤害")
                        
                        unit.attacked_this_turn = True
                    
                    elif target_type == 'building':
                        damage = max(1, unit.attack - 5)
                        if self.difficulty == Difficulty.HARD:
                            damage = int(damage * 1.2)
                        elif self.difficulty == Difficulty.EASY:
                            damage = int(damage * 0.8)
                        
                        target.health -= damage
                        
                        if target.health <= 0:
                            target.owner.remove_building(target)
                            target_tile.building = None
                            actions.append(f"摧毁了敌方{target.name}")
                        else:
                            actions.append(f"攻击了敌方{target.name}，造成{damage}点伤害")
                        
                        unit.attacked_this_turn = True
        
        return actions
    
    def _prioritize_attackers(self, units: List[Unit]) -> List[Unit]:
        def get_attack_score(unit: Unit) -> int:
            score = 0
            score += unit.attack * 10
            score += (100 - unit.defense) * 2
            
            if unit.is_melee:
                score -= 5
            
            return score
        
        return sorted(units, key=get_attack_score, reverse=True)
    
    def _select_best_target(self, targets: List[Tuple], attacker: Unit) -> Optional[Tuple]:
        if not targets:
            return None
        
        if self.attack_preference == 'weakest':
            def get_target_score(target_info: Tuple) -> int:
                target_type, nq, nr, target_tile, target = target_info
                if target_type == 'unit':
                    return target.health + target.defense * 2
                else:
                    return target.health * 2
            
            targets.sort(key=get_target_score)
            return targets[0]
        
        elif self.attack_preference == 'strategic':
            def get_target_score(target_info: Tuple) -> int:
                target_type, nq, nr, target_tile, target = target_info
                score = 0
                
                if target_type == 'building':
                    if target.building_type == 'town':
                        score += 200
                    elif target.building_type == 'barracks':
                        score += 150
                    else:
                        score += 100
                else:
                    score += (100 - target.health)
                    score += target.attack * 5
                
                return score
            
            targets.sort(key=lambda x: get_target_score(x), reverse=True)
            return targets[0]
        
        else:
            return targets[0]
    
    def _distance_to_enemy_owned(self, hex_map: HexMap, q: int, r: int) -> int:
        min_distance = 999
        
        for (eq, er), tile in hex_map.tiles.items():
            if tile.owner and tile.owner != self.player:
                dist = hex_map.hex_distance(q, r, eq, er)
                min_distance = min(min_distance, dist)
        
        return min_distance
