##############################################################################
#
# Copyright (c) 2001, 2002, 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Support for the XML configuration file format

Note, for a detailed description of the way that conflicting
configuration actions are resolved, see the detailed example in
test_includeOverrides in tests/text_xmlconfig.py

$Id: xmlconfig.py,v 1.19 2004/02/24 14:07:58 srichter Exp $
"""
import errno
import os
import sys
import logging
import zope.configuration.config as config

from zope import schema
from xml.sax import make_parser
from xml.sax.xmlreader import InputSource
from xml.sax.handler import ContentHandler, feature_namespaces
from xml.sax import SAXParseException
from zope.configuration.exceptions import ConfigurationError
from zope.interface import Interface
from zope.configuration.zopeconfigure import IZopeConfigure, ZopeConfigure

logger = logging.getLogger("config")

class ZopeXMLConfigurationError(ConfigurationError):
    """Zope XML Configuration error

    These errors are wrappers for other errors. The include configuration
    info and the wrapped error type and value:

    >>> v = ZopeXMLConfigurationError("blah", AttributeError, "xxx")
    >>> print v
    'blah'
        AttributeError: xxx

    """

    def __init__(self, info, etype, evalue):
        self.info, self.etype, self.evalue = info, etype, evalue

    def __str__(self):
        # Only use the repr of the info. This is because we expect to
        # get a parse info and we only want the location information.
        return "%s\n    %s: %s" % (
            `self.info`, self.etype.__name__, self.evalue)

class ZopeSAXParseException(ConfigurationError):
    """Sax Parser errors, reformatted in an emacs friendly way

    >>> v = ZopeSAXParseException("foo.xml:12:3:Not well formed")
    >>> print v
    File "foo.xml", line 12.3, Not well formed

    """

    def __init__(self, v):
        self._v = v

    def __str__(self):
        v = self._v
        s = tuple(str(v).split(':'))
        if len(s) == 4:
            return 'File "%s", line %s.%s, %s' % s
        else:
            return str(v)

class ParserInfo:
    """Information about a directive based on parser data

    This includes the directive location, as well as text data
    contained in the directive.

    >>> info = ParserInfo('tests//sample.zcml', 1, 0)
    >>> info
    File "tests//sample.zcml", line 1.0

    >>> print info
    File "tests//sample.zcml", line 1.0

    >>> info.characters("blah\\n")
    >>> info.characters("blah")
    >>> info.text
    u'blah\\nblah'

    >>> info.end(7, 0)
    >>> info
    File "tests//sample.zcml", line 1.0-7.0

    >>> print info
    File "tests//sample.zcml", line 1.0-7.0
      <configure xmlns='http://namespaces.zope.org/zope'>
        <!-- zope.configure -->
        <directives namespace="http://namespaces.zope.org/zope">
          <directive name="hook" attributes="name implementation module"
             handler="zope.configuration.metaconfigure.hook" />
        </directives>
      </configure>


    """

    text = u''

    def __init__(self, file, line, column):
        self.file, self.line, self.column = file, line, column
        self.eline, self.ecolumn = line, column

    def end(self, line, column):
        self.eline, self.ecolumn = line, column

    def __repr__(self):
        if (self.line, self.column) == (self.eline, self.ecolumn):
            return 'File "%s", line %s.%s' % (
                self.file, self.line, self.column)

        return 'File "%s", line %s.%s-%s.%s' % (
            self.file, self.line, self.column, self.eline, self.ecolumn)

    def __str__(self):
        if (self.line, self.column) == (self.eline, self.ecolumn):
            return 'File "%s", line %s.%s' % (
                self.file, self.line, self.column)

        file = self.file
        if file == 'tests//sample.zcml':
            # special case for testing
            file = os.path.join(os.path.split(__file__)[0],
                                'tests', 'sample.zcml')

        try:
            f = open(file)
        except IOError:
            src = "  Could not read source."
        else:
            lines = f.readlines()[self.line-1:self.eline]
            ecolumn = self.ecolumn
            if lines[-1][ecolumn:ecolumn+2] == '</':
                # We're pointing to the start of an end tag. Try to find
                # the end
                l = lines[-1].find('>', ecolumn)
                if l >= 0:
                    lines[-1] = lines[-1][:l+1]
            else:
                lines[-1] = lines[-1][:ecolumn+1]

            column = self.column
            if lines[0][:column].strip():
                # Remove text before start if it's noy whitespace
                lines[0] = lines[0][self.column:]
                
            src = ''.join([u"  "+l for l in lines])

        return "%s\n%s" % (`self`, src)

    def characters(self, characters):
        self.text += characters


class ConfigurationHandler(ContentHandler):
    """Interface to the xml parser

    Translate parser events into calls into the configuration system.
    """

    def __init__(self, context, testing=0):
        self.context = context
        self.testing = testing

    def setDocumentLocator(self, locator):
        self.locator = locator

    def characters(self, text):
        self.context.getInfo().characters(text)

    def startElementNS(self, name, qname, attrs):

        data = {}
        for (ns, aname), value in attrs.items():
            if ns is None:
                aname = str(aname)
                data[aname] = value

        info = ParserInfo(
            self.locator.getSystemId(),
            self.locator.getLineNumber(),
            self.locator.getColumnNumber(),
            )

        try:
            self.context.begin(name, data, info)
        except:
            if self.testing:
                raise
            raise ZopeXMLConfigurationError, (
                info, sys.exc_info()[0], sys.exc_info()[1]
                ), sys.exc_info()[2]

        self.context.setInfo(info)


    def endElementNS(self, name, qname):
        info = self.context.getInfo()
        info.end(
            self.locator.getLineNumber(),
            self.locator.getColumnNumber(),
            )

        try:
            self.context.end()
        except:
            if self.testing:
                raise
            raise ZopeXMLConfigurationError, (
                info, sys.exc_info()[0], sys.exc_info()[1]
                ), sys.exc_info()[2]


def processxmlfile(file, context, testing=False):
    """Process a configuration file

    See examples in tests/text_xmlconfig.py
    """
    src = InputSource(getattr(file, 'name', '<string>'))
    src.setByteStream(file)
    parser = make_parser()
    parser.setContentHandler(ConfigurationHandler(context, testing=testing))
    parser.setFeature(feature_namespaces, True)
    try:
        parser.parse(src)
    except SAXParseException:
        raise ZopeSAXParseException, sys.exc_info()[1], sys.exc_info()[2]


def openInOrPlain(filename):
    """Open a file, falling back to filename.in.

    If the requested file does not exist and filename.in does, fall
    back to filename.in.  If opening the original filename fails for
    any other reason, allow the failure to propogate.

    For example, the tests/samplepackage dirextory has files:

       configure.zcml
       configure.zcml.in
       foo.zcml.in

    If we open configure.zcml, we'll get that file:

    >>> here = os.path.split(__file__)[0]
    >>> path = os.path.join(here, 'tests', 'samplepackage', 'configure.zcml')
    >>> f = openInOrPlain(path)
    >>> f.name[-14:]
    'configure.zcml'

    But if we open foo.zcml, we'll get foo.zcml.in, since there isn't a
    foo.zcml:

    >>> path = os.path.join(here, 'tests', 'samplepackage', 'foo.zcml')
    >>> f = openInOrPlain(path)
    >>> f.name[-11:]
    'foo.zcml.in'

    """
    try:
        fp = open(filename)
    except IOError, (code, msg):
        if code == errno.ENOENT:
            fn = filename + ".in"
            if os.path.exists(fn):
                fp = open(fn)
            else:
                raise
    return fp

class IInclude(Interface):

    file = schema.BytesLine(
        __doc__=
        """Configuration file name

        The name of a configuration file to be included,
        relative to the directive containing the
        including configuration file.

        """,
        default="configure.zcml",
        )

    package = config.fields.GlobalObject(
        __doc__=
        """Include packahe

        Include the named file (or configure.zcml)
        from the directory of this package.
        """,
        required=False,
        )


def include(_context, file, package=None):
    """Include a zcml file

    See examples in tests/text_xmlconfig.py
    """

    logger.debug("include %s" % file)

    # This is a tad tricky. We want to behave a a grouping directive.
    context = config.GroupingContextDecorator(_context)
    if package is not None:
        context.package = package
        context.basepath = None
    path = context.path(file)
    f = openInOrPlain(path)

    logger.debug("include %s" % f.name)

    context.basepath = os.path.split(path)[0]
    context.includepath = _context.includepath + (f.name, )
    _context.stack.append(config.GroupingStackItem(context))

    processxmlfile(f, context)
    f.close()
    assert _context.stack[-1].context is context
    _context.stack.pop()

def includeOverrides(_context, file, package=None):
    """Include zcml file containing overrides

    The actions in the included file are added to the context as if they
    were in the including file directly.

    See the detailed example in test_includeOverrides in
    tests/text_xmlconfig.py
    """

    # We need to remember how many actions we had before
    nactions = len(_context.actions)

    # We'll give the new actions this include path
    includepath = _context.includepath

    # Now we'll include the file. We'll munge the actions after
    include(_context, file, package)

    # Now we'll grab the new actions, resolve conflicts,
    # and munge the includepath:
    newactions = []
    for action in config.resolveConflicts(_context.actions[nactions:]):
        (discriminator, callable, args, kw, oldincludepath, info
         ) = config.expand_action(*action)
        newactions.append(
            (discriminator, callable, args, kw, includepath, info)
            )

    # and replace the new actions with the munched new actions:
    _context.actions[nactions:] = newactions

def registerCommonDirectives(context):
    # We have to use the direct definition functions to define
    # a directive for all namespaces.

    config.defineSimpleDirective(
        context, "include", IInclude, include, namespace="*")

    config.defineSimpleDirective(
        context, "includeOverrides", IInclude, includeOverrides, namespace="*")

    # XXX zopeConfigure is deprecated; use configure in new ZCML instead
    config.defineGroupingDirective(
        context,
        name="zopeConfigure",
        namespace="*",
        schema=IZopeConfigure,
        handler=ZopeConfigure,
        )

    config.defineGroupingDirective(
        context,
        name="configure",
        namespace="*",
        schema=IZopeConfigure,
        handler=ZopeConfigure,
        )

def file(name, package=None, context=None, execute=True):
    """Execute a zcml file
    """

    if context is None:
        context = config.ConfigurationMachine()
        registerCommonDirectives(context)
        context.package = package

    include(context, name, package)
    if execute:
        context.execute_actions()

    return context

def string(s, context=None, name="<string>", execute=True):
    """Execute a zcml string
    """
    from StringIO import StringIO

    if context is None:
        context = config.ConfigurationMachine()
        registerCommonDirectives(context)

    f = StringIO(s)
    f.name = name
    processxmlfile(f, context)

    if execute:
        context.execute_actions()

    return context


##############################################################################
# Backward compatability, mainly for tests


_context = None
def _clearContext():
    global _context
    _context = config.ConfigurationMachine()
    registerCommonDirectives(_context)

def _getContext():
    global _context
    if _context is None:
        _clearContext()
        from zope.testing.cleanup import addCleanUp
        addCleanUp(_clearContext)
    return _context

class XMLConfig:
    """Provide high-level handling of configuration files.

    See examples in tests/text_xmlconfig.py
    """

    def __init__(self, file_name, module=None):
        context = _getContext()
        include(context, file_name, module)
        self.context = context

    def __call__(self):
        self.context.execute_actions()

def xmlconfig(file, testing=False):
    context = _getContext()
    processxmlfile(file, context, testing=testing)
    context.execute_actions(testing=testing)


def testxmlconfig(file, context=None):
    """xmlconfig that doesn't raise configuration errors

    This is useful for testing, as it doesn't mask exception types.
    """
    context = _getContext()
    processxmlfile(file, context, testing=True)
    context.execute_actions(testing=True)

