# vim: fileencoding=utf-8
#
# Copyright (C) 2014       Google, Inc.
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

"""Utilities for parsing and creating machine-readable debian/copyright files.

The specification for the format (also known as DEP5) is available here:
https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/

TODO(jsw): Add example usage.
"""

from __future__ import unicode_literals

import collections
import re
import string
import warnings

from debian import deb822


_CURRENT_FORMAT = (
    'http://www.debian.org/doc/packaging-manuals/copyright-format/1.0/')

_KNOWN_FORMATS = frozenset([
    _CURRENT_FORMAT,
    # TODO(jsw): Transparently rewrite https:// as http://, at least for this?
    'https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/',
])


class Error(Exception):
    """Base class for exceptions in this module."""


class NotMachineReadableError(Error):
    """Raised when the input is not a machine-readable debian/copyright file."""


class Copyright(object):
    """Represents a debian/copyright file."""

    def __init__(self, sequence=None, encoding='utf-8'):
        """Initializer.

        :param sequence: Sequence of lines, e.g. a list of strings or a
            file-like object.  If not specified, a blank Copyright object is
            initialized.
        :param encoding: Encoding to use, in case input is raw byte strings.
            It is recommended to use unicode objects everywhere instead, e.g.
            by opening files in text mode.

        Raises:
            NotMachineReadableError if 'sequence' does not contain a
                machine-readable debian/copyright file.
        """
        super(Copyright, self).__init__()

        if sequence is not None:
            paragraphs = list(deb822.Deb822.iter_paragraphs(
                sequence=sequence, encoding=encoding))
            if len(paragraphs) > 0:
                self.__header = Header(paragraphs[0])
            # TODO(jsw): Parse the rest of the paragraphs.
        else:
            self.__header = Header()

    @property
    def header(self):
        """The file header paragraph."""
        return self.__header

    @header.setter
    def header(self, hdr):
        if not isinstance(hdr, Header):
            raise TypeError('value must be a Header object')
        self.__header = hdr


def _single_line(s):
    """Returns s if it is a single line; otherwise raises ValueError."""
    if '\n' in s:
        raise ValueError('must be single line')
    return s


class _LineBased(object):
    """Namespace for conversion methods for line-based lists as tuples."""
    # TODO(jsw): Expose this somewhere else?  It may have more general utility.

    @staticmethod
    def from_str(s):
        """Returns the lines in 's', with whitespace stripped, as a tuple."""
        return tuple(v for v in
                     (line.strip() for line in (s or '').strip().splitlines())
                     if v)

    @staticmethod
    def to_str(seq):
        """Returns the sequence as a string with each element on its own line.

        If 'seq' has one element, the result will be on a single line.
        Otherwise, the first line will be blank.
        """
        l = list(seq)
        if not l:
            return None

        def process_and_validate(s):
            s = s.strip()
            if not s:
                raise ValueError('values must not be empty')
            if '\n' in s:
                raise ValueError('values must not contain newlines')
            return s

        if len(l) == 1:
            return process_and_validate(l[0])

        tmp = ['']
        for s in l:
            tmp.append(' ' + process_and_validate(s))
        return '\n'.join(tmp)


class _SpaceSeparated(object):
    """Namespace for conversion methods for space-separated lists as tuples."""
    # TODO(jsw): Expose this somewhere else?  It may have more general utility.

    _has_space = re.compile(r'\s')

    @staticmethod
    def from_str(s):
        """Returns the values in s as a tuple (empty if only whitespace)."""
        return tuple(v for v in (s or '').split() if v)

    @classmethod
    def to_str(cls, seq):
        """Returns the sequence as a space-separated string (None if empty)."""
        l = list(seq)
        if not l:
            return None
        tmp = []
        for s in l:
            if cls._has_space.search(s):
                raise ValueError('values must not contain whitespace')
            s = s.strip()
            if not s:
                raise ValueError('values must not be empty')
            tmp.append(s)
        return ' '.join(tmp)


class Header(deb822.RestrictedWrapper):
    """Represents the header paragraph of a debian/copyright file.

    Property values are all immutable, such that in order to modify them you
    must explicitly set them (rather than modifying a returned reference).
    """

    def __init__(self, data=None):
        """Initializer.

        :param parsed: A deb822.Deb822 object for underlying data.  If None, a
            new one will be created.
        """
        if data is None:
            data = deb822.Deb822()
            data['Format'] = _CURRENT_FORMAT
        super(Header, self).__init__(data)

        fmt = self.format
        if fmt is None:
            raise NotMachineReadableError(
                'input is not a machine-readable debian/copyright')
        if fmt not in _KNOWN_FORMATS:
            warnings.warn('format not known: %r' % fmt)

    def known_format(self):
        """Returns True iff the format is known."""
        return self.format in _KNOWN_FORMATS

    def current_format(self):
        """Returns True iff the format is the current format."""
        return self.format == _CURRENT_FORMAT

    format = deb822.RestrictedField(
        'Format', to_str=_single_line, allow_none=False)

    upstream_name = deb822.RestrictedField(
        'Upstream-Name', to_str=_single_line)

    upstream_contact = deb822.RestrictedField(
        'Upstream-Contact', from_str=_LineBased.from_str,
        to_str=_LineBased.to_str)

    source = deb822.RestrictedField('Source')

    disclaimer = deb822.RestrictedField('Disclaimer')

    comment = deb822.RestrictedField('Comment')

    # TODO(jsw): Parse this.
    license = deb822.RestrictedField(
        'License', to_str=lambda _: None, from_str=lambda _: None)

    copyright = deb822.RestrictedField('Copyright')
