##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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

$Id: xmlconfig.py,v 1.4 2002/06/18 13:07:30 stevea Exp $
"""

import os
import name
from xml.sax import make_parser
from xml.sax.xmlreader import InputSource
from xml.sax.handler import ContentHandler, feature_namespaces
from meta import begin, sub, end
from keyword import iskeyword
import sys, os
from types import StringType
from Exceptions import ConfigurationError

class ZopeXMLConfigurationError(ConfigurationError):
    "Zope XML Configuration error"

    def __init__(self, locator, mess, etype=None):
        if etype is None:
            if not isinstance(mess, StringType):
                try:
                    mess = "\n%s: %s" % (mess.__class__.__name__, mess)
                except AttributeError:
                    mess = str(mess)
        else:
            mess = "\n%s: %s" % (etype.__name__, mess)
            
        self.lno = locator.getLineNumber()
        self.cno = locator.getColumnNumber()
        self.sid = locator.getSystemId()
        self.mess = mess

    def __str__(self):
        return 'File "%s", line %s, column %s\n\t%s' % (
            self.sid, self.lno, self.cno, self.mess)

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

    __top_name = 'http://namespaces.zope.org/zope', 'zopeConfigure' 

    def __init__(self, actions, context, directives=None, testing=0):
        self.__stack = []
        self.__actions = actions
        self.__directives = directives
        self.__context = context
        self.__testing = testing
        context.resolve

    def setDocumentLocator(self, locator):
        self.__locator = locator

    def startElementNS(self, name, qname, attrs):
        stack = self.__stack
        if not stack:
            if name != self.__top_name:
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
        at line %s column %s of %s
        and% at line %s column %s of %s
        """ % ((self.des,) + self.l1 + self.l2)
        
_unset = object()
class Context:
    def __init__(self, stack, module=_unset):
        self.__stackcopy = tuple(stack)
        if module is _unset:
            self.__package = None
        elif module is None:
            self.__package = 'ZopeProducts'
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
        
def xmlconfig(file, actions=None, context=None, directives=None,
              testing=0):
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
    parser.parse(src)

    if call:
        descriptors = {}
        for level, loc, des, callable, args, kw in call:
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
                r.append("  at line %s column %s of %s" % loc)
        
        return "\n".join(r)
    
class XMLConfig:

    def __init__(self, file_name):
        self._actions = []
        self._directives = {('http://namespaces.zope.org/zope', 'include'):
                            (self.include, {})}

        f = open(file_name)
        self._stack = [file_name]
        xmlconfig(f, self._actions, Context(self._stack), self._directives)
        f.close()

    def include(self, _context, file='configure.zcml', package=None):
        if package is None and _context.packageWasSet():
            package = _context.package()
        if package is not None:
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

        file_name = os.path.join(prefix, file)

        f = open(file_name)
        self._stack.append(file_name)
        xmlconfig(f, self._actions, Context(self._stack, package),
                  self._directives)
        self._stack.pop()
        f.close()
        return ()

    def __call__(self):
        self.organize()

    def __iter__(self): return iter(self._actions)

    def organize(self):
        actions = self._actions

        # organize actions by discriminators
        unique = {}
        for i in range(len(actions)):
            context, loc, des, callable, args, kw = actions[i]
            a = unique.setdefault(des, [])
            a.append((context._stackcopy(), i, loc, (callable, args, kw)))

        # Check for conflicts
        conflicts = {}
        for des, actions in unique.items():
            path, i, loc, f = actions[0]
            for opath, i, oloc, f in actions[1:]:
                if opath[:len(path)] != path:
                    if des not in conflicts:
                        conflicts[des] = [loc]
                    conflicts[des].append(oloc)

        if conflicts:
            raise ZopeConfigurationConflictError(conflicts)

        # Now order the configuration directives
        cactions = []
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
