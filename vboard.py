#!/usr/bin/env python3

import gi
import os
import configparser
import subprocess

os.environ['GDK_BACKEND'] = 'x11'

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib

from uinput import Device, KEY_ESC, KEY_F1, KEY_F2, KEY_F3, KEY_F4, KEY_F5, KEY_F6, KEY_F7, KEY_F8, KEY_F9, KEY_F10, KEY_F11, KEY_F12, KEY_GRAVE, KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7, KEY_8, KEY_9, KEY_0, KEY_MINUS, KEY_EQUAL, KEY_BACKSPACE, KEY_TAB, KEY_Q, KEY_W, KEY_E, KEY_R, KEY_T, KEY_Y, KEY_U, KEY_I, KEY_O, KEY_P, KEY_LEFTBRACE, KEY_RIGHTBRACE, KEY_BACKSLASH, KEY_CAPSLOCK, KEY_A, KEY_S, KEY_D, KEY_F, KEY_G, KEY_H, KEY_J, KEY_K, KEY_L, KEY_SEMICOLON, KEY_APOSTROPHE, KEY_ENTER, KEY_LEFTSHIFT, KEY_Z, KEY_X, KEY_C, KEY_V, KEY_B, KEY_N, KEY_M, KEY_COMMA, KEY_DOT, KEY_SLASH, KEY_RIGHTSHIFT, KEY_LEFTCTRL, KEY_LEFTMETA, KEY_LEFTALT, KEY_SPACE, KEY_RIGHTALT, KEY_RIGHTMETA, KEY_RIGHTCTRL, KEY_SYSRQ, KEY_SCROLLLOCK, KEY_PAUSE, KEY_INSERT, KEY_HOME, KEY_PAGEUP, KEY_DELETE, KEY_END, KEY_PAGEDOWN, KEY_UP, KEY_LEFT, KEY_DOWN, KEY_RIGHT, KEY_NUMLOCK, KEY_KP0, KEY_KP1, KEY_KP2, KEY_KP3, KEY_KP4, KEY_KP5, KEY_KP6, KEY_KP7, KEY_KP8, KEY_KP9, KEY_KPPLUS, KEY_KPMINUS, KEY_KPASTERISK, KEY_KPSLASH, KEY_KPDOT, KEY_KPENTER

# Gap sizes in pixels
VBOX_SPACING = 12  # gap between top and bottom hboxes
HBOX_SPACING = 16  # gap between grids within each hbox

# Modifier states
MOD_OFF    = 0  # inactive
MOD_ON     = 1  # active for one keypress, then releases
MOD_LOCKED = 2  # stays active until clicked again

fn_rows = [
    [(KEY_ESC, "Esc"), 2, (KEY_F1, "F1"), (KEY_F2, "F2"), (KEY_F3, "F3"), (KEY_F4, "F4"),
     1, (KEY_F5, "F5"), (KEY_F6, "F6"), (KEY_F7, "F7"), (KEY_F8, "F8"),
     1, (KEY_F9, "F9"), (KEY_F10, "F10"), (KEY_F11, "F11"), (KEY_F12, "F12")],
]

sys_rows = [
    [(KEY_SYSRQ, "PrtScr", 2), (KEY_SCROLLLOCK, "ScrLk", 2), (KEY_PAUSE, "Pause", 2)],
]

fn_pad_rows = [
    [8],  # empty row matching numpad width (4 buttons x width 2)
]

navigation_rows = [
    [(KEY_INSERT, "Ins", 2), (KEY_HOME, "Home", 2), (KEY_PAGEUP, "PgUp", 2)],
    [(KEY_DELETE, "Del", 2), (KEY_END, "End", 2), (KEY_PAGEDOWN, "PgDn", 2)],
    [6],
    [2, (KEY_UP, "↑"), 2],
    [(KEY_LEFT, "←"), (KEY_DOWN, "↓"), (KEY_RIGHT, "→")],
]

