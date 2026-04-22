import math
from typing import Tuple, List, Dict, Optional
from config import HEX_SIZE, TERRAIN_COLORS, SELECTED_COLOR, HIGHLIGHT_COLOR


class HexTile:
    def __init__(self, q: int, r: int, terrain: str = 'plain'):
        self.q = q
        self.r = r
        self.terrain = terrain
        self.owner = None
        self.building = None
        self.unit = None
        self.selected = False
        self.highlighted = False
        self.reachable = False
        self.attackable = False

    def get_color(self):
        base_color = TERRAIN_COLORS.get(self.terrain, (150, 150, 150))
        
        if self.owner is not None:
            owner_color = self.owner.color
            r = (base_color[0] + owner_color[0]) // 2
            g = (base_color[1] + owner_color[1]) // 2
            b = (base_color[2] + owner_color[2]) // 2
            base_color = (r, g, b)
        
        return base_color

    def get_border_color(self):
        if self.selected:
            return SELECTED_COLOR
        elif self.attackable:
            return (255, 50, 50)
        elif self.reachable:
            return (100, 255, 100)
        elif self.highlighted:
            return HIGHLIGHT_COLOR
        return (50, 60, 70)


class HexMap:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.tiles: Dict[Tuple[int, int], HexTile] = {}
        
    def add_tile(self, q: int, r: int, terrain: str = 'plain') -> HexTile:
        tile = HexTile(q, r, terrain)
        self.tiles[(q, r)] = tile
        return tile

    def get_tile(self, q: int, r: int) -> Optional[HexTile]:
        return self.tiles.get((q, r))

    def hex_to_pixel(self, q: int, r: int) -> Tuple[float, float]:
        x = HEX_SIZE * (3/2 * q)
        y = HEX_SIZE * (math.sqrt(3)/2 * q + math.sqrt(3) * r)
        return x, y

    def pixel_to_hex(self, x: float, y: float) -> Tuple[int, int]:
        q = (2/3 * x) / HEX_SIZE
        r = (-1/3 * x + math.sqrt(3)/3 * y) / HEX_SIZE
        return self.hex_round(q, r)

    def hex_round(self, q: float, r: float) -> Tuple[int, int]:
        s = -q - r
        rq = round(q)
        rr = round(r)
        rs = round(s)
        
        q_diff = abs(rq - q)
        r_diff = abs(rr - r)
        s_diff = abs(rs - s)
        
        if q_diff > r_diff and q_diff > s_diff:
            rq = -rr - rs
        elif r_diff > s_diff:
            rr = -rq - rs
        
        return rq, rr

    def get_hex_corners(self, center_x: float, center_y: float) -> List[Tuple[float, float]]:
        corners = []
        for i in range(6):
            angle = math.pi / 3 * i
            x = center_x + HEX_SIZE * math.cos(angle)
            y = center_y + HEX_SIZE * math.sin(angle)
            corners.append((x, y))
        return corners

    def get_neighbors(self, q: int, r: int) -> List[Tuple[int, int]]:
        directions = [
            (1, 0), (1, -1), (0, -1),
            (-1, 0), (-1, 1), (0, 1)
        ]
        neighbors = []
        for dq, dr in directions:
            nq, nr = q + dq, r + dr
            if (nq, nr) in self.tiles:
                neighbors.append((nq, nr))
        return neighbors

    def get_tiles_in_range(self, q: int, r: int, range_val: int) -> List[Tuple[int, int]]:
        results = []
        for dq in range(-range_val, range_val + 1):
            for dr in range(max(-range_val, -dq - range_val), min(range_val + 1, -dq + range_val + 1)):
                if dq == 0 and dr == 0:
                    continue
                nq, nr = q + dq, r + dr
                if (nq, nr) in self.tiles:
                    results.append((nq, nr))
        return results

    def hex_distance(self, q1: int, r1: int, q2: int, r2: int) -> int:
        return (abs(q1 - q2) + abs(q1 + r1 - q2 - r2) + abs(r1 - r2)) // 2

    def clear_highlights(self):
        for tile in self.tiles.values():
            tile.selected = False
            tile.highlighted = False
            tile.reachable = False
            tile.attackable = False
