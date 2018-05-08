from engine.gui import GUI, load_image, Label, Image, TextBox
from engine.initialize_engine import Config
from engine.save_manager import SaveManager
from engine.scene_manager import SceneManager
from engine.game_objects import GameObject

from scene_loader import load_scene
from gui_misc import CloudsController, MedievalButton, MedievalCheckbox, ButtonChanger
from user_components import NetworkingController, ChatController, ChatContainer, AnimationController,MusicController, PhysicsCollider

from pygame import Color
import pygame


class MainMenuGUI:
    scene = None
    @staticmethod
    def start_game():
        MainMenuGUI.scene = load_scene('scenes/scene1.json')
        SaveManager.add_profile('village1', {'seen_tardis': False})
        GUI.clear()
        GameGUI.init()

    @staticmethod
    def load_settings():
        MainMenuGUI.remove_buttons()
        SettingsGUI.init()

    @staticmethod
    def exit():
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    @staticmethod
    def add_buttons():
        GUI.add_element(MedievalButton(
            (Config.get_width() // 2, Config.get_height() // 2),
            'Start game', 35, 'start_game', MainMenuGUI.start_game
        ))

        GUI.add_element(MedievalButton(
            (Config.get_width() // 2, Config.get_height() // 2 + 75),
            'Multyplayer', 35, 'multyplayer', Multyplayer.init
        ))

        GUI.add_element(MedievalButton(
            (Config.get_width() // 2, Config.get_height() // 2 + 150),
            'Settings', 35, 'settings', MainMenuGUI.load_settings
        ))

        GUI.add_element(MedievalButton(
            (Config.get_width() // 2, Config.get_height() // 2 + 225),
            'Exit', 35, 'exit', MainMenuGUI.exit
        ))

    @staticmethod
    def remove_buttons():
        GUI.del_element('start_game')
        GUI.del_element('multyplayer')
        GUI.del_element('settings')
        GUI.del_element('exit')

    @staticmethod
    def init():
        clouds_controller = CloudsController('Con', [1, 0])
        CloudsController.generate_clouds(15, clouds_controller)

        GUI.add_element(Image((Config.get_width() // 2, Config.get_height() // 2), pygame.transform.scale(
            load_image('images/main_menu/sky.png'), (Config.get_width(), Config.get_height())
        ), 'sky'))
        GUI.add_element(clouds_controller)

        GUI.add_element(Image((Config.get_width() // 2, 75), load_image('images/main_menu/title_bg.png'), 'title'))
        GUI.add_element(Label(
            (Config.get_width() // 2, 159), 53, 'Untitled game',
            Color('white'), 'fonts/Dot.ttf', 'title_text'
        ))

        MainMenuGUI.add_buttons()

class Multyplayer:
    @staticmethod
    def init():
        MainMenuGUI.remove_buttons()

        GUI.add_element(TextBox(
            (Config.get_width() // 2, Config.get_height() // 2, Config.get_height() // 2+100, 40),
            '', default_text='Login', name='user_login'))
        GUI.add_element(TextBox(
            (Config.get_width() // 2, Config.get_height() // 2+80, Config.get_height() // 2+100, 40),
            '', default_text='Server`s IP address', name='server`s_ip'))

        Multyplayer.add_buttons()
    @staticmethod
    def add_buttons():
        GUI.add_element(MedievalButton(
            (Config.get_width() // 2, Config.get_height() // 2 + 180),
            'Connect', 29, 'connect_with_server', lambda :Multyplayer.connect_with_server(
                    GUI.get_element('user_login').text,
                    GUI.get_element('server`s_ip').text)
        ))
        GUI.add_element(MedievalButton(
            (Config.get_width() // 2, Config.get_height() // 2 + 280),
            'Close', 29, 'close_myultyplayer', Multyplayer.exit
        ))

    @staticmethod
    def exit():
        Multyplayer.clear()
        MainMenuGUI.init()

    @staticmethod
    def clear():
        GUI.del_element('user_login', 'server`s_ip', 'bg_img', 'close_myultyplayer', 'connect_with_server')

    @staticmethod
    def connect_with_server(login, ip_address):
        print(login, ip_address)
        MainMenuGUI.start_game()
        go = GameObject(name='networking')
        go.add_component(NetworkingController(login, ip_address, 50000, go))
        go.add_component(ChatController(login, ip_address, 50001, go))
        go.add_component(ChatContainer(go))
        SceneManager.current_scene.add_object(go)

class SettingsGUI:
    _button_changer = None

    @staticmethod
    def exit():
        SettingsGUI.clear()
        MainMenuGUI.init()

    @staticmethod
    def clear():
        GUI.del_element(
            'lbl_change_keys', 'btn_mvup', 'btn_mvdown', 'btn_mvleft', 'btn_mvright',
            'lbl_set_resolution', 'btn_res1080p', 'btn_res_wxga+', 'btn_res_wxga', 'btn_res_720p', 'btn_res_xga',
            'bg_img', 'toggle_fullscreen', 'close_settings',
        )

    @staticmethod
    def toggle_fullscreen(value):
        SaveManager.set_entry('preferences', 'fullscreen', value)
        Config.set_fullscreen(value)

    @staticmethod
    def change_button(name):
        if SettingsGUI._button_changer is not None:
            if SettingsGUI._button_changer[2] in SceneManager.current_scene.objects:
                SceneManager.current_scene.remove_object(
                    SettingsGUI._button_changer[2]
                )
                SettingsGUI._button_changer[0].text = SettingsGUI._button_changer[1]

        button = GUI.get_element('btn_mv' + name)
        go = GameObject()
        go.add_component(ButtonChanger(name, button, go))
        SettingsGUI._button_changer = [button, button.text, go]
        button.text = 'Press any key...'
        SceneManager.current_scene.add_object(go)

    @staticmethod
    def add_move_buttons():
        x = 230
        y = 280

        GUI.add_element(Label(
            (Config.get_width() // 2 - x, Config.get_height() // 2 - y + 75), 32, 'Change control keys',
            pygame.Color('white'), 'fonts/Dot.ttf', 'lbl_change_keys'
        ))

        GUI.add_element(MedievalButton(
            (Config.get_width() // 2 - x, Config.get_height() // 2 - y + 75 * 2),
            'Move up: {}'.format(
                pygame.key.name(SaveManager.get_entry('preferences', 'up'))
            ), 29, 'btn_mvup', SettingsGUI.change_button, 'up'
        ))

        GUI.add_element(MedievalButton(
            (Config.get_width() // 2 - x, Config.get_height() // 2 - y + 75 * 3),
            'Move down: {}'.format(
                pygame.key.name(SaveManager.get_entry('preferences', 'down'))
            ), 29, 'btn_mvdown', SettingsGUI.change_button, 'down'
        ))

        GUI.add_element(MedievalButton(
            (Config.get_width() // 2 - x, Config.get_height() // 2 - y + 75 * 4),
            'Move left: {}'.format(
                pygame.key.name(SaveManager.get_entry('preferences', 'left'))
            ), 29, 'btn_mvleft', SettingsGUI.change_button, 'left'
        ))

        GUI.add_element(MedievalButton(
            (Config.get_width() // 2 - x, Config.get_height() // 2 - y + 75 * 5),
            'Move right: {}'.format(
                pygame.key.name(SaveManager.get_entry('preferences', 'right'))
            ), 29, 'btn_mvright', SettingsGUI.change_button, 'right'
        ))

    @staticmethod
    def add_resolutions_buttons():
        x = 230
        y = 280

        GUI.add_element(Label(
            (Config.get_width() // 2 + x, Config.get_height() // 2 - y + 75), 32, 'Set display resolution',
            pygame.Color('white'), 'fonts/Dot.ttf', 'lbl_set_resolution'
        ))

        GUI.add_element(MedievalButton(
            (Config.get_width() // 2 + x, Config.get_height() // 2 - y + 75 * 2),
            '1920x1080', 29, 'btn_res1080p', SettingsGUI.set_resolution, 1920, 1080
        ))

        GUI.add_element(MedievalButton(
            (Config.get_width() // 2 + x, Config.get_height() // 2 - y + 75 * 3),
            '1440x900', 29, 'btn_res_wxga+', SettingsGUI.set_resolution, 1440, 900
        ))

        GUI.add_element(MedievalButton(
            (Config.get_width() // 2 + x, Config.get_height() // 2 - y + 75 * 4),
            '1366x768', 29, 'btn_res_wxga', SettingsGUI.set_resolution, 1366, 768
        ))

        GUI.add_element(MedievalButton(
            (Config.get_width() // 2 + x, Config.get_height() // 2 - y + 75 * 5),
            '1280x720', 29, 'btn_res_720p', SettingsGUI.set_resolution, 1280, 720
        ))

        GUI.add_element(MedievalButton(
            (Config.get_width() // 2 + x, Config.get_height() // 2 - y + 75 * 6),
            '1024x768', 29, 'btn_res_xga', SettingsGUI.set_resolution, 1024, 768
        ))

    @staticmethod
    def set_resolution(width, height):
        Config.set_resolution(width, height)
        SaveManager.set_entry('preferences', 'resolution', [width, height])
        GUI.clear()
        MainMenuGUI.init()
        MainMenuGUI.remove_buttons()
        SettingsGUI.init()

    @staticmethod
    def init():
        GUI.add_element(Image(
            (Config.get_width() // 2, Config.get_height() // 2 + 40),
            load_image('images/bg.png'), 'bg_img')
        )

        SettingsGUI.add_move_buttons()
        SettingsGUI.add_resolutions_buttons()

        GUI.add_element(MedievalCheckbox(
            'toggle_fullscreen', (Config.get_width() // 2 + 230, Config.get_height() // 2 + 230),
            'Toggle Fullscreen', 29, SaveManager.get_entry('preferences', 'fullscreen'),
            SettingsGUI.toggle_fullscreen
        ))
        GUI.add_element(MedievalButton(
            (Config.get_width() // 2, Config.get_height() // 2 + 280),
            'Close', 29, 'close_settings', SettingsGUI.exit
        ))


class GameGUI:
    pause_menu_elements = set()
    flag_borba = True

    @staticmethod
    def exit_in_menu():
        for scene in SceneManager.scenes.values():
            for obj in scene.objects:
                for component in obj.get_components(NetworkingController):
                    component.client.shutdown()
                for component in obj.get_components(ChatController):
                    component.client.shutdown()
        GUI.clear()
        load_scene('scenes/main_menu.json')
        MainMenuGUI.init()

    @staticmethod
    def pause_menu_clear():
        for _ in GameGUI.pause_menu_elements:
            GUI.del_element(_)

        GameGUI.pause_menu_elements.clear()
        GUI.get_element('game_menu').func = GameGUI.create_menu

    @staticmethod
    def create_menu():
        GUI.get_element('game_menu').func = GameGUI.pause_menu_clear

        GUI.add_element(Image((Config.get_width() // 2, Config.get_height() // 2), load_image("images/game_menu_gui/menu.png"), 'background'))
        GameGUI.pause_menu_elements.add('background')

        GUI.add_element(MedievalButton((Config.get_width() // 2, Config.get_height() // 2 - 50), 'Resume', 35, 'resume', GameGUI.pause_menu_clear))
        GameGUI.pause_menu_elements.add('resume')

        GUI.add_element(MedievalButton((Config.get_width() // 2, Config.get_height() // 2 + 20), 'Exit in menu', 33, 'exit', GameGUI.exit_in_menu))
        GameGUI.pause_menu_elements.add('exit')

        GUI.add_element(MedievalButton((Config.get_width() // 2, Config.get_height() // 2 + 90), 'Exit in desktop', 29, 'exit_in_desktop', MainMenuGUI.exit))
        GameGUI.pause_menu_elements.add('exit_in_desktop')

    @staticmethod
    def init():
        GUI.add_element(MedievalButton((Config.get_width() // 2, Config.get_height()- 175), 'Начать бароца', 25, 'myBorba',
                                       GameGUI.borba))
        GUI.add_element(MedievalButton((Config.get_width() // 2, Config.get_height() - 35), 'Menu', 35, 'game_menu', GameGUI.create_menu))

    @staticmethod
    def borba():
        print('Борьба активирована')

        player = MainMenuGUI.scene.find_object('player')
        print(player.components)
        if GameGUI.flag_borba:
            anime = [str(player.components[1]), str(player.components[2])]
        else:
            anime = [str(player.components[-1]), str(player.components[-2])]
        a = []
        for com in player.components:
            if str(com) not in anime:
                a.append(com)
        player.components = a[:]
        player.add_component(AnimationController.deserialize({
            "name": "AnimationControllerd1",
            "start_animation": "idle_right",
            "animations": {
                "up": {"path": "images/player/myBorba/run_up.png", "size": [1, 10], "repeats": 3},
                "down": {"path": "images/player/myBorba/run_down.png", "size": [1, 10], "repeats": 3},
                "right": {"path": "images/player/myBorba/run_right.png", "size": [1, 10], "repeats": 3},
                "left": {"path": "images/player/myBorba/run_left.png", "size": [1, 10], "repeats": 3},

                "idle_up": {"path": "images/player/myBorba/idle_up.png", "size": [1, 1], "repeats": 1},
                "idle_down": {"path": "images/player/myBorba/idle_down.png", "size": [1, 3], "repeats": 10},
                "idle_right": {"path": "images/player/myBorba/idle_right.png", "size": [1, 3], "repeats": 10},
                "idle_left": {"path": "images/player/myBorba/idle_left.png", "size": [1, 3], "repeats": 10}
            }
        }, player))
        player.add_component(PhysicsCollider.deserialize({'rects':[[0, -52, 66, 72]]}, player))
        if GameGUI.flag_borba:
            music = MainMenuGUI.scene.find_object("villagemusic")
            _anime = str(music.components[1])
            _a = []
            for com in music.components:
                if str(com) != _anime:
                    _a.append(com)
            music.components = _a[:]
            music.add_component(MusicController.deserialize({"paths":[["sounds/village_background_music2.ogg", 100]]}, music))
            GameGUI.flag_borba = False