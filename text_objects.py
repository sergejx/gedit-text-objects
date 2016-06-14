# -*- coding: utf-8 -*-
#
#  text_objects.py (v0.1)
#    ~ Vim-line text objects for Gedit
#
#  Copyright (C) 2016 Sergej Chodarev
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330,
#  Boston, MA 02111-1307, USA.

from gi.repository import Gdk, Gedit, Gio, GObject, Gtk


class TextObjectsApp(GObject.Object, Gedit.AppActivatable):
    __gtype_name__ = 'TextObjectsApp'

    app = GObject.property(type=Gedit.App)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        # Can use: e, r, y, g, j, b, m
        self.app.add_accelerator('<Ctrl>g', 'win.text-object-delete')

    def do_deactivate(self):
        pass


class TextObjectsWin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = 'TextObjectsWin'

    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        action = Gio.SimpleAction.new('text-object-delete')
        action.connect('activate', self.activate)
        self.window.add_action(action)

    def do_deactivate(self):
        pass

    def activate(self, action, parameter):
        view = self.window.get_active_view()
        popup = CommandCompositionWidget(view)
        parent = view
        while not isinstance(parent, Gtk.Overlay):
            parent = parent.get_parent()
        parent.add_overlay(popup)
        popup.show_all()
        popup.activate()

    def delete_iword(self):
        document = self.window.get_active_view().get_buffer()
        insert = document.get_insert()
        itr = document.get_iter_at_mark(insert)
        if itr.inside_word() or itr.ends_word():
            end = itr.copy()
            print(itr.get_offset())
            if not itr.starts_word():
                itr.backward_word_start()
            if not end.ends_word():
                end.forward_word_end()
            print(itr.get_offset(), end.get_offset())
            document.delete(itr, end)


class CommandCompositionWidget(Gtk.Box):
    HELP_TEXT = "next: <b>a</b>n | <b>i</b>nner" \
                "  +  <b>w</b>ord | <b>l</b>ine | <b>p</b>aragraph"

    def __init__(self, view):
        self.view = view
        super(CommandCompositionWidget, self).__init__(name='text-object-popup')
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_valign(Gtk.Align.END)
        self.set_can_focus(True)
        # self.set_focus_on_click(True)
        self.connect('key-press-event', self.on_key_pressed)

        self.command_box = Gtk.Box(Gtk.Orientation.HORIZONTAL, 4,
                                   margin_left=8, margin_top=4)
        self.pack_start(self.command_box, False, False, 0)

        self._add_command_part("Delete (<b>Ctrl+G</b>)")

        help_label = Gtk.Label(label=self.HELP_TEXT, use_markup=True,
                               halign=Gtk.Align.START, margin_left=8)
        self.pack_start(help_label, False, False, 0)

        style = Gtk.CssProvider()
        style.load_from_data(bytes("""
        .command-part {
            background-color: #204a87;
            color: white;
            border-radius: 4px;
            padding: 2px 4px;
        }
        #text-object-popup {
            background-color: #e9b96e;
        }
        #text-object-entry {
            background-image: none;
        }
        """, 'utf-8'))
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),
                style, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.parser = TextObjectParser()

    def activate(self):
        self.grab_focus()

    def _add_command_part(self, text : str):
        if text.find("<b>") == -1:
            text = "<b>%s</b>%s" % (text[0], text[1:])
        label = Gtk.Label(label=text, use_markup=True)
        label.get_style_context().add_class('command-part')
        self.command_box.pack_start(label, False, False, 0)
        label.show()

    def on_key_pressed(self, widget, event):
        key = Gdk.keyval_name(event.keyval)
        print("key: ", key)
        result = self.parser.next_symbol(key)
        if result is not None:
            text, finished = result
            self._add_command_part(text)
            if finished:
                print(self.parser.expression)
                if self.parser.expression == "iw":
                    delete_inner_word(self.view.get_buffer())
                elif self.parser.expression == "is":
                    delete_inner_sentence(self.view.get_buffer())
        return True


class TextObjectParser:
    modifiers = {
        "a": "a",
        "i": "inner"
    }

    objects = {
        "w": "word",
        "s": "sentence",
        "l": "line",
        "p": "paragraph"
    }

    def __init__(self):
        self.state = 1
        self.expression = ""

    def next_symbol(self, symbol: str) -> (str, bool):
        if self.state == 1:
            if symbol in self.modifiers:
                self.expression += symbol
                self.state = 2
                return self.modifiers[symbol], False
            else:
                return None
        elif self.state == 2:
            if symbol in self.objects:
                self.expression += symbol
                return self.objects[symbol], True
            else:
                return None


def delete_inner_word(document):
    insert = document.get_insert()
    start = document.get_iter_at_mark(insert)
    if start.inside_word() or start.ends_word():
        end = start.copy()
        print(start.get_offset())
        if not start.starts_word():
            start.backward_word_start()
        if not end.ends_word():
            end.forward_word_end()
        print(start.get_offset(), end.get_offset())
        document.delete(start, end)


def delete_inner_sentence(document):
    insert = document.get_insert()
    start = document.get_iter_at_mark(insert)
    if start.inside_sentence() or start.ends_sentence():
        end = start.copy()
        print(start.get_offset())
        if not start.starts_sentence():
            start.backward_sentence_start()
        if not end.ends_sentence():
            end.forward_sentence_end()
        print(start.get_offset(), end.get_offset())
        document.delete(start, end)
