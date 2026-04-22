import pygame
import math
from typing import Dict, List, Optional, Callable, Any, Tuple
from config import ANIMATION_DURATION, BUTTON_ANIMATION


class Easing:
    @staticmethod
    def linear(t: float) -> float:
        return t
    
    @staticmethod
    def ease_in(t: float) -> float:
        return t * t
    
    @staticmethod
    def ease_out(t: float) -> float:
        return 1 - (1 - t) * (1 - t)
    
    @staticmethod
    def ease_in_out(t: float) -> float:
        if t < 0.5:
            return 2 * t * t
        return 1 - math.pow(-2 * t + 2, 2) / 2
    
    @staticmethod
    def bounce(t: float) -> float:
        n1 = 7.5625
        d1 = 2.75
        if t < 1 / d1:
            return n1 * t * t
        elif t < 2 / d1:
            t -= 1.5 / d1
            return n1 * t * t + 0.75
        elif t < 2.5 / d1:
            t -= 2.25 / d1
            return n1 * t * t + 0.9375
        else:
            t -= 2.625 / d1
            return n1 * t * t + 0.984375


class Animation:
    def __init__(self, duration: float, easing: Callable[[float], float] = Easing.ease_in_out):
        self.duration = duration
        self.easing = easing
        self.start_time = None
        self.progress = 0.0
        self.is_finished = False
        self.is_paused = False
    
    def start(self, current_time: float):
        self.start_time = current_time
        self.progress = 0.0
        self.is_finished = False
        self.is_paused = False
    
    def update(self, current_time: float) -> float:
        if self.is_finished or self.is_paused or self.start_time is None:
            return self.progress
        
        elapsed = current_time - self.start_time
        self.progress = min(elapsed / self.duration, 1.0)
        
        if self.progress >= 1.0:
            self.is_finished = True
        
        return self.easing(self.progress)
    
    def pause(self):
        self.is_paused = True
    
    def resume(self, current_time: float):
        if self.is_paused:
            self.start_time = current_time - (self.progress * self.duration)
            self.is_paused = False


class UnitMoveAnimation(Animation):
    def __init__(self, start_pos: Tuple[float, float], end_pos: Tuple[float, float], duration: float = None):
        if duration is None:
            duration = ANIMATION_DURATION['unit_move']
        super().__init__(duration, Easing.ease_in_out)
        self.start_x, self.start_y = start_pos
        self.end_x, self.end_y = end_pos
        self.current_x, self.current_y = start_pos
    
    def update(self, current_time: float) -> Tuple[float, float]:
        progress = super().update(current_time)
        self.current_x = self.start_x + (self.end_x - self.start_x) * progress
        self.current_y = self.start_y + (self.end_y - self.start_y) * progress
        return (self.current_x, self.current_y)


class UnitAttackAnimation(Animation):
    def __init__(self, start_pos: Tuple[float, float], target_pos: Tuple[float, float], duration: float = None):
        if duration is None:
            duration = ANIMATION_DURATION['unit_attack']
        super().__init__(duration, Easing.ease_out)
        self.start_x, self.start_y = start_pos
        self.target_x, self.target_y = target_pos
        self.current_x, self.current_y = start_pos
        self.shake_offset = (0, 0)
    
    def update(self, current_time: float) -> Tuple[float, float, Tuple[float, float]]:
        progress = super().update(current_time)
        
        mid_progress = min(progress * 2, 1.0)
        if progress <= 0.5:
            self.current_x = self.start_x + (self.target_x - self.start_x) * mid_progress * 0.8
            self.current_y = self.start_y + (self.target_y - self.start_y) * mid_progress * 0.8
        else:
            self.current_x = self.target_x + (self.start_x - self.target_x) * (mid_progress - 0.5) * 2
            self.current_y = self.target_y + (self.start_y - self.target_y) * (mid_progress - 0.5) * 2
        
        if progress > 0.6 and progress < 0.8:
            shake_progress = (progress - 0.6) / 0.2
            shake_amount = 5 * math.sin(shake_progress * math.pi * 4)
            self.shake_offset = (shake_amount, shake_amount * 0.5)
        else:
            self.shake_offset = (0, 0)
        
        return (self.current_x, self.current_y, self.shake_offset)


class TileSelectionAnimation(Animation):
    def __init__(self, duration: float = None):
        if duration is None:
            duration = ANIMATION_DURATION['tile_select']
        super().__init__(duration, Easing.ease_out)
        self.scale = 1.0
    
    def update(self, current_time: float) -> float:
        progress = super().update(current_time)
        self.scale = 1.0 + 0.1 * math.sin(progress * math.pi)
        return self.scale


class ButtonAnimation:
    def __init__(self):
        self.hover_progress = 0.0
        self.click_progress = 0.0
        self.is_hovered = False
        self.is_clicked = False
        self.scale = 1.0
        self.color_offset = 0
        self.border_width = 2
    
    def update(self, is_mouse_over: bool, is_mouse_down: bool, dt: float):
        target_hover = 1.0 if is_mouse_over else 0.0
        hover_speed = 5.0
        self.hover_progress += (target_hover - self.hover_progress) * hover_speed * dt
        self.hover_progress = max(0.0, min(1.0, self.hover_progress))
        
        if is_mouse_down and is_mouse_over:
            if not self.is_clicked:
                self.is_clicked = True
                self.click_progress = 0.0
        else:
            if self.is_clicked:
                self.is_clicked = False
        
        if self.is_clicked:
            self.click_progress = min(self.click_progress + dt * 10, 1.0)
        else:
            self.click_progress = max(self.click_progress - dt * 10, 0.0)
        
        hover_scale = BUTTON_ANIMATION['hover_scale']
        click_scale = BUTTON_ANIMATION['click_scale']
        
        hover_effect = (hover_scale - 1.0) * self.hover_progress
        click_effect = (click_scale - 1.0) * self.click_progress
        
        self.scale = 1.0 + hover_effect + click_effect
        
        hover_color = BUTTON_ANIMATION['hover_color_shift']
        click_color = BUTTON_ANIMATION['click_color_shift']
        
        self.color_offset = int(hover_color * self.hover_progress - click_color * self.click_progress)
        self.border_width = 2 + int(self.hover_progress * 2)


