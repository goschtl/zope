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
"""
$Id: xmlconfig.py,v 1.9 2003/06/23 14:44:13 fdrake Exp $
"""

import errno
import os
import sys
import logging
from keyword import iskeyword
from types import StringType
from os.path import abspath

from xml.sax import make_parser
from xml.sax.xmlreader import InputSource
from xml.sax.handler import ContentHandler, feature_namespaces
from xml.sax import SAXParseException
from zope.configuration import name
from zope.configuration.meta import begin, sub, end
from zope.configuration.exceptions import ConfigurationError

# marker used in Context class and XMLConfig class to indicate
# that a particular zcml file was given no "package" attribute
# when included, and the same went for all of its parents.
_NO_MODULE_GIVEN = object()


logger = logging.getLogger("config")

class ZopeXMLConfigurationError(ConfigurationError):
    """Zope XML Configuration error"""

    def __init__(self, locator, mess, etype=None):
        if etype is None:
            if not isinstance(mess, StringType):
                try:
                    mess = "\n%s:\n  %s" % (mess.__class__.__name__, mess)
                except AttributeError:
                    mess = str(mess)
        else:
            mess = "\n%s: %s" % (etype.__name__, mess)

        self.lno = locator.getLineNumber()
        self.cno = locator.getColumnNumber()
        self.sid = locator.getSystemId()
        self.mess = mess

    def __str__(self):
        return 'File "%s", line %s.%s\n\t%s' % (
            self.sid, self.lno, self.cno, self.mess)


class ZopeSAXParseException(ConfigurationError):
    def __init__(self, v):
        self._v = v

    def __str__(self):
        v = self._v
        s = tuple(str(v).split(':'))
        if len(s) == 4:
            return 'File "%s", line %s.%s, %s' % s
        else:
            return str(v)

class ConfigurationExecutionError(ZopeXMLConfigurationError):
    """An error occurred during execution of a configuration action
    """

    def __init__(self, locator, mess, etype=None):
        if etype is None:
            if isinstance(mess, StringType):
                try:
                    mess = "%s: %s" % (mess.__class__.__name__, mess)
                except AttributeError:
                    mess = str(mess)
        else:
            mess = "\n%s: %s" % (etype.__name__, mess)

        self.lno, self.cno, self.sid = locator
        self.mess = mess


class ConfigurationHandler(ContentHandler):

    __top_name = 'zopeConfigure'

    def __init__(self, actions, context, directives=None, testing=0):
        self.__stack = []
        self.__actions = actions
        self.__directives = directives
        self.__context = context
        self.__testing = testing

    def setDocumentLocator(self, locator):
        self.__locator = locator

    def characters(self, text):
        stack = self.__stack
        if len(stack) > 1:
            base = stack[-1][0]
            if hasattr(base, 'zcmlText'):
                base.zcmlText(text)

    def startElementNS(self, name, qname, attrs):
        stack = self.__stack
        if not stack:
            if name[1] != self.__top_name:
                raise ZopeXMLConfigurationError(
                    self.__locator, "Invalid top element: %s %s" % name)

            for (ns, aname), value in attrs.items():
                if ns is None:
                    self.__context.file_attr(aname, value)

            stack.append(None)
            return

        kw = {}
        for (ns, aname), value in attrs.items():
            if ns is None:
                aname = str(aname)
                if iskeyword(aname): aname += '_'
                kw[aname] = value

        if len(stack) == 1:
            try:
                stack.append(
                    begin(self.__directives, name, self.__context, **kw)
                    )
            except Exception, v:
                if self.__testing:
                    raise
                raise ZopeXMLConfigurationError, (
                    self.__locator, v), sys.exc_info()[2]

        else:
            subs = self.__stack[-1]
            if subs is None:
                raise ZopeXMLConfigurationError(self.__locator,
                                                'Invalid sub-directive')
            try:
                stack.append(sub(subs, name, self.__context, **kw))
            except Exception, v:
                if self.__testing:
                    raise
                raise ZopeXMLConfigurationError, (
                    self.__locator, v), sys.exc_info()[2]

    def endElementNS(self, name, qname):
        subs = self.__stack.pop()
        # to fool compiler that thinks actions is used before assignment:
        actions = ()

        if subs is not None:
            try:
                actions = end(subs)
            except Exception, v:
                if self.__testing:
                    raise
                raise ZopeXMLConfigurationError, (
                    self.__locator, str(v)), sys.exc_info()[2]

        append = self.__actions.append

        try:
            for des, callable, args, kw in actions:
                append((self.__context,
                        (self.__locator.getLineNumber(),
                         self.__locator.getColumnNumber(),
                         self.__locator.getSystemId(),
                         ), des, callable, args, kw))
        except:
            print 'endElementNS', actions
            raise