numpad_rows = [
    [(KEY_NUMLOCK, " Num "), (KEY_KPSLASH, "/"), (KEY_KPASTERISK, "*"), (KEY_KPMINUS, "-", 2, 2)],
    [(KEY_KP7, "7"), (KEY_KP8, "8"), (KEY_KP9, "9"), (KEY_KPPLUS, "+", 2, 2)],
    [(KEY_KP4, "4"), (KEY_KP5, "5"), (KEY_KP6, "6")],
    [(KEY_KP1, "1"), (KEY_KP2, "2"), (KEY_KP3, "3"), (KEY_KPENTER, "⏎", 2, 2)],
    [(KEY_KP0, "0", 4), (KEY_KPDOT, ".")],
]

base_60_rows = [
    [(KEY_GRAVE, "`"), (KEY_1, "1"), (KEY_2, "2"), (KEY_3, "3"), (KEY_4, "4"),
     (KEY_5, "5"), (KEY_6, "6"), (KEY_7, "7"), (KEY_8, "8"), (KEY_9, "9"),
     (KEY_0, "0"), (KEY_MINUS, "-"), (KEY_EQUAL, "="), (KEY_BACKSPACE, "⌫", 4)],

    [(KEY_TAB, "Tab", 3), (KEY_Q, "Q"), (KEY_W, "W"), (KEY_E, "E"), (KEY_R, "R"),
     (KEY_T, "T"), (KEY_Y, "Y"), (KEY_U, "U"), (KEY_I, "I"), (KEY_O, "O"),
     (KEY_P, "P"), (KEY_LEFTBRACE, "["), (KEY_RIGHTBRACE, "]"), (KEY_BACKSLASH, "\\", 3)],

    [(KEY_CAPSLOCK, "Caps", 4), (KEY_A, "A"), (KEY_S, "S"), (KEY_D, "D"), (KEY_F, "F"),
     (KEY_G, "G"), (KEY_H, "H"), (KEY_J, "J"), (KEY_K, "K"), (KEY_L, "L"),
     (KEY_SEMICOLON, ";"), (KEY_APOSTROPHE, "'"), (KEY_ENTER, "Enter", 4)],

    [(KEY_LEFTSHIFT, "Shift", 5), (KEY_Z, "Z"), (KEY_X, "X"), (KEY_C, "C"), (KEY_V, "V"),
     (KEY_B, "B"), (KEY_N, "N"), (KEY_M, "M"), (KEY_COMMA, ","), (KEY_DOT, "."),
     (KEY_SLASH, "/"), (KEY_RIGHTSHIFT, "Shift", 5)],

    [(KEY_LEFTCTRL, "Ctrl", 3), (KEY_LEFTMETA, "OS", 3), (KEY_LEFTALT, "Alt", 3),
     (KEY_SPACE, "Space", 12), (KEY_RIGHTALT, "Alt", 3), (KEY_RIGHTMETA, "OS", 3),
     (KEY_RIGHTCTRL, "Ctrl", 3)],
]

