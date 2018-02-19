from pygame import Color


from engine.gui import gui, Button, Image, load_image, Label
import main_menu_gui
from engine.initialize_engine import width, height
from scene_loader import load_scene


def init():
    gui.add_element(Button((width // 2, height - 35), {
        'normal': 'images/button/normal.png',
        'hovered': 'images/button/hovered.png',
        'clicked': 'images/button/clicked.png'
    }, 'game_menu', create_menu))
    gui.add_element(Label((width // 2, height - 35), 38, "Menu", Color('white'), 'fonts/Dot.ttf', 'label_game_menu'))

def create_menu():
    def deinit():
        for _ in names_elements:
            gui.del_element(_)

        names_elements.clear()

    names_elements = []
    gui.add_element(Image((width//2, height//2), load_image("images/game_menu_gui/menu.png"), 'background'))
    names_elements.append('background')

    gui.add_element(Button((width//2, height//2-50),{
        'normal': 'images/button/normal.png',
        'hovered': 'images/button/hovered.png',
        'clicked': 'images/button/clicked.png'
    },'resume', deinit))
    names_elements.append('resume')
    gui.add_element(Label((width//2, height//2-50), 38, 'Resume', Color('white'), 'fonts/Dot.ttf', 'label_resume'))
    names_elements.append('label_resume')

    gui.add_element(Button((width // 2, height // 2 + 30), {
        'normal': 'images/button/normal.png',
        'hovered': 'images/button/hovered.png',
        'clicked': 'images/button/clicked.png'
    }, 'exit', exit_in_menu))
    names_elements.append('exit')
    gui.add_element(
        Label((width // 2, height // 2 + 30), 35, 'Exit in menu', Color('white'), 'fonts/Dot.ttf', 'label_exit'))
    names_elements.append('label_exit')

    gui.add_element(Button((width // 2, height // 2 + 85), {
        'normal': 'images/button/normal.png',
        'hovered': 'images/button/hovered.png',
        'clicked': 'images/button/clicked.png'
    }, 'exit_in_desktop', exit_in_desktop))
    names_elements.append('exit_in_desktop')
    gui.add_element(
        Label((width // 2, height // 2 + 85), 31, 'Exit in desktop', Color('white'), 'fonts/Dot.ttf', 'label_exit_in_desktop'))
    names_elements.append('label_exit_in_desktop')

def exit_in_menu():
    gui.clear()
    load_scene('scenes/main_menu.json')
    main_menu_gui.init()

def exit_in_desktop():
    main_menu_gui.my_exit()
