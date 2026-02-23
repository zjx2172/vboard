#!/usr/bin/env python3

import gi
import uinput
import time
import os
import configparser

os.environ['GDK_BACKEND'] = 'x11'

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib

KB_GAP = -1  # sentinel value for gaps; safe because uinput keys are tuples, never ints

from uinput import Device, KEY_ESC, KEY_F1, KEY_F2, KEY_F3, KEY_F4, KEY_F5, KEY_F6, KEY_F7, KEY_F8, KEY_F9, KEY_F10, KEY_F11, KEY_F12, KEY_GRAVE, KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7, KEY_8, KEY_9, KEY_0, KEY_MINUS, KEY_EQUAL, KEY_BACKSPACE, KEY_TAB, KEY_Q, KEY_W, KEY_E, KEY_R, KEY_T, KEY_Y, KEY_U, KEY_I, KEY_O, KEY_P, KEY_LEFTBRACE, KEY_RIGHTBRACE, KEY_BACKSLASH, KEY_CAPSLOCK, KEY_A, KEY_S, KEY_D, KEY_F, KEY_G, KEY_H, KEY_J, KEY_K, KEY_L, KEY_SEMICOLON, KEY_APOSTROPHE, KEY_ENTER, KEY_LEFTSHIFT, KEY_Z, KEY_X, KEY_C, KEY_V, KEY_B, KEY_N, KEY_M, KEY_COMMA, KEY_DOT, KEY_SLASH, KEY_RIGHTSHIFT, KEY_LEFTCTRL, KEY_LEFTMETA, KEY_LEFTALT, KEY_SPACE, KEY_RIGHTALT, KEY_RIGHTMETA, KEY_RIGHTCTRL, KEY_SYSRQ, KEY_SCROLLLOCK, KEY_PAUSE, KEY_INSERT, KEY_HOME, KEY_PAGEUP, KEY_DELETE, KEY_END, KEY_PAGEDOWN, KEY_UP, KEY_LEFT, KEY_DOWN, KEY_RIGHT, KEY_NUMLOCK, KEY_KP0, KEY_KP1, KEY_KP2, KEY_KP3, KEY_KP4, KEY_KP5, KEY_KP6, KEY_KP7, KEY_KP8, KEY_KP9, KEY_KPPLUS, KEY_KPMINUS, KEY_KPASTERISK, KEY_KPSLASH, KEY_KPDOT, KEY_KPENTER

keys_dict = {
    KEY_ESC: "Esc",
    KEY_F1: "F1", KEY_F2: "F2", KEY_F3: "F3", KEY_F4: "F4",
    KEY_F5: "F5", KEY_F6: "F6", KEY_F7: "F7", KEY_F8: "F8",
    KEY_F9: "F9", KEY_F10: "F10", KEY_F11: "F11", KEY_F12: "F12",

    KEY_GRAVE: "`", KEY_1: "1", KEY_2: "2", KEY_3: "3", KEY_4: "4",
    KEY_5: "5", KEY_6: "6", KEY_7: "7", KEY_8: "8", KEY_9: "9",
    KEY_0: "0", KEY_MINUS: "-", KEY_EQUAL: "=", KEY_BACKSPACE: "⌫",

    KEY_TAB: "Tab", KEY_Q: "Q", KEY_W: "W", KEY_E: "E", KEY_R: "R",
    KEY_T: "T", KEY_Y: "Y", KEY_U: "U", KEY_I: "I", KEY_O: "O",
    KEY_P: "P", KEY_LEFTBRACE: "[", KEY_RIGHTBRACE: "]", KEY_BACKSLASH: "\\",

    KEY_CAPSLOCK: "Caps", KEY_A: "A", KEY_S: "S", KEY_D: "D",
    KEY_F: "F", KEY_G: "G", KEY_H: "H", KEY_J: "J", KEY_K: "K",
    KEY_L: "L", KEY_SEMICOLON: ";", KEY_APOSTROPHE: "'", KEY_ENTER: "Enter",

    KEY_LEFTSHIFT: "Shift", KEY_Z: "Z", KEY_X: "X", KEY_C: "C",
    KEY_V: "V", KEY_B: "B", KEY_N: "N", KEY_M: "M",
    KEY_COMMA: ",", KEY_DOT: ".", KEY_SLASH: "/", KEY_RIGHTSHIFT: "Shift",

    KEY_LEFTCTRL: "Ctrl", KEY_LEFTMETA: "OS", KEY_LEFTALT: "Alt",
    KEY_SPACE: "Space", KEY_RIGHTALT: "Alt", KEY_RIGHTMETA: "OS", KEY_RIGHTCTRL: "Ctrl",

    KEY_SYSRQ: "PrtScr", KEY_SCROLLLOCK: "ScrLk", KEY_PAUSE: "Pause",

    KEY_INSERT: "Ins", KEY_HOME: "Home", KEY_PAGEUP: "PgUp",
    KEY_DELETE: "Del", KEY_END: "End", KEY_PAGEDOWN: "PgDn",
    KEY_UP: "↑", KEY_LEFT: "←", KEY_DOWN: "↓", KEY_RIGHT: "→",

    KEY_NUMLOCK: "Num",
    KEY_KP0: "0", KEY_KP1: "1", KEY_KP2: "2", KEY_KP3: "3",
    KEY_KP4: "4", KEY_KP5: "5", KEY_KP6: "6", KEY_KP7: "7",
    KEY_KP8: "8", KEY_KP9: "9",
    KEY_KPPLUS: "+", KEY_KPMINUS: "-", KEY_KPASTERISK: "*",
    KEY_KPSLASH: "/", KEY_KPDOT: ".", KEY_KPENTER: "⏎",
}

