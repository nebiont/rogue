import engine
import render_functions
import event_manager

def run():
    evmanger = event_manager.EventManager()
    game_engine = engine.GameEngine(evmanager)
    renderer = render_functions.Renderer(evmanager, game_engine)
    game_engine.run()

if __name__ == '__main__':
    run()