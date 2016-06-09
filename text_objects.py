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

from gi.repository import Gedit, Gio, GLib, GObject, Gtk


class TextObjectsApp(GObject.Object, Gedit.AppActivatable):
    __gtype_name__ = 'TextObjectsApp'

    app = GObject.property(type=Gedit.App)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self.app.add_accelerator('<Ctrl>g', 'win.text-object-delete')
        self.menu_ext = self.extend_menu("tools-section-1")
        item = Gio.MenuItem.new(('Delete object'), "win.text-object-delete")
        self.menu_ext.append_menu_item(item)

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
