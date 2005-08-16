##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Python implementations of document template some features

$Id$
"""
import sys
from types import StringTypes, TupleType, ClassType
ClassTypes = [ClassType]


def safe_callable(ob):
    # Works with ExtensionClasses and Acquisition.
    if hasattr(ob, '__class__'):
        if hasattr(ob, '__call__'):
            return 1
        else:
            return type(ob) in ClassTypes
    else:
        return callable(ob)


class InstanceDict:

    def __init__(self, o, namespace):
        self.self = o
        self.cache = {}
        self.namespace = namespace

    def has_key(self,key):
        return hasattr(self.self,key)

    def keys(self):
        return self.self.__dict__.keys()

    def __repr__(self):
        return 'InstanceDict(%s)' % str(self.self)

    def __getitem__(self,key):

        cache=self.cache
        if cache.has_key(key):
            return cache[key]

        inst = self.self

        if key[:1] == '_':
            if key != '__str__':
                raise KeyError, key # Don't divuldge private data
            else:
                return str(inst)

        try:
            r = getattr(inst, key)
        except AttributeError:
            raise KeyError, key

        self.cache[key] = r
        return r

    def __len__(self):
        return 1


class MultiMapping:

    def __init__(self):
        self.dicts = []

    def __getitem__(self, key):
        for d in self.dicts:
            try:
                return d[key]
            except (KeyError, AttributeError):
                pass
        raise KeyError, key

    def push(self,d):
        self.dicts.insert(0, d)

    def pop(self, n=1):
        r = self.dicts[-1]
        del self.dicts[:n]
        return r

    def keys(self):
        kz = []
        for d in self.dicts:
            kz = kz + d.keys()
        return kz


class DictInstance:

    def __init__(self, mapping):
        self.__d = mapping

    def __getattr__(self, name):
        try:
            return self.__d[name]
        except KeyError:
            raise AttributeError, name


class TemplateDict:

    level = 0

    def _pop(self, n=1):
        return self.dicts.pop(n)

    def _push(self, d):
        return self.dicts.push(d)

    def __init__(self):
        m = self.dicts = MultiMapping()
        self._pop = m.pop
        self._push = m.push
        try:
            self.keys = m.keys
        except:
            pass

    def __getitem__(self,key,call=1):

        v = self.dicts[key]
        if call:
            if hasattr(v, '__render_with_namespace__'):
                return v.__render_with_namespace__(self)
            vbase = getattr(v, 'aq_base', v)
            if safe_callable(vbase):
                v = v()
        return v

    def __len__(self):
        total = 0
        for d in self.dicts.dicts:
            total += len(d)
        return total

    def has_key(self,key):
        try:
            self.dicts[key]
        except KeyError:
            return 0
        return 1

    getitem = __getitem__

    def __call__(self, *args, **kw):
        if args:
            if len(args) == 1 and not kw:
                m=args[0]
            else:
                m = self.__class__()
                for a in args:
                    m._push(a)
                if kw:
                    m._push(kw)
        else:
            m=kw
        return (DictInstance(m),)


def render_blocks(blocks, md):
    rendered = []
    for section in blocks:
        if type(section) is TupleType:
            l = len(section)
            if l == 1:
                # Simple var
                section = section[0]
                if isinstance(section, StringTypes):
                    section = md[section]
                else:
                    section = section(md)
                section = str(section)
            else:
                # if
                cache = {}
                md._push(cache)
                try:
                    i = 0
                    m = l-1
                    while i < m:
                        cond = section[i]
                        if isinstance(cond, StringTypes):
                            n = cond
                            try:
                                cond = md[cond]
                                cache[n] = cond
                            except KeyError, v:
                                v = v[0]
                                if n != v:
                                    raise KeyError, v, sys.exc_traceback
                                cond=None
                        else:
                            cond = cond(md)
                        if cond:
                            section = section[i+1]
                            if section:
                                section = render_blocks(section,md)
                            else: section=''
                            m = 0
                            break
                        i += 2
                    if m:
                        if i == m:
                            section = render_blocks(section[i],md)
                        else:
                            section = ''

                finally: md._pop()

        elif not isinstance(section, StringTypes):
            section = section(md)

        if section:
            rendered.append(section)

    l = len(rendered)
    if l == 0:
        return ''
    elif l == 1:
        return rendered[0]
    return ''.join(rendered)
    return rendered
