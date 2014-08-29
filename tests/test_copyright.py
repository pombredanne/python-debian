#! /usr/bin/python
## vim: fileencoding=utf-8

# Copyright (C) 2014 Google, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from __future__ import unicode_literals

import sys
import unittest

sys.path.insert(0, '../lib/')

from debian import copyright
from debian import deb822


SIMPLE = """\
Format: http://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: X Solitaire
Source: ftp://ftp.example.com/pub/games

Files: *
Copyright: Copyright 1998 John Doe <jdoe@example.com>
License: GPL-2+
 This program is free software; you can redistribute it
 and/or modify it under the terms of the GNU General Public
 License as published by the Free Software Foundation; either
 version 2 of the License, or (at your option) any later
 version.
 .
 This program is distributed in the hope that it will be
 useful, but WITHOUT ANY WARRANTY; without even the implied
 warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
 PURPOSE.  See the GNU General Public License for more
 details.
 .
 You should have received a copy of the GNU General Public
 License along with this package; if not, write to the Free
 Software Foundation, Inc., 51 Franklin St, Fifth Floor,
 Boston, MA  02110-1301 USA
 .
 On Debian systems, the full text of the GNU General Public
 License version 2 can be found in the file
 `/usr/share/common-licenses/GPL-2'.

Files: debian/*
Copyright: Copyright 1998 Jane Smith <jsmith@example.net>
License: GPL-2+
 [LICENSE TEXT]
"""

FORMAT = 'http://www.debian.org/doc/packaging-manuals/copyright-format/1.0/'


class LineBasedTest(unittest.TestCase):
    """Test for _LineBased.{to,from}_str"""

    def setUp(self):
        # Alias for less typing.
        self.lb = copyright._LineBased

    def test_from_str_none(self):
        self.assertEqual((), self.lb.from_str(None))

    def test_from_str_empty(self):
        self.assertEqual((), self.lb.from_str(''))

    def test_from_str_single_line(self):
        self.assertEqual(
            ('Foo Bar <foo@bar.com>',),
            self.lb.from_str('Foo Bar <foo@bar.com>'))

    def test_from_str_single_value_after_newline(self):
        self.assertEqual(
            ('Foo Bar <foo@bar.com>',),
            self.lb.from_str('\n Foo Bar <foo@bar.com>'))

    def test_from_str_multiline(self):
        self.assertEqual(
            ('Foo Bar <foo@bar.com>', 'http://bar.com/foo'),
            self.lb.from_str('\n Foo Bar <foo@bar.com>\n http://bar.com/foo'))

    def test_to_str_empty(self):
        self.assertIsNone(self.lb.to_str([]))
        self.assertIsNone(self.lb.to_str(()))

    def test_to_str_single(self):
        self.assertEqual(
            'Foo Bar <foo@bar.com>',
            self.lb.to_str(['Foo Bar <foo@bar.com>']))

    def test_to_str_multi_list(self):
        self.assertEqual(
            '\n Foo Bar <foo@bar.com>\n http://bar.com/foo',
            self.lb.to_str(
                ['Foo Bar <foo@bar.com>', 'http://bar.com/foo']))

    def test_to_str_multi_tuple(self):
        self.assertEqual(
            '\n Foo Bar <foo@bar.com>\n http://bar.com/foo',
            self.lb.to_str(
                ('Foo Bar <foo@bar.com>', 'http://bar.com/foo')))

    def test_to_str_empty_value(self):
        with self.assertRaises(ValueError) as cm:
            self.lb.to_str(['foo', '', 'bar'])
        self.assertEqual(('values must not be empty',), cm.exception.args)

    def test_to_str_whitespace_only_value(self):
        with self.assertRaises(ValueError) as cm:
            self.lb.to_str(['foo', ' \t', 'bar'])
        self.assertEqual(('values must not be empty',), cm.exception.args)

    def test_to_str_elements_stripped(self):
        self.assertEqual(
            '\n Foo Bar <foo@bar.com>\n http://bar.com/foo',
            self.lb.to_str(
                (' Foo Bar <foo@bar.com>\t', ' http://bar.com/foo  ')))

    def test_to_str_newlines_single(self):
        with self.assertRaises(ValueError) as cm:
            self.lb.to_str([' Foo Bar <foo@bar.com>\n http://bar.com/foo  '])
        self.assertEqual(
            ('values must not contain newlines',), cm.exception.args)

    def test_to_str_newlines_multi(self):
        with self.assertRaises(ValueError) as cm:
            self.lb.to_str(
                ['bar', ' Foo Bar <foo@bar.com>\n http://bar.com/foo  '])
        self.assertEqual(
            ('values must not contain newlines',), cm.exception.args)


