import itertools as it
from time import time
import random
from math import copysign


from pygame.math import Vector2
import pygame


from engine.input_manager import InputManager
from engine.scene_manager import SceneManager
from engine.initialize_engine import width, height
from engine.base_components import Component, ImageComponent, ImageFile
from engine.game_objects import GameObject
from engine.gui import GUI

from gui_misc import MedievalButton


class SceneReplacement:
    coords = {}
    del_tardis_flag = False

    @staticmethod
    def load_house(house):
        from scene_loader import load_scene
        GUI.del_element('house')
        SceneReplacement.coords['coord_in_street'] = SceneManager.current_scene.find_object('player').transform.coord
        load_scene('scenes/{}.json'.format(house))

        if SceneReplacement.del_tardis_flag:
            if SceneManager.current_scene.find_object('tardis'):
                SceneManager.current_scene.remove_object(SceneManager.current_scene.find_object('tardis'))
        else:
            SceneReplacement.del_tardis_flag = True

    @staticmethod
    def load_street():
        from scene_loader import load_scene
        GUI.del_element('enter_to_street')
        load_scene('scenes/scene1.json')
        SceneManager.current_scene.find_object('player').transform.move_to(*SceneReplacement.coords['coord_in_street'])


class AnimationController(ImageComponent):
    def __init__(self, animations, start_animation, game_object):
        self.animations = {}
        for name, params in animations.items():
            self.animations[name] = AnimationController.cut_sheet(
                AnimationController.load_image(params['path']), *params['size'], params['repeats']
            )
        self._current_animation_name = start_animation
        self._current_animation = it.cycle(self.animations[start_animation])
        super().__init__(next(self._current_animation), game_object)

    @staticmethod
    def cut_sheet(sheet, rows, cols, repeats):
        frames = []
        for j in range(rows):
            for i in range(cols):
                frame = sheet.subsurface(pygame.Rect(
                    sheet.get_width() // cols * i, sheet.get_height() // rows * j,
                    sheet.get_width() // cols, sheet.get_height() // rows
                ))
                for _ in range(repeats):
                    frames.append(frame)
        return frames

    def add_animation(self, name, path, size, repeats):
        self.animations[name] = AnimationController.cut_sheet(
            AnimationController.load_image(path), *size, repeats
        )

    def set_animation(self, name):
        self._current_animation_name = name
        self._current_animation = it.cycle(self.animations[name])

    def play_animation(self, name, times=1):
        self._current_animation = it.chain(
            iter(self.animations[name] * times), it.cycle(self.animations[self._current_animation_name])
        )

    def update(self, *args):
        self.image = next(self._current_animation)

    @staticmethod
    def deserialize(component_dict, obj):
        return AnimationController(
            component_dict['animations'], component_dict['start_animation'], obj
        )


