##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################
"""
Interpreter for a pre-compiled TAL program.
"""

import sys
import string
import getopt
import cgi

from XMLParser import XMLParser
from TALDefs import TALError, quote

BOOLEAN_HTML_ATTRS = [
    # List of Boolean attributes in HTML that should be rendered in
    # minimized form (e.g. <img ismap> rather than <img ismap="">)
    # From http://www.w3.org/TR/xhtml1/#guidelines (C.10)
    # XXX The problem with this is that this is not valid XML and
    # can't be parsed back!
    "compact", "nowrap", "ismap", "declare", "noshade", "checked",
    "disabled", "readonly", "multiple", "selected", "noresize",
    "defer"
]

EMPTY_HTML_TAGS = [
    # List of HTML tags with an empty content model; these are
    # rendered in minimized form, e.g. <img />.
    # From http://www.w3.org/TR/xhtml1/#dtds
    "base", "meta", "link", "hr", "br", "param", "img", "area",
    "input", "col", "basefont", "isindex", "frame", 
]

class TALInterpreter:

    def __init__(self, program, macros, engine, stream=None,
                 debug=0, wrap=60, metal=1, tal=1, html=0):
        self.program = program
        self.macros = macros
        self.engine = engine
        self.stream = stream or sys.stdout
        self.debug = debug
        self.wrap = wrap
        self.metal = metal
        self.tal = tal
        self.html = html
        self.slots = {}
        self.currentMacro = None
        self.position = None, None  # (lineno, offset)

    def __call__(self):
        if self.html:
            self.endsep = " />"
        else:
            self.endsep = "/>"
        self.interpret(self.program)
        if self.col > 0:
            self.stream_write("\n")

    col = 0

    def stream_write(self, s):
        self.stream.write(s)
        i = string.rfind(s, '\n')
        if i < 0:
            self.col = self.col + len(s)
        else:
            self.col = len(s) - (i + 1)

    level = 0

    def interpret(self, program):
        self.level = self.level + 1
        for item in program:
            methodName = "do_" + item[0]
            args = item[1:]
            if self.debug:
                s = "%s%s%s\n" % ("    "*self.level, methodName, repr(args))
                if len(s) > 80:
                    s = s[:76] + "...\n"
                sys.stderr.write(s)
            method = getattr(self, methodName)
            apply(method, args)
        self.level = self.level - 1

    def do_setPosition(self, position):
        self.position = position

    def do_startEndTag(self, name, attrList):
        if self.html and string.lower(name) not in EMPTY_HTML_TAGS:
            self.do_startTag(name, attrList)
            self.do_endTag(name)
        else:
            self.startTagCommon(name, attrList, self.endsep)

    def do_startTag(self, name, attrList):
        self.startTagCommon(name, attrList, ">")

    def startTagCommon(self, name, attrList, end):
        if not attrList:
            self.stream_write("<%s%s" % (name, end))
            return
        self.stream_write("<" + name)
        align = self.col+1
        for item in attrList:
            name, value = item[:2]
            if len(item) > 2:
                action = item[2]
                if action == "replace" and len(item) > 3 and self.tal:
                    value = self.engine.evaluateText(item[3])
                elif (action == "macroHack" and self.currentMacro and
                      name[-13:] == ":define-macro" and self.metal):
                    name = name[:-13] + ":use-macro"
                    value = self.currentMacro
            if (self.html and not value and
                string.lower(name) in BOOLEAN_HTML_ATTRS):
                s = name
            else:
                s = "%s=%s" % (name, quote(value))
            if (self.wrap and
                self.col >= align and
                self.col + 1 + len(s) > self.wrap):
                self.stream_write("\n" + " "*align + s)
            else:
                self.stream_write(" " + s)
        self.stream_write(end)

    def do_endTag(self, name):
        self.stream_write("</%s>" % name)

    def do_beginScope(self):
        self.engine.beginScope()

    def do_endScope(self):
        self.engine.endScope()

    def do_setLocal(self, name, expr):
        if not self.tal:
            return
        value = self.engine.evaluateValue(expr)
        self.engine.setLocal(name, value)

    def do_setGlobal(self, name, expr):
        if not self.tal:
            return
        value = self.engine.evaluateValue(expr)
        self.engine.setGlobal(name, value)

    def do_insertText(self, expr, block):
        if not self.tal:
            self.interpret(block)
            return
        text = self.engine.evaluateText(expr)
        if text is None:
            return
        text = cgi.escape(text)
        self.stream_write(text)

    def do_insertStructure(self, expr, repldict, block):
        if not self.tal:
            self.interpret(block)
            return
        structure = self.engine.evaluateStructure(expr)
        if structure is None:
            return
        if repldict:
            raise TALError("replace structure with attribute replacements "
                           "not yet implemented", self.position)
        text = str(structure)
        self.checkXMLSyntax(text)
        self.stream_write(text) # No quoting -- this is intentional

    def checkXMLSyntax(self, text):
        # XXX This is a bit of a hack!
        text = '<!DOCTYPE foo PUBLIC "foo" "bar"><foo>%s</foo>' % text
        p = XMLParser()
        p.parseString(text)
        # If this succeeds without errors, we're fine

    def do_loop(self, name, expr, block):
        if not self.tal:
            self.interpret(block)
            return
        iterator = self.engine.setRepeat(name, expr)
        while iterator.next():
            self.interpret(block)

    def do_rawtext(self, text):
        self.stream_write(text)

    def do_condition(self, condition, block):
        if not self.tal or self.engine.evaluateBoolean(condition):
            self.interpret(block)

    def do_defineMacro(self, macroName, macro):
        self.interpret(macro)

    def do_useMacro(self, macroName, compiledSlots, block):
        if not self.metal:
            self.interpret(block)
            return
        macro = self.engine.evaluateMacro(macroName)
        save = self.slots, self.currentMacro
        self.slots = compiledSlots
        self.currentMacro = macroName
        self.interpret(macro)
        self.slots, self.currentMacro = save

    def do_fillSlot(self, slotName, block):
        self.interpret(block)

    def do_defineSlot(self, slotName, block):
        compiledSlot = self.metal and self.slots.get(slotName)
        if compiledSlot:
            self.interpret(compiledSlot)
        else:
            self.interpret(block)

def test():
    from driver import FILE, parsefile
    from DummyEngine import DummyEngine
    try:
        opts, args = getopt.getopt(sys.argv[1:], "")
    except getopt.error, msg:
        print msg
        sys.exit(2)
    if args:
        file = args[0]
    else:
        file = FILE
    doc = parsefile(file)
    compiler = TALCompiler(doc)
    program, macros = compiler()
    engine = DummyEngine()
    interpreter = TALInterpreter(program, macros, engine)
    interpreter()

if __name__ == "__main__":
    test()
