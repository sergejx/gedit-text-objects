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


def prepare_bounds(document):
    """
    Give two Gtk.TextIters for marking start and end of text object
    :rtype: Tuple(Gtk.TreeIter, Gtk.TreeIter)
    """
    insert = document.get_insert()
    start = document.get_iter_at_mark(insert)
    end = start.copy()
    return start, end


def delete_word(document, inner):
    start, end = prepare_bounds(document)
    if start.inside_word() or start.ends_word():
        if not start.starts_word():
            start.backward_word_start()
        if not end.ends_word():
            end.forward_word_end()
        if not inner:
            end.forward_find_char(lambda ch, d: not ch.isspace())
        document.delete(start, end)


def delete_sentence(document, inner):
    start, end = prepare_bounds(document)
    if start.inside_sentence() or start.ends_sentence():
        if not start.starts_sentence():
            start.backward_sentence_start()
        if not end.ends_sentence():
            end.forward_sentence_end()
        if not inner:
            end.forward_find_char(lambda ch, d: not ch.isspace())
        document.delete(start, end)


def delete_line(document, inner):
    start, end = prepare_bounds(document)
    if not start.starts_line():
        start.backward_line()
    if not end.ends_line():
        if inner:
            end.forward_to_line_end()
        else:
            end.forward_line()
    document.delete(start, end)
