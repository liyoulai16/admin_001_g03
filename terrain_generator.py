import random
from typing import List, Tuple
from hex_map import HexMap
from config import TERRAIN_TYPES, FEATURE_TYPES


class TerrainGenerator:
    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
    
    def generate_random_map(self, hex_map: HexMap, rows: int, cols: int) -> HexMap:
        terrain_types = ['plain', 'hill', 'mountain', 'river', 'lake']
        terrain_weights = [40, 20, 15, 15, 10]
        
        for q in range(cols):
            offset = q // 2
            for r in range(-offset, rows - offset):
                terrain = random.choices(terrain_types, weights=terrain_weights, k=1)[0]
                
                feature = 'none'
                if terrain in ['plain', 'hill']:
                    if random.random() < 0.3:
                        feature = 'forest'
                
                hex_map.add_tile(q, r, terrain, feature)
        
        self.smooth_terrain(hex_map)
        self.ensure_passable_start_areas(hex_map)
        
        return hex_map
    
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
                    tile.terrain = new_terrain
                    if new_terrain in ['plain', 'hill']:
                        if random.random() < 0.3:
                            tile.feature = 'forest'
                        else:
                            tile.feature = 'none'
                    else:
                        tile.feature = 'none'
    
    def ensure_passable_start_areas(self, hex_map: HexMap):
        passable_terrains = ['plain', 'hill']
        unpassable_terrains = ['mountain', 'river', 'lake']
        
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
                        if tile and tile.terrain in unpassable_terrains:
                            tile.terrain = random.choice(passable_terrains)
                            tile.feature = 'none'
    
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
        
        unpassable = ['mountain', 'river', 'lake']
        
        for q, r in corners[:num_players]:
            if (q, r) in hex_map.tiles:
                tile = hex_map.get_tile(q, r)
                if tile and tile.terrain not in unpassable:
                    positions.append((q, r))
                else:
                    for neighbor_q, neighbor_r in hex_map.get_neighbors(q, r):
                        neighbor = hex_map.get_tile(neighbor_q, neighbor_r)
                        if neighbor and neighbor.terrain not in unpassable:
                            positions.append((neighbor_q, neighbor_r))
                            break
        
        while len(positions) < num_players:
            q, r = random.choice(all_tiles)
            tile = hex_map.get_tile(q, r)
            if tile and tile.terrain not in unpassable:
                positions.append((q, r))
        
        return positions[:num_players]
