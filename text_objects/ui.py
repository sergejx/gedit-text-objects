# -*- coding: utf-8 -*-
#
#  Gedit Text Objects
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

from gi.repository import Gtk, Gdk

from text_objects.objects import TextObjectParser


def cmd(name):
    return "<span weight='bold' color='black'>%s</span>%s" % (name[0], name[1:])


class CommandCompositionWidget(Gtk.Box):
    HELP_TEXT = "1. modifier:\t" + cmd("a") + " | " + cmd("inner") + "\n" \
                "2. object:  \t" + " | ".join(map(cmd, TextObjectParser.object_names()))

    def __init__(self, view, revealer, operation):
        self.view = view
        self.revealer = revealer
        self.operation = operation
        self.key_handler = None
        super(CommandCompositionWidget, self).__init__(name='text-object-popup')
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_valign(Gtk.Align.END)

        self.command_box = Gtk.Box(Gtk.Orientation.HORIZONTAL, 4,
                                   margin_left=8, margin_top=4)
        self.pack_start(self.command_box, False, False, 0)

        self._add_command_part(operation.capitalize())

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
            color: #2e3436;
        }
        #text-object-entry {
            background-image: none;
        }
        """, 'utf-8'))
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),
                style, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.parser = TextObjectParser()

    def activate(self):
        self.show_all()
        self.revealer.set_transition_duration(500)
        self.revealer.set_reveal_child(True)
        # Intercept keyboard input from the TextView
        self.key_handler = self.view.connect('key-press-event',
                                             self.on_key_pressed)

    def deactivate(self, slow=False):
        # Return keyboard input
        self.view.disconnect(self.key_handler)
        if slow:
            self.revealer.set_transition_duration(4000)
        self.revealer.set_reveal_child(False)

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
        if key == "Escape":
            self.deactivate()
            return True
        result = self.parser.next_symbol(key)
        if result is not None:
            text, object = result
            self._add_command_part(text)
            if object is not None:
                self.do_operation(object)
                self.deactivate(slow=True)
        return True

    def do_operation(self, text_object):
        if self.operation == 'delete':
            text_object.delete(self.view.get_buffer())
        elif self.operation == 'select':
            text_object.select(self.view.get_buffer())
