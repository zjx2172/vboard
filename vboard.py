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
    [(KEY_NUMLOCK, "Num"), (KEY_KPSLASH, "/"), (KEY_KPASTERISK, "*"), (KEY_KPMINUS, "-", 2, 2)],
    [(KEY_KP7, "7"), (KEY_KP8, "8"), (KEY_KP9, "9"), (KEY_KPPLUS, "+", 2, 2)],
    [(KEY_KP4, "4"), (KEY_KP5, "5"), (KEY_KP6, "6")],
    [(KEY_KP1, "1"), (KEY_KP2, "2"), (KEY_KP3, "3"), (KEY_KPENTER, "⏎", 2, 2)],
    [(KEY_KP0, "0", 4), (KEY_KPDOT, ".")],
]

base_rows = [
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

LAYOUTS = {
    "Compact": {"fn": False, "sys": False, "nav": False, "num": False},
    "TKL":     {"fn": True,  "sys": True,  "nav": True,  "num": False},
    "Full":    {"fn": True,  "sys": True,  "nav": True,  "num": True},
}

# Maps keys to their shifted symbols, used to update button labels when shift is active
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

        self.bg_color = "0,0,0"  # background color
        self.opacity = "0.90"
        self.current_layout = "Full"
        self.layout_sizes = {name: (0, 0) for name in LAYOUTS}
        self.read_settings()
        self.text_color = self.get_text_color(self.bg_color)
        self.outline_color = self.get_outline_color(self.bg_color)

        self.modifiers = {
            KEY_LEFTSHIFT: False, KEY_RIGHTSHIFT: False,
            KEY_LEFTCTRL: False, KEY_RIGHTCTRL: False,
            KEY_LEFTALT: False, KEY_RIGHTALT: False,
            KEY_LEFTMETA: False, KEY_RIGHTMETA: False,
            KEY_CAPSLOCK: False,
            KEY_NUMLOCK: False,
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
        self.buttons = []
        self.modifier_buttons = {}
        self.row_buttons = []
        self.color_combobox = Gtk.ComboBoxText()
        self.set_titlebar(self.header)
        self.set_default_icon_name("preferences-desktop-keyboard")
        self.header.set_decoration_layout(":minimize,maximize,close")

        self.create_settings()

        self.apply_css()
        self.button_keys = {}  # maps button widget -> uinput key constant
        self.vbox = None
        self.build_layout(self.current_layout)

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

        self.layout_combobox = Gtk.ComboBoxText()
        self.layout_combobox.set_name("combobox")
        for name in LAYOUTS:
            self.layout_combobox.append_text(name)
        self.layout_combobox.set_active(list(LAYOUTS.keys()).index(self.current_layout))
        self.layout_combobox.connect("changed", self.change_layout)
        self.header.add(self.layout_combobox)

    def change_layout(self, widget):
        name = self.layout_combobox.get_active_text()
        if name and name != self.current_layout:
            self.current_layout = name
            self.build_layout(name)

    def build_layout(self, name):
        layout = LAYOUTS[name]

        # Tear down existing layout
        if self.vbox is not None:
            self.remove(self.vbox)
            self.vbox.destroy()

        self.row_buttons = []
        self.button_keys = {}
        self.modifier_buttons = {}

        def make_grid():
            g = Gtk.Grid()
            g.set_row_homogeneous(True)    # rows resize uniformly
            g.set_column_homogeneous(True)  # columns are equal width
            g.set_name("grid")
            return g

        grid_main = make_grid()
        hbox_main = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=HBOX_SPACING)
        hbox_main.pack_start(grid_main, True, True, 0)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=VBOX_SPACING)

        # Collect all keys for device (always from all row groups regardless of layout)
        all_row_groups = [fn_rows, sys_rows, base_rows, navigation_rows, numpad_rows]
        all_keys = set()
        self.key_labels = {}  # key constant -> default label
        for group in all_row_groups:
            for row in group:
                for entry in row:
                    if isinstance(entry, tuple):
                        all_keys.add(entry[0])
                        self.key_labels[entry[0]] = entry[1]
        if not hasattr(self, 'device'):
            self.device = Device(all_keys)

        # Build top hbox if fn row is included
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

        # Build nav grid
        if layout["nav"]:
            grid_nav = make_grid()
            hbox_main.pack_start(grid_nav, False, False, 0)

        # Build numpad grid
        if layout["num"]:
            grid_num = make_grid()
            hbox_main.pack_start(grid_num, False, False, 0)

        self.vbox.pack_start(hbox_main, True, True, 0)
        self.add(self.vbox)

        # Populate grids, saving reference buttons for SizeGroups
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

        i = len(self.row_buttons)
        for row_index, row in enumerate(base_rows):
            self.create_row(grid_main, row_index, row)
        ref_main = self.row_buttons[i]

        if layout["nav"]:
            i = len(self.row_buttons)
            for row_index, row in enumerate(navigation_rows):
                self.create_row(grid_nav, row_index, row)
            ref_nav = self.row_buttons[i]

        if layout["num"]:
            i = len(self.row_buttons)
            for row_index, row in enumerate(numpad_rows):
                self.create_row(grid_num, row_index, row)

            sg_pad = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
            sg_pad.add_widget(grid_fn_pad)
            sg_pad.add_widget(grid_num)

        # Synchronize column widths between top and main grids
        if ref_fn and ref_main:
            sg_main = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
            sg_main.add_widget(ref_fn)
            sg_main.add_widget(ref_main)

        if ref_sys and ref_nav:
            sg_side = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
            sg_side.add_widget(ref_sys)
            sg_side.add_widget(ref_nav)

        # Initialize CapsLock & Numlock visual state
        self.modifiers[KEY_CAPSLOCK] = self.get_capslock_state()
        if self.modifiers[KEY_CAPSLOCK] and KEY_CAPSLOCK in self.modifier_buttons:
            self.modifier_buttons[KEY_CAPSLOCK].get_style_context().add_class('pressed')

        self.modifiers[KEY_NUMLOCK] = self.get_numlock_state()
        if self.modifiers[KEY_NUMLOCK] and KEY_NUMLOCK in self.modifier_buttons:
            self.modifier_buttons[KEY_NUMLOCK].get_style_context().add_class('pressed')
        elif KEY_NUMLOCK in self.modifier_buttons:
            self.update_label_numlock(True)

        self.vbox.show_all()

        # Restore saved size for this layout, or shrink to fit
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
        self.layout_combobox.set_visible(not self.layout_combobox.get_visible())

    def change_color(self, widget):
        label = self.color_combobox.get_active_text()
        for label_, color_ in self.colors:
            if label_ == label:
                self.bg_color = color_
        self.text_color = self.get_text_color(self.bg_color)
        self.outline_color = self.get_outline_color(self.bg_color)
        self.apply_css()

    def change_opacity(self, widget, boolean):
        if boolean:
            self.opacity = str(round(min(1.0, float(self.opacity) + 0.01), 2))
        else:
            self.opacity = str(round(max(0.0, float(self.opacity) - 0.01), 2))
        self.opacity_btn.set_label(f"{self.opacity}")
        self.apply_css()

    def get_default_font_size(self):
        style = self.get_style_context()
        font = style.get_property("font", Gtk.StateFlags.NORMAL)
        return font.get_size() / 1024  # Pango uses 1024 units per point

    def get_text_color(self, rgb_string):
        r, g, b = [int(x) for x in rgb_string.split(",")]
        # standard luminance formula
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return "#1C1C1C" if luminance > 0.5 else "white"

    def get_outline_color(self, rgb_string):
        r, g, b = [int(x) for x in rgb_string.split(",")]
        gray = int(0.299 * r + 0.587 * g + 0.114 * b)
        outline = (gray + 0x40) % 256
        return f"#{outline:02x}{outline:02x}{outline:02x}"

    def apply_css(self):
        provider = Gtk.CssProvider()
        default = self.get_default_font_size()
        small = round(default * 0.8, 1)
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
        #grid button {{ border: 1px solid {self.outline_color}; background-image: none; padding: 0px; margin: 0px; }}
        button {{ background-color: transparent; color: {self.text_color}; }}
        #grid button:hover {{ border: 1px solid #00CACB; }}
        #grid button.pressed, #grid button.pressed:hover {{ border: 1px solid {self.text_color}; }}
        #grid button:active {{ background-color: {self.text_color}; }}
        #grid button:active label {{ color: rgba({self.bg_color}, {self.opacity}); }}
        tooltip {{ color: white; padding: 5px; }}
        #combobox button.combo {{ color: {self.text_color}; padding: 5px; }}
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
            # plain int = gap
            if isinstance(entry, int):
                col += self.create_spacer(grid, col, row_index, entry)
                continue

            # unpack tuple — label is always second element
            key = entry[0]
            label = entry[1]
            width = entry[2] if len(entry) >= 3 else 2
            rowspan = entry[3] if len(entry) >= 4 else 1
            small = len(label) > 1  # use small font for multi-character labels

            button = Gtk.Button(label=label)
            if small:
                button.get_style_context().add_class('small-key')
            button.connect("pressed", self.on_button_press, key)
            button.connect("released", self.on_button_release)
            button.connect("leave-notify-event", self.on_button_release)
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

    def update_modifier(self, key_event, value):
        self.modifiers[key_event] = value
        button = self.modifier_buttons[key_event]
        style_context = button.get_style_context()
        if value:
            style_context.add_class('pressed')
        else:
            style_context.remove_class('pressed')

    def sync_capslock(self):
        state = self.get_capslock_state()
        self.modifiers[KEY_CAPSLOCK] = state
        style_context = self.modifier_buttons[KEY_CAPSLOCK].get_style_context()
        if state:
            style_context.add_class('pressed')
        else:
            style_context.remove_class('pressed')
        return False  # don't repeat

    def sync_numlock(self):
        state = self.get_numlock_state()
        self.modifiers[KEY_NUMLOCK] = state
        style_context = self.modifier_buttons[KEY_NUMLOCK].get_style_context()
        if state:
            style_context.add_class('pressed')
        else:
            style_context.remove_class('pressed')
        self.update_label_numlock(not state)  # numlock off = navigation labels visible
        return False

    def on_button_press(self, widget, key_event):
        # CapsLock toggles independently — emit and sync state after a short delay
        if key_event == KEY_CAPSLOCK:
            self.device.emit(KEY_CAPSLOCK, 1)
            self.device.emit(KEY_CAPSLOCK, 0)
            GLib.timeout_add(50, self.sync_capslock)
            return

        # Same for Numlock
        if key_event == KEY_NUMLOCK:
            self.device.emit(KEY_NUMLOCK, 1)
            self.device.emit(KEY_NUMLOCK, 0)
            GLib.timeout_add(50, self.sync_numlock)
            return

        # If it's a modifier, toggle state (like Shift, Ctrl, etc.)
        if key_event in self.modifiers:
            self.update_modifier(key_event, not self.modifiers[key_event])

            # prevent both shifts being active at once
            if self.modifiers[KEY_LEFTSHIFT] and self.modifiers[KEY_RIGHTSHIFT]:
                self.update_modifier(KEY_LEFTSHIFT, False)
                self.update_modifier(KEY_RIGHTSHIFT, False)

            # update label state (caps-like effect)
            if self.modifiers[KEY_LEFTSHIFT] or self.modifiers[KEY_RIGHTSHIFT]:
                self.update_label_shift(True)
            else:
                self.update_label_shift(False)
            return  # modifiers don't repeat

        # Fire key once immediately
        self.emit_key(key_event)

        # Start a one-time delay before repeat kicks in (e.g. 400ms)
        self.delay_source = GLib.timeout_add(400, self.start_repeat, key_event)

    def on_button_release(self, widget, *args):
        # Cancel both delay and repeat when released
        if hasattr(self, "delay_source"):
            GLib.source_remove(self.delay_source)
            del self.delay_source
        if hasattr(self, "repeat_source"):
            GLib.source_remove(self.repeat_source)
            del self.repeat_source

    def start_repeat(self, key_event):
        # After the delay, start the repeat loop
        self.repeat_source = GLib.timeout_add(100, self.repeat_key, key_event)
        return False  # stop this one-time delay timer

    def repeat_key(self, key_event):
        self.emit_key(key_event)
        return True  # keep repeating

    def emit_key(self, key_event):
        # Apply active modifiers (excluding CapsLock & Numlock which are handled separately)
        for mod_key, active in self.modifiers.items():
            if active and mod_key not in (KEY_CAPSLOCK, KEY_NUMLOCK):
                self.device.emit(mod_key, 1)

        # Emit the key
        self.device.emit(key_event, 1)
        self.device.emit(key_event, 0)
        self.update_label_shift(False)

        # Release modifiers (so they only act as held while sending this key)
        for mod_key, active in self.modifiers.items():
            if active and mod_key not in (KEY_CAPSLOCK, KEY_NUMLOCK):
                self.device.emit(mod_key, 0)
                self.update_modifier(mod_key, False)

    def read_settings(self):
        # Ensure the config directory exists
        try:
            os.makedirs(self.CONFIG_DIR, exist_ok=True)
        except PermissionError:
            print("Warning: No permission to create the config directory.")
        try:
            if os.path.exists(self.CONFIG_FILE):
                self.config.read(self.CONFIG_FILE)
                self.bg_color = self.config.get("DEFAULT", "bg_color")
                self.opacity = self.config.get("DEFAULT", "opacity")
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
    win.change_visibility()
    Gtk.main()
