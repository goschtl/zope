##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Extra-lite parser for a `ZConfig`_-like configuration syntax.

There is no support for external schemas; schemas are simpler and must
be specified using Python data structures.

There is no support for any %-directives, but dollar signs in values
must be doubled to ensure compatibility with `ZConfig`_.

.. _ZConfig:  http://www.zope.org/Members/fdrake/zconfig/

"""

import re


class ConfigurationError(Exception):
    """Exception raised for errors in a configuration file.

    :ivar url: URL of the resource being read when the error was
      detected.

    :ivar lineno: Line number within the resource at which the
      error was detected.

    """

    def __init__(self, message, url=None, lineno=None):
        """Initialize the ConfigurationError instance.

        :param message: Text of the error message.

        :param url: URL of the resource being read when the error was
          detected.

        :param lineno: Line number within the resource at which the
          error was detected.

        """
        Exception.__init__(self, message)
        self.url = url
        self.lineno = lineno

    def __str__(self):
        s = Exception.__str__(self)
        if self.url:
            s = "%s\n(%s" % (s, self.url)
            if self.lineno is not None:
                s = "%s, line %s" % (s, self.lineno)
            s += ")"
        return s


class Schema:
    """Schema definition that can be used by the Parser class to
    construct a configuration.

    The definition is defined as a set of *type definitions*.  Each
    type definition is a triple containing a dictionary, a list, and a
    function (or `None`).  The dictionary maps the names of the keys
    allowed in the section to conversion functions for the values (or
    None if no conversion is required).  The list names the section
    types which can occur in the section.  The function is used to
    convert a `SectionValue` representing the collected values to the
    actual value of the section itself; if `None` is used, no
    conversion is performed.

    """

    def __init__(self, toplevel, typedefs=None):
        """Initialize a schema definition based on type definitions.

        :param toplevel: Type definition that represents the otherwise
          anonymous top-level section of a configuration.

        :param typedefs: Mapping from typenames (which must be given
          as lower-case strings) to type definitions.  Only section
          types specified in `typedefs` can be used anywhere in
          configurations described by the schema.

        """
        self._toplevel = toplevel
        if typedefs is None:
            typedefs = {}
        self._typedefs = typedefs

    def getConfiguration(self):
        """Return a configuration object for the top-level section.

        :return: New configuration object.

        The attributes of the configuration object represent values
        that have not been specified in a configuration file; these
        will be filled in during parsing.
        """
        return self.createSection(None, None, self._toplevel)

    def startSection(self, parent, typename, name):
        # make sure typename is defined:
        typedef = self._typedefs.get(typename)
        if typedef is None:
            raise ConfigurationError("unknown section type: %s" % typename)
        # make sure typename is allowed:
        x, sects, x = parent.getSectionDefinition()
        if typename not in sects:
            parent_type = parent.getSectionType()
            if parent_type:
                msg = ("%r sections not allowed in %r sections"
                       % (typename, parent_type))
            else:
                msg = "%r sections not allowed" % typename
            raise ConfigurationError(msg)
        return self.createSection(name, typename, typedef)

    def createSection(self, name, typename, typedef):
        child = SectionValue(name, typename, typedef)
        keys, sects, x = typedef
        # initialize the defaults:
        for name in keys:
            name = name.lower().replace("-", "_")
            setattr(child, name, [])
        for name in sects:
            name = name.lower().replace("-", "_")
            setattr(child, name, [])
        return child

    def finishSection(self, section):
        x, x, datatype = section.getSectionDefinition()
        if datatype is not None:
            typename = section.getSectionType()
            try:
                section = datatype(section)
            except ValueError, e:
                raise ConfigurationError(
                    "could not convert %r section value: %s"
                    % (typename, e))
        return section

    def endSection(self, parent, typename, name, child):
        value = self.finishSection(child)
        getattr(parent, typename).append(value)

    def addValue(self, section, key, value):
        keys, x, x = section.getSectionDefinition()
        keyname = key.lower()
        if keyname not in keys:
            typename = section.getSectionType()
            if typename:
                msg = "key %r not defined in %r sections" % (key, typename)
            else:
                msg = "key %r not defined" % key
            raise ConfigurationError(msg)
        datatype = keys[keyname]
        if datatype is not None:
            try:
                value = datatype(value)
            except ValueError, e:
                raise ConfigurationError("could not convert value: %s" % e)
        attrname = keyname.replace("-", "_")
        getattr(section, attrname).append(value)


# These regular expressions should match the corresponding definitions
# in ZConfig.cfgparser since this needs to be a format that could be
# read by ZConfig with an appropriate schema definition.
#
_name_re = r"[^\s()]+"
_keyvalue_rx = re.compile(r"(?P<key>%s)\s*(?P<value>[^\s].*)?$"
                          % _name_re)
_section_start_rx = re.compile(r"(?P<type>%s)"
                               r"(?:\s+(?P<name>%s))?"
                               r"$"
                               % (_name_re, _name_re))

_nulljoin = "".join


class Parser:
    """Parser for ZConfig-like configuration files."""

    def __init__(self, file, url, schema):
        self.schema = schema
        self.file = file
        self.url = url
        self.lineno = 0
        self.stack = []   # [(type, name, prevmatcher), ...]

    def nextline(self):
        line = self.file.readline()
        if line:
            self.lineno += 1
            return False, line.strip()
        else:
            return True, None

    def load(self):
        section = self.schema.getConfiguration()
        self.parse(section)
        try:
            return self.schema.finishSection(section)
        except ConfigurationError, e:
            e.lineno = self.lineno
            e.url = self.url
            raise

    def parse(self, section):
        done, line = self.nextline()
        while not done:
            if line[:1] in ("", "#"):
                # blank line or comment
                pass

            elif line[:2] == "</":
                # section end
                if line[-1] != ">":
                    self.error("malformed section end")
                section = self.end_section(section, line[2:-1])

            elif line[0] == "<":
                # section start
                if line[-1] != ">":
                    self.error("malformed section start")
                section = self.start_section(section, line[1:-1])

            elif line[0] == "%":
                self.error("ZConfig-style directives are not supported")

            else:
                self.handle_key_value(section, line)

            done, line = self.nextline()

        if self.stack:
            self.error("unclosed sections not allowed")

    def start_section(self, section, rest):
        isempty = rest[-1:] == "/"
        if isempty:
            text = rest[:-1].rstrip()
        else:
            text = rest.rstrip()
        # parse section start stuff here
        m = _section_start_rx.match(text)
        if not m:
            self.error("malformed section header")
        type, name = m.group('type', 'name')
        type = type.lower()
        #
        # XXX Argh!  Converting section names to lower-case was a
        # mistake in ZConfig, but we have to honor case here for
        # <extension> sections.  We need to add some way to control
        # the "nametype" of sections in ZConfig anyway.
        #
        # if name:
        #    name = name.lower()
        #
        try:
            newsect = self.schema.startSection(section, type, name)
        except ConfigurationError, e:
            e.lineno = self.lineno
            e.url = self.url
            raise
        if isempty:
            try:
                self.schema.endSection(section, type, name, newsect)
            except ConfigurationError, e:
                e.lineno = self.lineno
                e.url = self.url
                raise
            return section
        else:
            self.stack.append((type, name, section))
            return newsect

    def end_section(self, section, rest):
        if not self.stack:
            self.error("unexpected section end")
        type = rest.rstrip().lower()
        opentype, name, prevsection = self.stack.pop()
        if type != opentype:
            self.error("unbalanced section end")
        try:
            self.schema.endSection(prevsection, type, name, section)
        except ConfigurationError, e:
            e.lineno = self.lineno
            e.url = self.url
            raise
        return prevsection

    def handle_key_value(self, section, rest):
        m = _keyvalue_rx.match(rest)
        if not m:
            self.error("malformed configuration data")
        key, value = m.group('key', 'value')
        if value:
            value = self.replace(value)
        else:
            value = ''
        try:
            self.schema.addValue(section, key, value)
        except ConfigurationError, e:
            e.lineno = self.lineno
            e.url = self.url
            raise

    def replace(self, text):
        parts = []
        rest = text
        while "$" in rest:
            i = rest.index("$")
            if i:
                parts.append(rest[:i])
            rest = rest[i+1:]
            if not rest:
                self.error("text cannot end with a bare '$'")
            if rest[0] == "$":
                parts.append("$")
                rest = rest[1:]
            else:
                self.error("unsupported substitution syntax")
        parts.append(rest)
        return _nulljoin(parts)

    def error(self, message):
        raise ConfigurationError(message, self.url, self.lineno)


class SectionValue:
    """Generic bag-of-values object for a section."""

    def __init__(self, name, typename, typedef):
        self._name = name
        self._typename = typename
        self._typedef = typedef

    def getSectionName(self):
        """Return the name of the section, or `None`."""
        return self._name

    def getSectionType(self):
        """Return the name of the section type."""
        return self._typename

    def getSectionDefinition(self):
        """Return the data structure that represents the type of this
        section value.
        """
        return self._typedef
