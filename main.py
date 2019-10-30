import engine
import render_functions
import event_manager
from input import InputHandler
import warnings


def run():

    evmanager = event_manager.EventManager()
    game_engine = engine.GameEngine(evmanager)
    input_handler = InputHandler(evmanager, game_engine)
    renderer = render_functions.Renderer(evmanager, game_engine)
    game_engine.run()

if __name__ == '__main__':
    run()