shift_dict = {
    KEY_GRAVE: "~", KEY_1: "!", KEY_2: "@", KEY_3: "#", KEY_4: "$",
    KEY_5: "%", KEY_6: "^", KEY_7: "&", KEY_8: "*", KEY_9: "(",
    KEY_0: ")", KEY_MINUS: "_", KEY_EQUAL: "+",
    KEY_LEFTBRACE: "{", KEY_RIGHTBRACE: "}", KEY_BACKSLASH: "|",
    KEY_SEMICOLON: ":", KEY_APOSTROPHE: '"',
    KEY_COMMA: "<", KEY_DOT: ">", KEY_SLASH: "?"
}

numlock_dict = {
    KEY_KP0: "Del", KEY_KP1: "End", KEY_KP2: "⬇", KEY_KP3: "PgDn",
    KEY_KP4: "⬅", KEY_KP6: "➡", KEY_KP7: "Hm", KEY_KP8: "⬆",
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
        self.width = 0
        self.height = 0

        self.CONFIG_DIR = os.path.expanduser("~/.config/vboard")
        self.CONFIG_FILE = os.path.join(self.CONFIG_DIR, "settings.conf")
        self.config = configparser.ConfigParser()

        self.bg_color = "0, 0, 0"
        self.opacity = "0.90"
        self.text_color = "white"
        self.read_settings()

        self.modifiers = {
            KEY_LEFTSHIFT: False, KEY_RIGHTSHIFT: False,
            KEY_LEFTCTRL: False, KEY_RIGHTCTRL: False,
            KEY_LEFTALT: False, KEY_RIGHTALT: False,
            KEY_LEFTMETA: False, KEY_RIGHTMETA: False,
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

        if self.width != 0:
            self.set_default_size(self.width, self.height)

        self.header = Gtk.HeaderBar()
        self.header.set_show_close_button(True)
        self.buttons = []
        self.modifier_buttons = {}
        self.row_buttons = []
        self.color_combobox = Gtk.ComboBoxText()
        self.set_titlebar(self.header)
        self.set_default_icon_name("preferences-desktop-keyboard")
        self.header.set_decoration_layout(":minimize,maximize,close")

        self.create_settings()

        grid = Gtk.Grid()
        grid.set_row_homogeneous(True)
        grid.set_column_homogeneous(True)
        grid.set_margin_start(3)
        grid.set_margin_end(3)
        grid.set_name("grid")
        self.add(grid)
        self.apply_css()
        self.device = Device(list(keys_dict.keys()))
        self.button_keys = {}

        function_row = [
            KEY_ESC, (KB_GAP, 1), KEY_F1, KEY_F2, KEY_F3, KEY_F4,
            (KB_GAP, 1), KEY_F5, KEY_F6, KEY_F7, KEY_F8,
            (KB_GAP, 1), KEY_F9, KEY_F10, KEY_F11, KEY_F12, (KB_GAP, 1)
        ]

        navigation_rows = [
            [KEY_SYSRQ, KEY_SCROLLLOCK, KEY_PAUSE],
            [KEY_INSERT, KEY_HOME, KEY_PAGEUP],
            [KEY_DELETE, KEY_END, KEY_PAGEDOWN],
            [(KB_GAP, 6)],
            [(KB_GAP, 2), KEY_UP, (KB_GAP, 2)],
            [KEY_LEFT, KEY_DOWN, KEY_RIGHT],
        ]

        numpad_rows = [
            [(KB_GAP, 8)],
            [KEY_NUMLOCK, KEY_KPSLASH, KEY_KPASTERISK, KEY_KPMINUS],
            [KEY_KP7, KEY_KP8, KEY_KP9, KEY_KPPLUS],
            [KEY_KP4, KEY_KP5, KEY_KP6, (KB_GAP, 2)],
            [KEY_KP1, KEY_KP2, KEY_KP3, (KB_GAP, 2)],
            [(KEY_KP0, 4), KEY_KPDOT, KEY_KPENTER],
        ]

        base_rows = [
            [KEY_GRAVE, KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7, KEY_8, KEY_9, KEY_0, KEY_MINUS, KEY_EQUAL, (KEY_BACKSPACE, 4)],
            [(KEY_TAB, 3), KEY_Q, KEY_W, KEY_E, KEY_R, KEY_T, KEY_Y, KEY_U, KEY_I, KEY_O, KEY_P, KEY_LEFTBRACE, KEY_RIGHTBRACE, (KEY_BACKSLASH, 3)],
            [(KEY_CAPSLOCK, 4), KEY_A, KEY_S, KEY_D, KEY_F, KEY_G, KEY_H, KEY_J, KEY_K, KEY_L, KEY_SEMICOLON, KEY_APOSTROPHE, (KEY_ENTER, 4)],
            [(KEY_LEFTSHIFT, 5), KEY_Z, KEY_X, KEY_C, KEY_V, KEY_B, KEY_N, KEY_M, KEY_COMMA, KEY_DOT, KEY_SLASH, (KEY_RIGHTSHIFT, 5)],
            [(KEY_LEFTCTRL, 3), (KEY_LEFTMETA, 3), (KEY_LEFTALT, 3), (KEY_SPACE, 12), (KEY_RIGHTALT, 3), (KEY_RIGHTMETA, 3), (KEY_RIGHTCTRL, 3)],
        ]

        rows = [function_row] + base_rows
        for row_num in range(len(rows)):
            rows[row_num] = rows[row_num] + [(KB_GAP, 1)] + navigation_rows[row_num]
        for row_num in range(len(rows)):
            rows[row_num] = rows[row_num] + [(KB_GAP, 1)] + numpad_rows[row_num]

        for row_index, row in enumerate(rows):
            self.create_row(grid, row_index, row)

    def create_settings(self):
        self.create_button("☰", self.change_visibility, callbacks=1)
        self.create_button("+", self.change_opacity, True, 2)
        self.create_button("-", self.change_opacity, False, 2)
        self.create_button(f"{self.opacity}")
        self.color_combobox.append_text("Change Background")
        self.color_combobox.set_active(0)
        self.color_combobox.connect("changed", self.change_color)
        self.color_combobox.set_name("combobox")
        self.header.add(self.color_combobox)
        for label, color in self.colors:
            self.color_combobox.append_text(label)

    def on_resize(self, widget, event):
        self.width, self.height = self.get_size()

    def create_button(self, label_="", callback=None, callback2=None, callbacks=0):
        button = Gtk.Button(label=label_)
        button.set_name("headbar-button")
        if callbacks == 1:
            button.connect("clicked", callback)
        elif callbacks == 2:
            button.connect("clicked", callback, callback2)
        if label_ == self.opacity:
            self.opacity_btn = button
            self.opacity_btn.set_tooltip_text("opacity")
        self.header.add(button)
        self.buttons.append(button)

    def change_visibility(self, widget=None):
        for button in self.buttons:
            if button.get_label() != "☰":
                button.set_visible(not button.get_visible())
        self.color_combobox.set_visible(not self.color_combobox.get_visible())

    def change_color(self, widget):
        label = self.color_combobox.get_active_text()
        for label_, color_ in self.colors:
            if label_ == label:
                self.bg_color = color_
        if self.bg_color in {"255,255,255", "0,255,0", "255,255,0", "245,245,220", "230,230,250", "255,215,0"}:
            self.text_color = "#1C1C1C"
        else:
            self.text_color = "white"
        self.apply_css()

    def change_opacity(self, widget, boolean):
        if boolean:
            self.opacity = str(round(min(1.0, float(self.opacity) + 0.01), 2))
        else:
            self.opacity = str(round(max(0.0, float(self.opacity) - 0.01), 2))
        self.opacity_btn.set_label(f"{self.opacity}")
        self.apply_css()

    def apply_css(self):
        provider = Gtk.CssProvider()
        css = f"""
        headerbar {{
            background-color: rgba({self.bg_color}, {self.opacity});
            border: 0px; box-shadow: none;
        }}
        headerbar button {{ min-width: 10px; padding: 0px; border: 0px; margin: 0px; }}
        headerbar .titlebutton {{ min-width: 50px; min-height: 40px }}
        headerbar button label {{ color: {self.text_color}; }}
        #headbar-button, #combobox button.combo {{ background-image: none; }}
        #toplevel {{ background-color: rgba({self.bg_color}, {self.opacity}); }}
        #grid button label {{ color: {self.text_color}; }}
        #grid button {{ border: none; background-image: none; padding: 0px; margin: 0px; }}
        button {{ background-color: transparent; color: {self.text_color}; }}
        #grid button:hover {{ border: 1px solid #00CACB; }}
        #grid button.pressed, #grid button.pressed:hover {{ border: 1px solid {self.text_color}; }}
        tooltip {{ color: white; padding: 5px; }}
        #combobox button.combo {{ color: {self.text_color}; padding: 5px; }}
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
            if isinstance(entry, tuple) and len(entry) == 2 and entry[0] == KB_GAP:
                col += self.create_spacer(grid, col, row_index, entry[1])
                continue
            elif isinstance(entry, tuple) and len(entry) == 2 and isinstance(entry[0], tuple):
                key, width = entry
            else:
                key, width = entry, 2

            button = Gtk.Button(label=keys_dict[key])
            button.connect("pressed", self.on_button_press, key)
            button.connect("released", self.on_button_release)
            button.connect("leave-notify-event", self.on_button_release)
            self.row_buttons.append(button)
            self.button_keys[button] = key
            if key in self.modifiers:
                self.modifier_buttons[key] = button
            grid.attach(button, col, row_index, width, 1)
            col += width

    def update_label_shift(self, show_symbols):
        # Rewritten to use button_keys and shift_dict — no hardcoded indices,
        # numpad keys are naturally excluded since they're not in shift_dict
        for button in self.row_buttons:
            key = self.button_keys[button]
            if show_symbols and key in shift_dict:
                button.set_label(shift_dict[key])
            elif not show_symbols and key in shift_dict:
                button.set_label(keys_dict[key])

    def update_modifier(self, key_event, value):
        self.modifiers[key_event] = value
        button = self.modifier_buttons[key_event]
        style_context = button.get_style_context()
        if value:
            style_context.add_class('pressed')
        else:
            style_context.remove_class('pressed')

    def on_button_press(self, widget, key_event):
        if key_event in self.modifiers:
            self.update_modifier(key_event, not self.modifiers[key_event])
            if self.modifiers[KEY_LEFTSHIFT] and self.modifiers[KEY_RIGHTSHIFT]:
                self.update_modifier(KEY_LEFTSHIFT, False)
                self.update_modifier(KEY_RIGHTSHIFT, False)
            if self.modifiers[KEY_LEFTSHIFT] or self.modifiers[KEY_RIGHTSHIFT]:
                self.update_label_shift(True)
            else:
                self.update_label_shift(False)
            return
        self.emit_key(key_event)
        self.delay_source = GLib.timeout_add(400, self.start_repeat, key_event)

    def on_button_release(self, widget, *args):
        if hasattr(self, "delay_source"):
            GLib.source_remove(self.delay_source)
            del self.delay_source
        if hasattr(self, "repeat_source"):
            GLib.source_remove(self.repeat_source)
            del self.repeat_source

    def start_repeat(self, key_event):
        self.repeat_source = GLib.timeout_add(100, self.repeat_key, key_event)
        return False

    def repeat_key(self, key_event):
        self.emit_key(key_event)
        return True

    def emit_key(self, key_event):
        for mod_key, active in self.modifiers.items():
            if active:
                self.device.emit(mod_key, 1)
        self.device.emit(key_event, 1)
        self.device.emit(key_event, 0)
        self.update_label_shift(False)
        for mod_key, active in self.modifiers.items():
            if active:
                self.device.emit(mod_key, 0)
                self.update_modifier(mod_key, False)

    def read_settings(self):
        try:
            os.makedirs(self.CONFIG_DIR, exist_ok=True)
        except PermissionError:
            print("Warning: No permission to create the config directory.")
        try:
            if os.path.exists(self.CONFIG_FILE):
                self.config.read(self.CONFIG_FILE)
                self.bg_color = self.config.get("DEFAULT", "bg_color")
                self.opacity = self.config.get("DEFAULT", "opacity")
                self.text_color = self.config.get("DEFAULT", "text_color", fallback="white")
                self.width = self.config.getint("DEFAULT", "width", fallback=0)
                self.height = self.config.getint("DEFAULT", "height", fallback=0)
        except configparser.Error as e:
            print(f"Warning: Could not read config file ({e}).")

    def save_settings(self):
        self.config["DEFAULT"] = {
            "bg_color": self.bg_color, "opacity": self.opacity,
            "text_color": self.text_color, "width": self.width, "height": self.height
        }
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
    win.change_visibility()
    Gtk.main()