class PlayerController(Component):
    def __init__(self, speed, game_object):
        super().__init__(game_object)
        self.speed = speed
        self.gui_obj = {}
        self._prev_move = Vector2()
        self._direction = 'down'
        self.set_camera_pos()

        self._steps_sound = pygame.mixer.Sound('sounds/steps.ogg')

    def change_animation(self, move):
        animator = self.game_object.get_component(AnimationController)
        if animator is not None:
            if move.x > 0:
                if self._prev_move.x == 0 or self._direction != 'right':
                    animator.set_animation('right')
                self._direction = 'right'
            elif move.x < 0:
                if self._prev_move.x == 0 or self._direction != 'left':
                    animator.set_animation('left')
                self._direction = 'left'
            elif move.y > 0:
                if self._prev_move.y == 0 or self._direction != 'up':
                    animator.set_animation('up')
                self._direction = 'up'
            elif move.y < 0:
                if self._prev_move.y == 0 or self._direction != 'down':
                    animator.set_animation('down')
                self._direction = 'down'
            elif move.x == move.y == 0 and self._prev_move.length() != 0:
                animator.set_animation('idle_' + self._direction)

    def play_sound(self, move):
        if self._prev_move.length() == 0 and move.length() != 0:
            self._steps_sound.play(-1)
        elif move.length() == 0:
            self._steps_sound.stop()

    def set_camera_pos(self):
        cam = SceneManager.current_scene.current_camera
        x, y = self.game_object.transform.coord

        if abs(x) < 1024 - width // 2:
            cam.transform.move_to(x, cam.transform.y)
        else:
            cam.transform.move_to(
                copysign(1024 - width // 2, x), cam.transform.y
            )

        if abs(y) < 1024 - height // 2:
            cam.transform.move_to(cam.transform.x, y)
        else:
            cam.transform.move_to(
                cam.transform.x, copysign(1024 - height // 2, y)
            )

    def update(self, *args):
        move = Vector2(
            InputManager.get_axis('Horizontal') * self.speed,
            InputManager.get_axis('Vertical') * self.speed
        )
        self.game_object.transform.move(move.x, move.y)

        phys_collider = self.game_object.get_component(PhysicsCollider)

        for obj in SceneManager.current_scene.objects:
            if phys_collider is not None:
                phys_collider.update()
                if obj != self.game_object and obj.has_component(PhysicsCollider):
                    collision = phys_collider.detect_collision(obj.get_component(PhysicsCollider))
                    if collision:
                        self.game_object.transform.move(-move.x, -move.y)
                        move = Vector2()

        self.set_camera_pos()
        self.change_animation(move)
        self.play_sound(move)
        self._prev_move = move

    @staticmethod
    def deserialize(component_dict, obj):
        return PlayerController(component_dict['speed'], obj)


class TriggerController(Component):
    def __init__(self, game_object):
        super().__init__(game_object)
        self._player_collider = SceneManager.current_scene.find_object('player').get_component(TriggerCollider)
        self._collider = self.game_object.get_component(TriggerCollider)

        self.gui_obj = None

    @staticmethod
    def deserialize(component_dict, obj):
        return TriggerController(obj)


class House1Trigger(TriggerController):
    def update(self, *args):
        if self._collider is not None and self._player_collider is not None:
            if self._collider.detect_collision(self._player_collider):
                if self.gui_obj is None:
                    self.gui_obj = GUI.add_element(MedievalButton(
                        (width // 2, height - 100), 'Enter in house', 29, 'house',
                        lambda: SceneReplacement.load_house('house1')
                    ))
            else:
                if self.gui_obj is not None:
                    GUI.del_element(self.gui_obj.name)
                    self.gui_obj = None

    @staticmethod
    def deserialize(component_dict, obj):
        return House1Trigger(obj)


class House2Trigger(TriggerController):
    def update(self, *args):
        if self._collider is not None and self._player_collider is not None:
            if self._collider.detect_collision(self._player_collider):
                if self.gui_obj is None:
                    self.gui_obj = GUI.add_element(MedievalButton(
                        (width // 2, height - 100), 'Enter in house', 29, 'house',
                        lambda: SceneReplacement.load_house('house2')
                    ))
            else:
                if self.gui_obj is not None:
                    GUI.del_element(self.gui_obj.name)
                    self.gui_obj = None

    @staticmethod
    def deserialize(component_dict, obj):
        return House2Trigger(obj)


class EnterStreetTrigger(TriggerController):
    def update(self, *args):
        if self._collider is not None and self._player_collider is not None:
            if self._collider.detect_collision(self._player_collider):
                if self.gui_obj is None:
                    self.gui_obj = GUI.add_element(MedievalButton(
                        (width // 2, height - 100), 'Come to street', 29, 'enter_to_street',
                        lambda: SceneReplacement.load_street()
                    ))
            else:
                if self.gui_obj is not None:
                    GUI.del_element(self.gui_obj.name)
                    self.gui_obj = None

    @staticmethod
    def deserialize(component_dict, obj):
        return EnterStreetTrigger(obj)


class _ColliderSprite(pygame.sprite.Sprite):
    def __init__(self, rect):
        super().__init__()
        self.shift_x = rect[0]
        self.shift_y = rect[1]
        self.rect = pygame.Rect(0, 0, *rect[2:])

    def move_to(self, x, y):
        self.rect.center = x + self.shift_x, y + self.shift_y

    def update(self, x, y, *args):
        self.move_to(x, y)


class Collider(Component):
    def __init__(self, rects, game_object):
        super().__init__(game_object)
        self.rects = pygame.sprite.Group(*(_ColliderSprite(rect) for rect in rects))

    def detect_collision(self, collider):
        return pygame.sprite.groupcollide(self.rects, collider.rects, False, False)

    def update(self, *args):
        self.rects.update(*self.game_object.transform.coord)

    @staticmethod
    def deserialize(component_dict, obj):
        return Collider(component_dict['rects'], obj)


class PhysicsCollider(Collider):
    def __init__(self, rects, game_object):
        if not rects:
            rect = game_object.get_component(ImageComponent)
            if rect is None:
                raise ValueError('rect parameter is empty and PhysicsCollider component added before ImageComponent')
            else:
                rects = [rect.image.get_rect()]

        super().__init__(rects, game_object)

    @staticmethod
    def deserialize(component_dict, obj):
        return PhysicsCollider(component_dict['rects'], obj)


class TriggerCollider(Collider):
    def __init__(self, rects, trigger_name, game_object):
        self.trigger_name = trigger_name
        super().__init__(rects, game_object)

    @staticmethod
    def deserialize(component_dict, obj):
        return TriggerCollider(
            component_dict['rects'], component_dict['trigger_name'], obj
        )


class ParticleSystem(Component):
    def __init__(self, image_path, particles_per_frame, correction, speed, life_time, game_object):
        self.path = image_path
        self.particles_per_frame = particles_per_frame
        self.speed = speed
        self.life_time = life_time
        self.correction = Vector2(correction) + Vector2(-0.5, -0.5)
        super().__init__(game_object)

    def update(self, *args):
        for _ in range(self.particles_per_frame):
            go = GameObject(*self.game_object.transform.coord)
            go.add_component(ImageFile(self.path, go))
            go.add_component(Particle(
                (self.correction + Vector2(random.random(), random.random())).normalize(),
                self.speed, self.life_time, go
            ))
            SceneManager.current_scene.add_object(go)

    @staticmethod
    def deserialize(component_dict, obj):
        return ParticleSystem(
            component_dict['path'], component_dict['particles_per_frame'], component_dict['correction'],
            component_dict['speed'], component_dict['life_time'], obj
        )


class Particle(Component):
    def __init__(self, direction, speed, life_time, game_object):
        super().__init__(game_object)
        self.life_time = life_time
        self.direction = direction
        self.speed = speed
        self._start = time()

    def update(self, *args):
        if time() - self._start >= self.life_time:
            # POSSIBLE MEMORY LEAK ????????
            SceneManager.current_scene.remove_object(self.game_object)
        else:
            move = self.direction * self.speed
            self.game_object.transform.move(move.x, move.y)


class MusicController(Component):
    def __init__(self, music_paths, game_object):
        super().__init__(game_object)
        for path, volume in music_paths:
            snd = pygame.mixer.Sound(path)
            snd.set_volume(volume / 100)
            snd.play(-1)

    @staticmethod
    def deserialize(component_dict, obj):
        return MusicController(component_dict['paths'], obj)


class WaterSound(Component):
    def __init__(self, max_distance, game_object):
        super().__init__(game_object)
        self.sound = pygame.mixer.Sound('sounds/water_waves.ogg')
        self.sound.play(-1)
        self.player_transform = SceneManager.current_scene.find_object('player').transform
        self.max_distance = max_distance

    def update(self, *args):
        vol = (self.max_distance - Vector2(
            self.game_object.transform.x - self.player_transform.x,
            self.game_object.transform.y - self.player_transform.y
        ).length()) / self.max_distance

        self.sound.set_volume(0 if vol < 0 else vol)
        if vol < 0:
            self.sound.set_volume(0)
        else:
            self.sound.set_volume(vol)

    @staticmethod
    def deserialize(component_dict, obj):
        return WaterSound(component_dict['max_distance'], obj)


class NPCController(Component):
    def __init__(self, speed, commands, game_object):
        super().__init__(game_object)
        self.speed = speed

        _ = []
        for i, com in enumerate(commands):
            com_ = com.split()[0]
            if com_ == 'move_to' and len(com_) > 2:
                for com2 in com.split()[1:]:
                    _1 = com2.replace('(', '').replace(')', '').replace(';', ' ')
                    _.append("move_to {}".format(_1))
            else:
                _.append(com)

        self.commands = it.cycle(_)
        self.current_command = next(self.commands)
        self._start_sleep = None
        self._prev_move = Vector2()
        self._direction = 'down'

    def change_animation(self, move):
        animator = self.game_object.get_component(AnimationController)
        if animator is not None:
            if move.x > 0:
                if self._prev_move.x == 0 or self._direction != 'right':
                    animator.set_animation('right')
                self._direction = 'right'
            elif move.x < 0:
                if self._prev_move.x == 0 or self._direction != 'left':
                    animator.set_animation('left')
                self._direction = 'left'
            elif move.y > 0:
                if self._prev_move.y == 0 or self._direction != 'up':
                    animator.set_animation('up')
                self._direction = 'up'
            elif move.y < 0:
                if self._prev_move.y == 0 or self._direction != 'down':
                    animator.set_animation('down')
                self._direction = 'down'
            elif move.x == move.y == 0 and self._prev_move.length() != 0:
                animator.set_animation('idle_' + self._direction)

    def update(self, *args):
        command = self.current_command.split()
        if command[0] == 'move_to':
            move = Vector2(int(command[1]) - self.game_object.transform.x, int(command[2]) - self.game_object.transform.y)
            if move.length() > self.speed:
                move = move.normalize() * self.speed
            else:
                self.current_command = next(self.commands)

            self.game_object.transform.move(move.x, move.y)

            phys_collider = self.game_object.get_component(PhysicsCollider)
            for obj in SceneManager.current_scene.objects:
                if phys_collider is not None:
                    phys_collider.update()
                    if obj != self.game_object and obj.has_component(PhysicsCollider):
                        collision = phys_collider.detect_collision(obj.get_component(PhysicsCollider))
                        if collision:
                            self.game_object.transform.move(-move.x, -move.y)
                            move = Vector2()

            self.change_animation(move)
            self._prev_move = move

        elif command[0] == 'sleep':
            if self._start_sleep is None:
                self._start_sleep = time()
            if time() - self._start_sleep >= float(command[1]):
                self.current_command = next(self.commands)
                self._start_sleep = None
            self.change_animation(Vector2())
            self._prev_move = Vector2()

        elif command[0] == 'del_self':
            SceneManager.current_scene.remove_object(self.game_object)

    @staticmethod
    def deserialize(component_dict, obj):
        return NPCController(component_dict['speed'], component_dict['commands'], obj)


class TardisController(Component):
    def __init__(self, game_object):
        super().__init__(game_object)
        self._start_time = time()
        self.game_object.get_component(AnimationController).play_animation('start')

    def update(self, *args):
        if time() - self._start_time > 3:
            SceneManager.current_scene.remove_object(self.game_object)

    @staticmethod
    def deserialize(component_dict, obj):
        return TardisController(obj)