class Particle:
    def __init__(self, x: float, y: float, vx: float, vy: float, color: Tuple[int, int, int], 
                 size: float, life: float):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.max_life = life
        self.life = life
        self.alpha = 255
    
    def update(self, dt: float) -> bool:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 100 * dt
        self.life -= dt
        self.alpha = int(255 * (self.life / self.max_life))
        return self.life > 0
    
    def draw(self, surface: pygame.Surface):
        if self.alpha <= 0:
            return
        s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        color_with_alpha = (*self.color, self.alpha)
        pygame.draw.circle(s, color_with_alpha, (int(self.size), int(self.size)), int(self.size))
        surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))


class ParticleSystem:
    def __init__(self):
        self.particles: List[Particle] = []
    
    def emit(self, x: float, y: float, color: Tuple[int, int, int], count: int = 10, spread: float = 100):
        import random
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, spread)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 50
            size = random.uniform(2, 5)
            life = random.uniform(0.3, 0.8)
            self.particles.append(Particle(x, y, vx, vy, color, size, life))
    
    def update(self, dt: float):
        self.particles = [p for p in self.particles if p.update(dt)]
    
    def draw(self, surface: pygame.Surface):
        for particle in self.particles:
            particle.draw(surface)


class AnimationManager:
    def __init__(self):
        self.animations: List[Animation] = []
        self.unit_move_animations: Dict[int, UnitMoveAnimation] = {}
        self.unit_attack_animations: Dict[int, UnitAttackAnimation] = {}
        self.tile_animations: Dict[Tuple[int, int], TileSelectionAnimation] = {}
        self.particle_system = ParticleSystem()
        self.button_animations: Dict[str, ButtonAnimation] = {}
        self.last_time = pygame.time.get_ticks() / 1000.0
    
    def get_dt(self) -> float:
        current_time = pygame.time.get_ticks() / 1000.0
        dt = current_time - self.last_time
        self.last_time = current_time
        return dt
    
    def add_unit_move(self, unit_id: int, start_pos: Tuple[float, float], end_pos: Tuple[float, float]):
        anim = UnitMoveAnimation(start_pos, end_pos)
        anim.start(pygame.time.get_ticks() / 1000.0)
        self.unit_move_animations[unit_id] = anim
    
    def add_unit_attack(self, unit_id: int, start_pos: Tuple[float, float], target_pos: Tuple[float, float]):
        anim = UnitAttackAnimation(start_pos, target_pos)
        anim.start(pygame.time.get_ticks() / 1000.0)
        self.unit_attack_animations[unit_id] = anim
    
    def add_tile_selection(self, tile_pos: Tuple[int, int]):
        anim = TileSelectionAnimation()
        anim.start(pygame.time.get_ticks() / 1000.0)
        self.tile_animations[tile_pos] = anim
    
    def get_button_animation(self, button_id: str) -> ButtonAnimation:
        if button_id not in self.button_animations:
            self.button_animations[button_id] = ButtonAnimation()
        return self.button_animations[button_id]
    
    def update_all(self):
        current_time = pygame.time.get_ticks() / 1000.0
        
        to_remove = []
        for unit_id, anim in self.unit_move_animations.items():
            anim.update(current_time)
            if anim.is_finished:
                to_remove.append(unit_id)
        for unit_id in to_remove:
            del self.unit_move_animations[unit_id]
        
        to_remove = []
        for unit_id, anim in self.unit_attack_animations.items():
            anim.update(current_time)
            if anim.is_finished:
                to_remove.append(unit_id)
        for unit_id in to_remove:
            del self.unit_attack_animations[unit_id]
        
        to_remove = []
        for tile_pos, anim in self.tile_animations.items():
            anim.update(current_time)
            if anim.is_finished:
                to_remove.append(tile_pos)
        for tile_pos in to_remove:
            del self.tile_animations[tile_pos]
        
        dt = self.get_dt()
        self.particle_system.update(dt)
    
    def is_unit_animating(self, unit_id: int) -> bool:
        return unit_id in self.unit_move_animations or unit_id in self.unit_attack_animations
    
    def get_unit_position(self, unit_id: int, default_pos: Tuple[float, float]) -> Tuple[float, float]:
        if unit_id in self.unit_move_animations:
            return (self.unit_move_animations[unit_id].current_x, self.unit_move_animations[unit_id].current_y)
        elif unit_id in self.unit_attack_animations:
            return (self.unit_attack_animations[unit_id].current_x, self.unit_attack_animations[unit_id].current_y)
        return default_pos
    
    def get_target_shake(self, target_pos: Tuple[float, float]) -> Tuple[float, float]:
        for anim in self.unit_attack_animations.values():
            if (anim.target_x, anim.target_y) == target_pos:
                return anim.shake_offset
        return (0, 0)
