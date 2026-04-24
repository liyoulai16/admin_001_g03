import random
from typing import List, Tuple, Dict, Optional
from hex_map import HexMap
from config import TERRAIN_TYPES, FEATURE_TYPES, HEX_DIRECTIONS


class TerrainGenerator:
    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
    
    def generate_random_map(self, hex_map: HexMap, rows: int, cols: int) -> HexMap:
        terrain_types = ['plain', 'hill', 'mountain', 'lake']
        terrain_weights = [45, 25, 20, 10]
        
        for q in range(cols):
            offset = q // 2
            for r in range(-offset, rows - offset):
                terrain = random.choices(terrain_types, weights=terrain_weights, k=1)[0]
                
                feature = 'none'
                if terrain in ['plain', 'hill']:
                    if random.random() < 0.25:
                        feature = 'forest'
                
                hex_map.add_tile(q, r, terrain, feature)
        
        self.smooth_terrain(hex_map)
        
        self.generate_river_networks(hex_map, num_rivers=2)
        
        self.ensure_passable_start_areas(hex_map)
        
        return hex_map
    
    def generate_river_networks(self, hex_map: HexMap, num_rivers: int = 2):
        all_tiles = list(hex_map.tiles.keys())
        if not all_tiles:
            return
        
        min_q = min(q for q, r in all_tiles)
        max_q = max(q for q, r in all_tiles)
        min_r = min(r for q, r in all_tiles)
        max_r = max(r for q, r in all_tiles)
        
        for _ in range(num_rivers):
            start_edge = random.choice(['left', 'right', 'top', 'bottom'])
            
            start_tile = None
            if start_edge == 'left':
                candidates = [(min_q, r) for q, r in all_tiles if q == min_q]
                if candidates:
                    start_tile = random.choice(candidates)
            elif start_edge == 'right':
                candidates = [(max_q, r) for q, r in all_tiles if q == max_q]
                if candidates:
                    start_tile = random.choice(candidates)
            elif start_edge == 'top':
                candidates = [(q, min_r) for q, r in all_tiles if r == min_r]
                if candidates:
                    start_tile = random.choice(candidates)
            elif start_edge == 'bottom':
                candidates = [(q, max_r) for q, r in all_tiles if r == max_r]
                if candidates:
                    start_tile = random.choice(candidates)
            
            if not start_tile:
                continue
            
            river_length = random.randint(8, 15)
            self._create_river_path(hex_map, start_tile[0], start_tile[1], river_length)
    
    def _create_river_path(self, hex_map: HexMap, start_q: int, start_r: int, length: int):
        current_q, current_r = start_q, start_r
        prev_direction = None
        
        river_tiles = []
        
        for i in range(length):
            tile = hex_map.get_tile(current_q, current_r)
            if not tile:
                break
            
            if tile.terrain not in ['mountain', 'lake'] and tile.feature != 'river':
                tile.feature = 'river'
                river_tiles.append((current_q, current_r))
            
            neighbors = hex_map.get_neighbors(current_q, current_r)
            valid_directions = []
            
            for d_idx, (dq, dr) in enumerate(HEX_DIRECTIONS):
                nq, nr = current_q + dq, current_r + dr
                if (nq, nr) in hex_map.tiles:
                    neighbor = hex_map.get_tile(nq, nr)
                    if neighbor and neighbor.terrain not in ['mountain', 'lake']:
                        valid_directions.append(d_idx)
            
            if not valid_directions:
                break
            
            if prev_direction is not None:
                opposite_dir = (prev_direction + 3) % 6
                if opposite_dir in valid_directions and len(valid_directions) > 1:
                    valid_directions.remove(opposite_dir)
            
            if prev_direction is not None:
                preferred_dirs = [
                    (prev_direction - 1) % 6,
                    prev_direction,
                    (prev_direction + 1) % 6
                ]
                available_preferred = [d for d in preferred_dirs if d in valid_directions]
                
                if available_preferred:
                    weights = [0.3, 0.5, 0.3]
                    next_dir = random.choices(available_preferred, 
                                              weights=weights[:len(available_preferred)], k=1)[0]
                else:
                    next_dir = random.choice(valid_directions)
            else:
                next_dir = random.choice(valid_directions)
            
            dq, dr = HEX_DIRECTIONS[next_dir]
            current_q += dq
            current_r += dr
            prev_direction = next_dir
        
        self._set_river_directions(hex_map, river_tiles)
    
    def _set_river_directions(self, hex_map: HexMap, river_tiles: List[Tuple[int, int]]):
        for i, (q, r) in enumerate(river_tiles):
            tile = hex_map.get_tile(q, r)
            if not tile:
                continue
            
            if i > 0:
                prev_q, prev_r = river_tiles[i-1]
                for d_idx, (dq, dr) in enumerate(HEX_DIRECTIONS):
                    if q + dq == prev_q and r + dr == prev_r:
                        tile.river_from = d_idx
                        break
            
            if i < len(river_tiles) - 1:
                next_q, next_r = river_tiles[i+1]
                for d_idx, (dq, dr) in enumerate(HEX_DIRECTIONS):
                    if q + dq == next_q and r + dr == next_r:
                        tile.river_to = d_idx
                        break
    
    def smooth_terrain(self, hex_map: HexMap, iterations: int = 3):
        for _ in range(iterations):
            changes = {}
            
            for (q, r), tile in hex_map.tiles.items():
                neighbors = hex_map.get_neighbors(q, r)
                terrain_counts = {}
                
                for nq, nr in neighbors:
                    neighbor = hex_map.get_tile(nq, nr)
                    if neighbor:
                        t = neighbor.terrain
                        terrain_counts[t] = terrain_counts.get(t, 0) + 1
                
                if terrain_counts:
                    max_count = max(terrain_counts.values())
                    majority_terrains = [t for t, c in terrain_counts.items() if c == max_count]
                    
                    if max_count >= 4 and tile.terrain not in majority_terrains:
                        changes[(q, r)] = random.choice(majority_terrains)
            
            for (q, r), new_terrain in changes.items():
                tile = hex_map.get_tile(q, r)
                if tile:
                    if tile.feature != 'river':
                        tile.terrain = new_terrain
                        if new_terrain in ['plain', 'hill']:
                            if random.random() < 0.25:
                                tile.feature = 'forest'
                            else:
                                tile.feature = 'none'
                        else:
                            tile.feature = 'none'
    
    def ensure_passable_start_areas(self, hex_map: HexMap):
        passable_terrains = ['plain', 'hill']
        unpassable_terrains = ['mountain', 'lake']
        
        corners = [
            (0, 0),
            (max(q for q, r in hex_map.tiles.keys()), max(r for q, r in hex_map.tiles.keys())),
            (0, min(r for q, r in hex_map.tiles.keys())),
            (max(q for q, r in hex_map.tiles.keys()), min(r for q, r in hex_map.tiles.keys())),
        ]
        
        for center_q, center_r in corners:
            for i in range(3):
                for dq in range(-i, i + 1):
                    for dr in range(max(-i, -dq - i), min(i + 1, -dq + i + 1)):
                        q = center_q + dq
                        r = center_r + dr
                        tile = hex_map.get_tile(q, r)
                        if tile and (tile.terrain in unpassable_terrains or tile.feature == 'river'):
                            tile.terrain = random.choice(passable_terrains)
                            tile.feature = 'none'
                            tile.river_from = None
                            tile.river_to = None
    
    def get_start_positions(self, hex_map: HexMap, num_players: int = 2) -> List[Tuple[int, int]]:
        all_tiles = list(hex_map.tiles.keys())
        if not all_tiles:
            return []
        
        min_q = min(q for q, r in all_tiles)
        max_q = max(q for q, r in all_tiles)
        min_r = min(r for q, r in all_tiles)
        max_r = max(r for q, r in all_tiles)
        
        positions = []
        
        corners = [
            (min_q + 2, min_r + 2),
            (max_q - 2, max_r - 2),
            (min_q + 2, max_r - 2),
            (max_q - 2, min_r + 2),
        ]
        
        unpassable_terrains = ['mountain', 'lake']
        
        for q, r in corners[:num_players]:
            if (q, r) in hex_map.tiles:
                tile = hex_map.get_tile(q, r)
                if tile and tile.terrain not in unpassable_terrains and tile.feature != 'river':
                    positions.append((q, r))
                else:
                    for neighbor_q, neighbor_r in hex_map.get_neighbors(q, r):
                        neighbor = hex_map.get_tile(neighbor_q, neighbor_r)
                        if neighbor and neighbor.terrain not in unpassable_terrains and neighbor.feature != 'river':
                            positions.append((neighbor_q, neighbor_r))
                            break
        
        while len(positions) < num_players:
            q, r = random.choice(all_tiles)
            tile = hex_map.get_tile(q, r)
            if tile and tile.terrain not in unpassable_terrains and tile.feature != 'river':
                positions.append((q, r))
        
        return positions[:num_players]
