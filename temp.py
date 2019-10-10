import tcod as libtcod
from game_states import GameStates

def menu(con, header, options, width, screen_width, screen_height, list=True):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')
    # So we can pad our box by 1 cell
    text_width = width - 1

    # calculate total height for the header (after auto-wrap) and one line per option
    if header == None:
        header_height = 0
    else:
        header_height = libtcod.console_get_height_rect(con, 0, 0, text_width, screen_height, header)

    height = len(options) + header_height

    # create an off-screen console that represents the menu's window
    #window = libtcod.console_new(width, height)
    window = libtcod.console.Console(width, screen_height)

    # print the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    if header != None:
        libtcod.console_print_rect_ex(window, 1, 1, text_width, height, libtcod.BKGND_SCREEN, libtcod.LEFT, header)
        header_height += 2
        height += 2

    # add 1 line space between the header and the rest
    header_height += 1    
    height += 1

    # print all the options
    text_height = 0
    if list:
        y = header_height
        letter_index = ord('a')
        for options_text in options:
            text = '(' + chr(letter_index) + ') ' + options_text
            text_height = libtcod.console_get_height_rect(con, 0, 0, width, screen_height, text)
            libtcod.console_print_rect_ex(window, 1, y, text_width, text_height, libtcod.BKGND_NONE, libtcod.LEFT, text)
            y += text_height
            letter_index += 1
    else:
        y = header_height
        for options_text in options:
            text_height = libtcod.console_get_height_rect(con, 0, 0, width, screen_height, options_text)
            libtcod.console_print_rect_ex(window, 1, y, text_width, text_height , libtcod.BKGND_NONE, libtcod.LEFT, options_text)
            y += text_height

    height = height + text_height
    # draw box for window
    window.draw_rect(0, 0, width , height , 0, bg=libtcod.white)

    # blit the contents of "window" to the root console
    x = int(screen_width / 2 - width / 2)
    y = int(screen_height / 2 - height / 2)
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.4)

def inventory_menu(con, header, inventory, inventory_width, screen_width, screen_height):
    # show a menu with each item of the inventory as an option
    if len(inventory.items) == 0:
        options = ['Inventory is empty']
    else:
        options = [item.name for item in inventory.items]
        options.sort()

    menu(con, header, options, inventory_width, screen_width, screen_height)

def main_menu(con, background_image, screen_width, screen_height):
    libtcod.image_blit_2x(background_image, 0, 0, 0)

    libtcod.console_set_default_foreground(0, libtcod.yellow)
    libtcod.console_print_ex(0, int(screen_width / 2), int(screen_height / 2) - 6, libtcod.BKGND_NONE, libtcod.CENTER, 
        'A Song of Pong and Moustache')
    libtcod.console_print_ex(0, int(screen_width / 2), int(screen_height - 2), libtcod.BKGND_NONE, libtcod.CENTER,
        'By Don Carruthers')
    menu(con, None,['Play a new game', 'Continue last game', 'Quit'], 24, screen_width, screen_height)

def message_box(con, header, width, screen_width, screen_height):
    menu(con, header, [], width, screen_width, screen_height)