base_compact_rows = [
    [(KEY_ESC, "Esc"), (KEY_F1, "F1"), (KEY_F2, "F2"), (KEY_F3, "F3"),
     (KEY_F4, "F4"), (KEY_F5, "F5"), (KEY_F6, "F6"), (KEY_F7, "F7"),
     (KEY_F8, "F8"), (KEY_F9, "F9"), (KEY_F10, "F10"), (KEY_F11, "F11"),
     (KEY_F12, "F12"), (KEY_INSERT, "Ins", 2), (KEY_DELETE, "Del", 2),
     (KEY_PAGEUP, "PgUp")],

    [(KEY_GRAVE, "`"), (KEY_1, "1"), (KEY_2, "2"), (KEY_3, "3"), (KEY_4, "4"),
     (KEY_5, "5"), (KEY_6, "6"), (KEY_7, "7"), (KEY_8, "8"), (KEY_9, "9"),
     (KEY_0, "0"), (KEY_MINUS, "-"), (KEY_EQUAL, "="), (KEY_BACKSPACE, "⌫", 4),
     (KEY_PAGEDOWN, "PgDn")],

    [(KEY_TAB, "Tab", 3), (KEY_Q, "Q"), (KEY_W, "W"), (KEY_E, "E"), (KEY_R, "R"),
     (KEY_T, "T"), (KEY_Y, "Y"), (KEY_U, "U"), (KEY_I, "I"), (KEY_O, "O"),
     (KEY_P, "P"), (KEY_LEFTBRACE, "["), (KEY_RIGHTBRACE, "]"),
     (KEY_BACKSLASH, "\\", 3), (KEY_HOME, "Home")],

    [(KEY_CAPSLOCK, "Caps", 4), (KEY_A, "A"), (KEY_S, "S"), (KEY_D, "D"), (KEY_F, "F"),
     (KEY_G, "G"), (KEY_H, "H"), (KEY_J, "J"), (KEY_K, "K"), (KEY_L, "L"),
     (KEY_SEMICOLON, ";"), (KEY_APOSTROPHE, "'"), (KEY_ENTER, "Enter", 4),
     (KEY_END, "End")],

    [(KEY_LEFTSHIFT, "Shift", 5), (KEY_Z, "Z"), (KEY_X, "X"), (KEY_C, "C"), (KEY_V, "V"),
     (KEY_B, "B"), (KEY_N, "N"), (KEY_M, "M"), (KEY_COMMA, ","), (KEY_DOT, "."),
     (KEY_SLASH, "/"), (KEY_RIGHTSHIFT, "Shift", 5), (KEY_UP, "↑", 2)],

    [(KEY_LEFTCTRL, "Ctrl", 3), (KEY_LEFTMETA, "OS", 2), (KEY_LEFTALT, "Alt", 3),
     (KEY_SPACE, "Space", 12), (KEY_RIGHTALT, "Alt", 2), (KEY_RIGHTMETA, "OS", 2),
     (KEY_RIGHTCTRL, "Ctrl", 2), (KEY_LEFT, "←"), (KEY_RIGHT, "→"), (KEY_DOWN, "↓")],
]

LAYOUTS = {
    "Full":    {"base": base_60_rows,      "fn": True,  "sys": True,  "nav": True,  "num": True},
    "TKL":     {"base": base_60_rows,      "fn": True,  "sys": True,  "nav": True,  "num": False},
    "60%":     {"base": base_60_rows,      "fn": False, "sys": False, "nav": False, "num": False},
    "Compact": {"base": base_compact_rows, "fn": False, "sys": False, "nav": False, "num": False},
    "Numpad":  {"base": None,              "fn": False, "sys": False, "nav": False, "num": True},
}

# Maps keys to their shifted symbols
shift_dict = {
    KEY_GRAVE: "~", KEY_1: "!", KEY_2: "@", KEY_3: "#", KEY_4: "$",
    KEY_5: "%", KEY_6: "^", KEY_7: "&", KEY_8: "*", KEY_9: "(",
    KEY_0: ")", KEY_MINUS: "_", KEY_EQUAL: "+",
    KEY_LEFTBRACE: "{", KEY_RIGHTBRACE: "}", KEY_BACKSLASH: "|",
    KEY_SEMICOLON: ":", KEY_APOSTROPHE: '"',
    KEY_COMMA: "<", KEY_DOT: ">", KEY_SLASH: "?"
}

# Maps numpad keys to their numlock-off labels
numlock_dict = {
    KEY_KP0: "Del", KEY_KP1: "End", KEY_KP2: "⬇", KEY_KP3: "PgDn",
    KEY_KP4: "⬅", KEY_KP5: " ", KEY_KP6: "➡", KEY_KP7: "Home", KEY_KP8: "⬆",
    KEY_KP9: "PgUp", KEY_KPDOT: "Ins"
}


