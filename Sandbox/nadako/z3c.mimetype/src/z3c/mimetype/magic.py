##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
'''
$Id$
'''
from z3c.mimetype.mimetype import lookup

class MagicRule(object):

    def __init__(self, f):
        self.next = None
        self.prev = None

        indent = ''
        while True:
            c = f.read(1)
            if c == '>':
                break
            indent += c
        if not indent:
            self.nest = 0
        else:
            self.nest = int(indent)

        start = ''
        while True:
            c = f.read(1)
            if c == '=':
                break
            start += c
        self.start = int(start)
        
        hb = f.read(1)
        lb = f.read(1)
        self.lenvalue = ord(lb) + (ord(hb) << 8)

        self.value = f.read(self.lenvalue)

        c = f.read(1)
        if c == '&':
            self.mask = f.read(self.lenvalue)
            c = f.read(1)
        else:
            self.mask = None

        if c == '~':
            w = ''
            while c != '+' and c!='\n':
                c = f.read(1)
                if c == '+' or c == '\n':
                    break
                w += c
            self.word = int(w)
        else:
            self.word = 1

        if c == '+':
            r = ''
            while c != '\n':
                c = f.read(1)
                if c == '\n':
                    break
                r += c
            self.range = int(r)
        else:
            self.range = 1

        if c != '\n':
            raise Exception('Malformed MIME magic line')

    def getLength(self):
        return self.start + self.lenvalue + self.range

    def appendRule(self, rule):
        if self.nest < rule.nest:
            self.next = rule
            rule.prev = self
        elif self.prev:
            self.prev.appendRule(rule)

    def match(self, buffer):
        if self.match0(buffer):
            if self.next:
                return self.next.match(buffer)
            return True

    def match0(self, buffer):
        l = len(buffer)
        for o in xrange(self.range):
            s = self.start + o
            e = s + self.lenvalue
            if l < e:
                return False
            if self.mask:
                test = ''
                for i in xrange(self.lenvalue):
                    c = ord(buffer[s + i]) & ord(self.mask[i])
                    test += chr(c)
            else:
                test = buffer[s:e]

            if test == self.value:
                return True

class MagicType(object):

    def __init__(self, mtype):
        self.mtype = mtype
        self.top_rules = []
        self.last_rule = None

    def getLine(self, f):
        nrule = MagicRule(f)
        if nrule.nest and self.last_rule:
            self.last_rule.appendRule(nrule)
        else:
            self.top_rules.append(nrule)
        self.last_rule = nrule
        return nrule

    def match(self, buffer):
        for rule in self.top_rules:
            if rule.match(buffer):
                return self.mtype

class MagicDB(object):

    def __init__(self):
        self.types = {}
        self.maxlen = 0

    def mergeFile(self, fname):
        f = open(fname, 'r')

        line = f.readline()
        if line != 'MIME-Magic\0\n':
            raise Exception('Not a MIME magic file')

        while True:
            shead = f.readline()
            if not shead:
                break
            if shead[0] != '[' or shead[-2:] != ']\n':
                raise Exception('Malformed section heading')
            pri, tname = shead[1:-2].split(':')
            pri = int(pri)
            mtype = lookup(tname)

            ents = self.types.setdefault(pri, [])
            magictype = MagicType(mtype)

            c = f.read(1)
            f.seek(-1, 1)
            while c and c!='[':
                rule = magictype.getLine(f)
                if rule:
                    rulelen = rule.getLength()
                    if rulelen > self.maxlen:
                        self.maxlen = rulelen
                c = f.read(1)
                f.seek(-1, 1)

            ents.append(magictype)

            if not c:
                break

    def match(self, file, min_priority=0, max_priority=100):
        file.seek(0, 0)
        buf = file.read(self.maxlen)
        for priority, types in sorted(self.types.items(), key=lambda ob:ob[0], reverse=True):
            if priority > max_priority:
                continue
            if priority < min_priority:
                break
            for type in types:
                m = type.match(buf)
                if m:
                    return m
        return None
