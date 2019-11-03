
import tcod as libtcod
import tcod.event


# Setup the font.
tcod.console_set_custom_font(
    "arial10x10.png",
    tcod.FONT_LAYOUT_TCOD | tcod.FONT_TYPE_GREYSCALE,
)
# Initialize the root console in a context.
with tcod.console_init_root(80, 60, order="F") as root_console:
    root_console.print_(x=0, y=0, string='Hello World!')
    while True:
        tcod.console_flush()  # Show the console.
        for event in tcod.event.get():
            print(event)
            if event.type == "QUIT":
                raise SystemExit()
    # The libtcod window will be closed at the end of this with-block.

# test = True
# while test == True:
#     for event in libtcod.event.get():
#         print(event)