class ZopeConflictingConfigurationError(ZopeXMLConfigurationError):
    "Zope XML Configuration error"

    def __init__(self, l1, l2, des):
        self.l1 = l1
        self.l2 = l2
        self.des = des

    def __str__(self):
        return """Conflicting configuration action:
        %s
        File "%s", line %s column %s
        File "%s", line %s column %s
        """ % (self.des,
               self.l1[2], self.l1[0], self.l1[1],
               self.l2[2], self.l2[0], self.l2[1],
               )


class Context:
    def __init__(self, stack, module):
        self.__stackcopy = tuple(stack)
        if module is _NO_MODULE_GIVEN:
            self.__package = None
        elif module is None:
            self.__package = 'zopeproducts'
        else:
            self.__package = module.__name__

    def _stackcopy(self):
        return self.__stackcopy

    def resolve(self, dottedname):
        return name.resolve(dottedname, self.__package)

    def getNormalizedName(self, dottedname):
        return name.getNormalizedName(dottedname, self.__package)

    def path(self, file=None):
        return name.path(file, self.__package)

    def file_attr(self, name, value):
        if name == 'package':
            self.__package = value
        else:
            raise TypeError, "Unrecognized config file attribute: %s" % name

    def packageWasSet(self):
        return self.__package is not None

    def package(self):
        return self.__package


def xmlconfig(file, actions=None, context=None, directives=None, testing=0):
    if context is None:
        context = name

    if actions is None:
        call = actions = []
    else:
        call = 0

    src = InputSource(getattr(file, 'name', '<string>'))
    src.setByteStream(file)
    parser = make_parser()
    parser.setContentHandler(
        ConfigurationHandler(actions, context,directives,
                             testing=testing)
        )
    parser.setFeature(feature_namespaces, 1)
    try:
        parser.parse(src)
    except SAXParseException:
        raise ZopeSAXParseException, sys.exc_info()[1], sys.exc_info()[2]

    if call:
        descriptors = {}
        for level, loc, des, callable, args, kw in call:
            if des is not None:
                if des in descriptors:
                    raise ZopeConflictingConfigurationError(
                        descriptors[des], loc, des)
                descriptors[des] = loc

            callable(*args, **kw)


def testxmlconfig(file, actions=None, context=None, directives=None):
    """xmlconfig that doesn't raise configuration errors

    This is useful for testing, as it doesn't mask exception types.
    """
    return xmlconfig(file, actions, context, directives, testing=1)


class ZopeConfigurationConflictError(ZopeXMLConfigurationError):

    def __init__(self, conflicts):
        self._conflicts = conflicts

    def __str__(self):
        r = ["Conflicting configuration actions"]
        for dis, locs in self._conflicts.items():
            r.append('for: %s' % (dis,))
            for loc in locs:
                r.append('  File "%s", line %s column %s' %
                         (loc[2], loc[0], loc[1]))

        return "\n".join(r)