class SpaceSeparatedTest(unittest.TestCase):
    """Tests for _SpaceSeparated.{to,from}_str."""

    def setUp(self):
        # Alias for less typing.
        self.ss = copyright._SpaceSeparated

    def test_from_str_none(self):
        self.assertEqual((), self.ss.from_str(None))

    def test_from_str_empty(self):
        self.assertEqual((), self.ss.from_str(' '))
        self.assertEqual((), self.ss.from_str(''))

    def test_from_str_single(self):
        self.assertEqual(('foo',), self.ss.from_str('foo'))
        self.assertEqual(('bar',), self.ss.from_str(' bar '))

    def test_from_str_multi(self):
        self.assertEqual(('foo', 'bar', 'baz'), self.ss.from_str('foo bar baz'))
        self.assertEqual(
            ('bar', 'baz', 'quux'), self.ss.from_str(' bar baz quux \t '))

    def test_to_str_empty(self):
        self.assertIsNone(self.ss.to_str([]))
        self.assertIsNone(self.ss.to_str(()))

    def test_to_str_single(self):
        self.assertEqual('foo', self.ss.to_str(['foo']))

    def test_to_str_multi(self):
        self.assertEqual('foo bar baz', self.ss.to_str(['foo', 'bar', 'baz']))

    def test_to_str_empty_value(self):
        with self.assertRaises(ValueError) as cm:
            self.ss.to_str(['foo', '', 'bar'])
        self.assertEqual(('values must not be empty',), cm.exception.args)

    def test_to_str_value_has_space_single(self):
        with self.assertRaises(ValueError) as cm:
            self.ss.to_str([' baz quux '])
        self.assertEqual(
            ('values must not contain whitespace',), cm.exception.args)

    def test_to_str_value_has_space_multi(self):
        with self.assertRaises(ValueError) as cm:
            self.ss.to_str(['foo', ' baz quux '])
        self.assertEqual(
            ('values must not contain whitespace',), cm.exception.args)


class CopyrightTest(unittest.TestCase):

    def test_basic_parse_success(self):
        c = copyright.Copyright(sequence=SIMPLE.splitlines())
        self.assertEqual(FORMAT, c.header.format)
        self.assertEqual(FORMAT, c.header['Format'])
        self.assertEqual('X Solitaire', c.header.upstream_name)
        self.assertEqual('X Solitaire', c.header['Upstream-Name'])
        self.assertEqual('ftp://ftp.example.com/pub/games', c.header.source)
        self.assertEqual('ftp://ftp.example.com/pub/games', c.header['Source'])
        self.assertIsNone(c.header.license)


class HeaderTest(unittest.TestCase):

    def test_format_not_none(self):
        h = copyright.Header()
        self.assertEqual(FORMAT, h.format)
        with self.assertRaises(TypeError) as cm:
            h.format = None
        self.assertEqual(('value must not be None',), cm.exception.args)

    def test_upstream_name_single_line(self):
        h = copyright.Header()
        h.upstream_name = 'Foo Bar'
        self.assertEqual('Foo Bar', h.upstream_name)
        with self.assertRaises(ValueError) as cm:
            h.upstream_name = 'Foo Bar\n Baz'
        self.assertEqual(('must be single line',), cm.exception.args)

    def test_upstream_contact_single_read(self):
        data = deb822.Deb822()
        data['Format'] = FORMAT
        data['Upstream-Contact'] = 'Foo Bar <foo@bar.com>'
        h = copyright.Header(data=data)
        self.assertEqual(('Foo Bar <foo@bar.com>',), h.upstream_contact)

    def test_upstream_contact_multi1_read(self):
        data = deb822.Deb822()
        data['Format'] = FORMAT
        data['Upstream-Contact'] = 'Foo Bar <foo@bar.com>\n http://bar.com/foo'
        h = copyright.Header(data=data)
        self.assertEqual(
            ('Foo Bar <foo@bar.com>', 'http://bar.com/foo'),
            h.upstream_contact)

    def test_upstream_contact_multi2_read(self):
        data = deb822.Deb822()
        data['Format'] = FORMAT
        data['Upstream-Contact'] = (
            '\n Foo Bar <foo@bar.com>\n http://bar.com/foo')
        h = copyright.Header(data=data)
        self.assertEqual(
            ('Foo Bar <foo@bar.com>', 'http://bar.com/foo'),
            h.upstream_contact)

    def test_upstream_contact_single_write(self):
        h = copyright.Header()
        h.upstream_contact = ['Foo Bar <foo@bar.com>']
        self.assertEqual(('Foo Bar <foo@bar.com>',), h.upstream_contact)
        self.assertEqual('Foo Bar <foo@bar.com>', h['Upstream-Contact'])

    def test_upstream_contact_multi_write(self):
        h = copyright.Header()
        h.upstream_contact = ['Foo Bar <foo@bar.com>', 'http://bar.com/foo']
        self.assertEqual(
            ('Foo Bar <foo@bar.com>', 'http://bar.com/foo'),
            h.upstream_contact)
        self.assertEqual(
            '\n Foo Bar <foo@bar.com>\n http://bar.com/foo',
            h['upstream-contact'])


if __name__ == '__main__':
    unittest.main()