class VirtualKeyboard(Gtk.Window):
    def __init__(self):
        super().__init__(title="Virtual Keyboard", name="toplevel")

        self.set_border_width(0)
        self.set_resizable(True)
        self.set_keep_above(True)
        self.set_modal(False)
        self.set_focus_on_map(False)
        self.set_can_focus(False)
        self.set_accept_focus(False)

        self.CONFIG_DIR = os.path.expanduser("~/.config/vboard")
        self.CONFIG_FILE = os.path.join(self.CONFIG_DIR, "settings.conf")
        self.config = configparser.ConfigParser()

        self.bg_color = "0,0,0"
        self.opacity = "0.90"
        self.current_layout = "Full"
        self.layout_sizes = {name: (0, 0) for name in LAYOUTS}
        self.read_settings()
        self.text_color = self.get_text_color(self.bg_color)
        self.outline_color = self.get_outline_color(self.bg_color)

        self.modifiers = {
            KEY_LEFTSHIFT: MOD_OFF, KEY_RIGHTSHIFT: MOD_OFF,
            KEY_LEFTCTRL: MOD_OFF,  KEY_RIGHTCTRL: MOD_OFF,
            KEY_LEFTALT: MOD_OFF,   KEY_RIGHTALT: MOD_OFF,
            KEY_LEFTMETA: MOD_OFF,  KEY_RIGHTMETA: MOD_OFF,
            KEY_CAPSLOCK: MOD_OFF,
            KEY_NUMLOCK: MOD_OFF,
        }

        self.colors = [
            ("Black", "0,0,0"), ("Red", "255,0,0"), ("Pink", "255,105,183"),
            ("White", "255,255,255"), ("Green", "0,255,0"), ("Blue", "0,0,110"),
            ("Gray", "128,128,128"), ("Dark Gray", "64,64,64"), ("Orange", "255,165,0"),
            ("Yellow", "255,255,0"), ("Purple", "128,0,128"), ("Cyan", "0,255,255"),
            ("Teal", "0,128,128"), ("Brown", "139,69,19"), ("Gold", "255,215,0"),
            ("Silver", "192,192,192"), ("Turquoise", "64,224,208"), ("Magenta", "255,0,255"),
            ("Olive", "128,128,0"), ("Maroon", "128,0,0"), ("Indigo", "75,0,130"),
            ("Beige", "245,245,220"), ("Lavender", "230,230,250"),
        ]

        self.header = Gtk.HeaderBar()
        self.header.set_show_close_button(True)
        self.set_titlebar(self.header)
        self.set_default_icon_name("preferences-desktop-keyboard")
        self.header.set_decoration_layout(":minimize,close")

        self.apply_css()
        self.modifier_buttons = {}
        self.row_buttons = []
        self.button_keys = {}
        self.vbox = None
        self.build_layout(self.current_layout)

        # Right-click menu on the window
        self.connect("button-press-event", self.on_button_press_event)

    def build_context_menu(self):
        menu = Gtk.Menu()

        # Layout submenu
        layout_item = Gtk.MenuItem(label="Layout")
        layout_sub = Gtk.Menu()
        layout_group = []
        for name in LAYOUTS:
            item = Gtk.RadioMenuItem.new_with_label(layout_group, name)
            layout_group = item.get_group()
            if name == self.current_layout:
                item.set_active(True)
            item.connect("activate", self.on_menu_layout, name)
            layout_sub.append(item)
        layout_item.set_submenu(layout_sub)
        menu.append(layout_item)

        # Background color submenu
        color_item = Gtk.MenuItem(label="Background")
        color_sub = Gtk.Menu()
        for label, color in self.colors:
            item = Gtk.MenuItem(label=label)
            item.connect("activate", self.on_menu_color, color)
            color_sub.append(item)
        color_item.set_submenu(color_sub)
        menu.append(color_item)

        # Opacity submenu
        opacity_item = Gtk.MenuItem(label=f"Opacity: {self.opacity}")
        opacity_sub = Gtk.Menu()
        for val in ["1.0", "0.95", "0.90", "0.85", "0.80", "0.75", "0.70",
                    "0.60", "0.50", "0.40", "0.30", "0.20"]:
            item = Gtk.MenuItem(label=val)
            item.connect("activate", self.on_menu_opacity, val)
            opacity_sub.append(item)
        opacity_item.set_submenu(opacity_sub)
        menu.append(opacity_item)

        menu.append(Gtk.SeparatorMenuItem())

        wm_item = Gtk.MenuItem(label="Window Menu")
        wm_item.connect("activate", self.on_menu_window_menu)
        menu.append(wm_item)

        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", Gtk.main_quit)
        menu.append(quit_item)

        menu.show_all()
        return menu

    def on_button_press_event(self, widget, event):
        if event.button == 3:  # right click
            self._last_event = event.copy()
            menu = self.build_context_menu()
            menu.popup_at_pointer(event)
            return True
        return False

    def on_menu_window_menu(self, item):
        self.get_window().show_window_menu(self._last_event)

    def on_menu_layout(self, item, name):
        if item.get_active() and name != self.current_layout:
            self.current_layout = name
            self.build_layout(name)

    def on_menu_color(self, item, color):
        self.bg_color = color
        self.text_color = self.get_text_color(self.bg_color)
        self.outline_color = self.get_outline_color(self.bg_color)
        self.apply_css()

    def on_menu_opacity(self, item, val):
        self.opacity = val
        self.apply_css()

    def build_layout(self, name):
        layout = LAYOUTS[name]

        if self.vbox is not None:
            self.remove(self.vbox)
            self.vbox.destroy()

        self.row_buttons = []
        self.button_keys = {}
        self.modifier_buttons = {}

        def make_grid():
            g = Gtk.Grid()
            g.set_row_homogeneous(True)
            g.set_column_homogeneous(True)
            g.set_name("grid")
            return g

        grid_main = make_grid() if layout["base"] else None
        hbox_main = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=HBOX_SPACING)
        if grid_main:
            hbox_main.pack_start(grid_main, True, True, 0)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=VBOX_SPACING)
        self.vbox.set_margin_start(8)
        self.vbox.set_margin_end(8)
        self.vbox.set_margin_bottom(8)
        # Collect all keys for device (always from all row groups regardless of layout)
        all_row_groups = [fn_rows, sys_rows, base_60_rows, base_compact_rows, navigation_rows, numpad_rows]
        all_keys = set()
        self.key_labels = {}
        for group in all_row_groups:
            for row in group:
                for entry in row:
                    if isinstance(entry, tuple):
                        all_keys.add(entry[0])
                        self.key_labels[entry[0]] = entry[1]
        if not hasattr(self, 'device'):
            self.device = Device(all_keys)

        if layout["fn"]:
            grid_fn = make_grid()
            grid_sys = make_grid()
            grid_fn_pad = make_grid()
            hbox_top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=HBOX_SPACING)
            hbox_top.pack_start(grid_fn, True, True, 0)
            if layout["sys"]:
                hbox_top.pack_start(grid_sys, False, False, 0)
            if layout["num"]:
                hbox_top.pack_start(grid_fn_pad, False, False, 0)
            self.vbox.pack_start(hbox_top, False, False, 0)

        if layout["nav"]:
            grid_nav = make_grid()
            hbox_main.pack_start(grid_nav, False, False, 0)

        if layout["num"]:
            grid_num = make_grid()
            expand = not layout["base"] and not layout["nav"]
            hbox_main.pack_start(grid_num, expand, expand, 0)

        self.vbox.pack_start(hbox_main, True, True, 0)
        self.add(self.vbox)

        ref_fn = ref_main = ref_sys = ref_nav = None

        if layout["fn"]:
            i = len(self.row_buttons)
            for row_index, row in enumerate(fn_rows):
                self.create_row(grid_fn, row_index, row)
            ref_fn = self.row_buttons[i]

            if layout["sys"]:
                i = len(self.row_buttons)
                for row_index, row in enumerate(sys_rows):
                    self.create_row(grid_sys, row_index, row)
                ref_sys = self.row_buttons[i]

            if layout["num"]:
                for row_index, row in enumerate(fn_pad_rows):
                    self.create_row(grid_fn_pad, row_index, row)

        if layout["base"]:
            i = len(self.row_buttons)
            for row_index, row in enumerate(layout["base"]):
                self.create_row(grid_main, row_index, row)
            ref_main = self.row_buttons[i]

        if layout["nav"]:
            i = len(self.row_buttons)
            for row_index, row in enumerate(navigation_rows):
                self.create_row(grid_nav, row_index, row)
            ref_nav = self.row_buttons[i]

        if layout["num"]:
            for row_index, row in enumerate(numpad_rows):
                self.create_row(grid_num, row_index, row)

            if layout["fn"]:
                sg_pad = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
                sg_pad.add_widget(grid_fn_pad)
                sg_pad.add_widget(grid_num)

        if ref_fn and ref_main:
            sg_main = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
            sg_main.add_widget(ref_fn)
            sg_main.add_widget(ref_main)

        if ref_sys and ref_nav:
            sg_side = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
            sg_side.add_widget(ref_sys)
            sg_side.add_widget(ref_nav)

        self.sync_capslock()
        self.sync_numlock()

        self.vbox.show_all()

        w, h = self.layout_sizes.get(name, (0, 0))
        if w and h:
            self.resize(w, h)
        else:
            self.resize(1, 1)

    def on_resize(self, widget, event):
        w, h = self.get_size()
        self.layout_sizes[self.current_layout] = (w, h)

    def get_capslock_state(self):
        output = subprocess.check_output("xset q", shell=True).decode()
        return "Caps Lock:   on" in output

    def get_numlock_state(self):
        output = subprocess.check_output("xset q", shell=True).decode()
        return "Num Lock:    on" in output

    def get_text_color(self, rgb_string):
        r, g, b = [int(x) for x in rgb_string.split(",")]
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return "#1C1C1C" if luminance > 0.5 else "white"

    def get_outline_color(self, rgb_string):
        r, g, b = [int(x) for x in rgb_string.split(",")]
        gray = int(0.299 * r + 0.587 * g + 0.114 * b)
        outline = (gray + 0x40) % 256
        return f"#{outline:02x}{outline:02x}{outline:02x}"

    def apply_css(self):
        provider = Gtk.CssProvider()
        default_font = self.get_style_context().get_property("font", Gtk.StateFlags.NORMAL)
        default_size = default_font.get_size() / 1024
        small = round(default_size * 0.8, 1)
        css = f"""
        headerbar {{
            background-color: rgba({self.bg_color}, {self.opacity});
            border: 0px; box-shadow: none; min-width: 0px; min-height: 0px; padding: 0px;
        }}
        headerbar button {{ min-width: 0px; min-height: 0px; padding: 2px; border: 0px; margin: 0px; }}
        headerbar .titlebutton {{ min-width: 16px; min-height: 16px; }}
        headerbar button label {{ color: {self.text_color}; }}
        #toplevel {{ background-color: rgba({self.bg_color}, {self.opacity}); }}
        #grid button label {{ color: {self.text_color}; }}
        #grid button {{ border: 1px solid {self.outline_color}; background-image: none; padding: 0px; margin: 0px; min-width: 0px; min-height: 0px; }}
        button {{ background-color: transparent; color: {self.text_color}; }}
        #grid button:hover {{ border: 1px solid #00CACB; }}
        #grid button.pressed, #grid button.pressed:hover {{ border: 1px solid {self.text_color}; }}
        #grid button.locked, #grid button.locked:hover {{ border: 1px solid {self.text_color}; background-color: {self.text_color}; }}
        #grid button.locked label, #grid button.locked:hover label {{ color: rgba({self.bg_color}, {self.opacity}); }}
        #grid button:active {{ background-color: {self.text_color}; }}
        #grid button:active label {{ color: rgba({self.bg_color}, {self.opacity}); }}
        tooltip {{ color: white; padding: 5px; }}
        #grid button.small-key label {{ font-size: {small}pt; }}
        #grid button.numlock-label label {{ font-size: {small}pt; }}
        """
        try:
            provider.load_from_data(css.encode("utf-8"))
        except GLib.GError as e:
            print(f"CSS Error: {e.message}")
        Gtk.StyleContext.add_provider_for_screen(self.get_screen(), provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def create_spacer(self, grid, col, row_index, width=1):
        spacer = Gtk.Label(label="")
        grid.attach(spacer, col, row_index, width, 1)
        return width

    def create_row(self, grid, row_index, row):
        col = 0
        for entry in row:
            if isinstance(entry, int):  # plain int = gap
                col += self.create_spacer(grid, col, row_index, entry)
                continue

            key = entry[0]
            label = entry[1]
            width = entry[2] if len(entry) >= 3 else 2
            rowspan = entry[3] if len(entry) >= 4 else 1

            button = Gtk.Button(label=label)
            if len(label) > 1:  # small font for multi-character labels
                button.get_style_context().add_class('small-key')
            button.connect("pressed", self.on_key_press, key)
            button.connect("released", self.on_key_release)
            button.connect("leave-notify-event", self.on_key_release)
            self.row_buttons.append(button)
            self.button_keys[button] = key
            if key in self.modifiers:
                self.modifier_buttons[key] = button
            grid.attach(button, col, row_index, width, rowspan)
            col += width

    def update_label_shift(self, show_symbols):
        for button in self.row_buttons:
            key = self.button_keys[button]
            if show_symbols and key in shift_dict:
                button.set_label(shift_dict[key])
            elif not show_symbols:
                button.set_label(self.key_labels[key])

    def update_label_numlock(self, numlock_off):
        for button in self.row_buttons:
            key = self.button_keys[button]
            if numlock_off and key in numlock_dict:
                button.set_label(numlock_dict[key])
                button.get_style_context().add_class('numlock-label')
            elif not numlock_off and key in numlock_dict:
                button.set_label(self.key_labels[key])
                button.get_style_context().remove_class('numlock-label')

    def update_modifier(self, key_event, state):
        old_state = self.modifiers[key_event]
        self.modifiers[key_event] = state
        ctx = self.modifier_buttons[key_event].get_style_context()
        ctx.remove_class('pressed')
        ctx.remove_class('locked')
        if state == MOD_ON:
            ctx.add_class('pressed')
        elif state == MOD_LOCKED:
            ctx.add_class('locked')
            if key_event not in (KEY_CAPSLOCK, KEY_NUMLOCK):
                self.device.emit(key_event, 1)
        if old_state == MOD_LOCKED and state == MOD_OFF:
            if key_event not in (KEY_CAPSLOCK, KEY_NUMLOCK):
                self.device.emit(key_event, 0)

    def sync_capslock(self):
        state = MOD_ON if self.get_capslock_state() else MOD_OFF
        if KEY_CAPSLOCK in self.modifier_buttons:
            self.update_modifier(KEY_CAPSLOCK, state)
        else:
            self.modifiers[KEY_CAPSLOCK] = state
        return False

    def sync_numlock(self):
        on = self.get_numlock_state()
        state = MOD_ON if on else MOD_OFF
        if KEY_NUMLOCK in self.modifier_buttons:
            self.update_modifier(KEY_NUMLOCK, state)
            self.update_label_numlock(not on)
        else:
            self.modifiers[KEY_NUMLOCK] = state
        return False

    def on_key_press(self, widget, key_event):
        if key_event == KEY_CAPSLOCK:
            self.device.emit(KEY_CAPSLOCK, 1)
            self.device.emit(KEY_CAPSLOCK, 0)
            GLib.timeout_add(50, self.sync_capslock)
            return
        if key_event == KEY_NUMLOCK:
            self.device.emit(KEY_NUMLOCK, 1)
            self.device.emit(KEY_NUMLOCK, 0)
            GLib.timeout_add(50, self.sync_numlock)
            return

        if key_event in self.modifiers:
            current = self.modifiers[key_event]
            next_state = [MOD_ON, MOD_LOCKED, MOD_OFF][current]
            self.update_modifier(key_event, next_state)

            if self.modifiers[KEY_LEFTSHIFT] and self.modifiers[KEY_RIGHTSHIFT]:
                self.update_modifier(KEY_LEFTSHIFT, MOD_OFF)
                self.update_modifier(KEY_RIGHTSHIFT, MOD_OFF)

            shift_active = self.modifiers[KEY_LEFTSHIFT] or self.modifiers[KEY_RIGHTSHIFT]
            self.update_label_shift(bool(shift_active))
            return

        for mod_key, state in self.modifiers.items():
            if state == MOD_ON and mod_key not in (KEY_CAPSLOCK, KEY_NUMLOCK):
                self.device.emit(mod_key, 1)
        self.device.emit(key_event, 1)
        self.pressed_key = key_event

    def on_key_release(self, widget, *args):
        if not hasattr(self, 'pressed_key'):
            return
        key_event = self.pressed_key
        del self.pressed_key

        self.device.emit(key_event, 0)

        for mod_key, state in self.modifiers.items():
            if state == MOD_ON and mod_key not in (KEY_CAPSLOCK, KEY_NUMLOCK):
                self.device.emit(mod_key, 0)
                self.update_modifier(mod_key, MOD_OFF)

        self.update_label_shift(False)

    def read_settings(self):
        try:
            os.makedirs(self.CONFIG_DIR, exist_ok=True)
        except PermissionError:
            print("Warning: No permission to create the config directory.")
        try:
            if os.path.exists(self.CONFIG_FILE):
                self.config.read(self.CONFIG_FILE)
                self.bg_color = self.config.get("DEFAULT", "bg_color", fallback="0,0,0")
                self.opacity = self.config.get("DEFAULT", "opacity", fallback="0.90")
                self.current_layout = self.config.get("DEFAULT", "layout", fallback="Full")
                for name in LAYOUTS:
                    w = self.config.getint("SIZES", f"{name}_width", fallback=0)
                    h = self.config.getint("SIZES", f"{name}_height", fallback=0)
                    self.layout_sizes[name] = (w, h)
        except configparser.Error as e:
            print(f"Warning: Could not read config file ({e}).")

    def save_settings(self):
        self.config["DEFAULT"] = {
            "bg_color": self.bg_color,
            "opacity": self.opacity,
            "layout": self.current_layout,
        }
        self.config["SIZES"] = {}
        for name, (w, h) in self.layout_sizes.items():
            self.config["SIZES"][f"{name}_width"] = str(w)
            self.config["SIZES"][f"{name}_height"] = str(h)
        try:
            with open(self.CONFIG_FILE, "w") as configfile:
                self.config.write(configfile)
        except (configparser.Error, IOError) as e:
            print(f"Warning: Could not write to config file ({e}).")


if __name__ == "__main__":
    win = VirtualKeyboard()
    win.connect("destroy", Gtk.main_quit)
    win.connect("destroy", lambda w: win.save_settings())
    win.show_all()
    win.connect("configure-event", win.on_resize)
    Gtk.main()