def inopen(filename):
    # XXX I don't really like the name of this function
    """Open a file, falling back to filename.in.

    If the requested file does not exist and filename.in does, fall
    back to filename.in.  If opening the original filename fails for
    any other reason, allow the failure to propogate.
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


class XMLConfig:

    def __init__(self, file_name, module=_NO_MODULE_GIVEN):
        if module is not None and module is not _NO_MODULE_GIVEN:
            module_dir = abspath(os.path.split(module.__file__)[0])
            file_name = os.path.join(module_dir, file_name)

        self._actions = []
        self._directives = {('*', 'include'):
                            (self.include, {})}

        f = inopen(file_name)
        self._stack = [file_name]
        xmlconfig(f, self._actions,
                  Context(self._stack, module=module),
                  self._directives)
        f.close()

    def include(self, _context, file='configure.zcml', package=None):
        if package is None and _context.packageWasSet():
            package = _context.package()
        subpackages = False
        if package is not None:
            if package.endswith('.*'):
                # <include package="package.*" /> includes all subpackages
                subpackages = True
                parent = package = package[:-2]
                if package == "":
                    package = "."
            try:
                package = _context.resolve(package)
                if len(package.__path__) != 1:
                    print ("Module Path: '%s' has wrong number of elements"
                            % str(package.__path__))
                # XXX: This should work for 99% of cases
                # We may want to revisit this with a more robust
                # mechanism later. Specifically, sometimes __path__
                # will have more than one element. Also, we could
                # use package.__file__, and lop the tail off that.
                prefix = package.__path__[0]
            except (ImportError, AttributeError, ValueError), v:
                raise # XXX the raise below hides the real error
                raise ValueError("Invalid package attribute: %s\n(%s)"
                                 % (package, `v`))
        else:
            prefix = os.path.dirname(self._stack[-1])

        if subpackages:
            for subdir in os.listdir(prefix):
                file_name = os.path.join(prefix, subdir, file)
                if not os.access(file_name, os.F_OK):
                    continue
                subpackage = "%s.%s" % (parent, subdir)
                subpackage = _context.resolve(subpackage)
                self._include(file_name, subpackage)
        else:
            file_name = os.path.join(prefix, file)
            self._include(file_name, package)
        return ()

    def _include(self, file_name, package):
        logger.debug("include %s" % file_name)
        f = inopen(file_name)
        self._stack.append(file_name)
        xmlconfig(f, self._actions, Context(self._stack, package),
                  self._directives)
        self._stack.pop()
        f.close()

    def __call__(self):
        self.organize()

    def __iter__(self):
        return iter(self._actions)

    def organize(self):
        actions = self._actions

        # organize actions by discriminators
        unique = {}
        cactions = []
        for i in range(len(actions)):
            context, loc, des, callable, args, kw = actions[i]
            if des is None:
                # The descriminator is None, so this directive can
                # never conflict. We can add it directly to the
                # configuration actions.
                cactions.append((i, loc, (callable, args, kw)))
                continue

            a = unique.setdefault(des, [])
            a.append((context._stackcopy(), i, loc, (callable, args, kw)))

        # Check for conflicts
        conflicts = {}
        for des, actions in unique.items():

            # We need to sort the actions by the paths so that the shortest
            # path with a given prefix comes first:
            actions.sort()

            path, i, loc, f = actions[0]
            for opath, i, oloc, f in actions[1:]:
                # Test whether path is a prefix of opath
                if opath[:len(path)] != path or (opath == path):
                    if des not in conflicts:
                        conflicts[des] = [loc]
                    conflicts[des].append(oloc)

        if conflicts:
            raise ZopeConfigurationConflictError(conflicts)

        # Now order the configuration directives
        for des, actions in unique.items():
            path, i, loc, f = actions.pop(0)
            cactions.append((i, loc, f))

        unique = None

        cactions.sort()

        # Call actions
        for i, loc, f in cactions:
            try:
                callable, args, kw = f
                callable(*args, **kw)
            except Exception, v:
                raise ConfigurationExecutionError, (
                    loc, v, sys.exc_info()[0]), sys.exc_info()[2]
