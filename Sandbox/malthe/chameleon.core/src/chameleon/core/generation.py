from zope.i18n import interpolate
from zope.i18n import translate
from zope.i18nmessageid import Message

import utils
import etree

template_wrapper = """\
def render(%(init)s, %(args)s%(extra)s%(language)s=None):
\t%(out)s, %(write)s = %(init)s.initialize_stream()
\t%(attributes)s, %(repeat)s = %(init)s.initialize_tal()
\t%(scope)s = {}
\t%(domain)s = None

%(body)s
\treturn %(out)s.getvalue()
"""

macro_wrapper = """\
def render(%(init)s, %(kwargs)s%(extra)s):
\t%(attributes)s, %(repeat)s = %(init)s.initialize_tal()
\t%(domain)s = None
%(body)s
"""

class marker(object):
    pass

def fast_translate(msgid, domain=None, mapping=None, context=None,
                   target_language=None, default=None):
    """This translation function does not attempt to negotiate a
    language if ``None`` is passed."""
    
    if target_language is not None:
        return translate(
            msgid, domain=domain, mapping=mapping, context=context,
            target_language=target_language, default=default)
    
    if isinstance(msgid, Message):
        default = msgid.default
        mapping = msgid.mapping

    if default is None:
        default = unicode(msgid)

    if not isinstance(default, (str, unicode)):
        return default
    
    return interpolate(default, mapping)

def initialize_tal():
    return ({}, utils.repeatdict())

def initialize_stream():
    out = BufferIO()
    return (out, out.write)

class BufferIO(list):
    write = list.append

    def getvalue(self):
        return ''.join(self)
        
class CodeIO(BufferIO):
    """Stream buffer suitable for writing Python-code. This class is
    used internally by the compiler to manage variable scopes, source
    annotations and temporary variables."""

    t_prefix = '_tmp'
    v_prefix = '_tmpv'

    annotation = None
    
    def __init__(self, symbols=None, encoding=None,
                 indentation=0, indentation_string="\t"):
        BufferIO.__init__(self)
        self.symbols = symbols or object
        self.symbol_mapping = {}
        self.encoding = encoding
        self.indentation = indentation
        self.indentation_string = indentation_string
        self.queue = ''
        self.scope = [set()]
        self.selectors = {}
        self.annotations = {}
        self._variables = {}
        self.t_counter = 0
        self.v_counter = 0
        self.l_counter = 0

    def new_var(self):
        self.v_counter += 1
        return "%s%d" % (self.v_prefix, self.v_counter)
        
    def save(self):
        self.t_counter += 1
        return "%s%d" % (self.t_prefix, self.t_counter)

    def restore(self):
        var = "%s%d" % (self.t_prefix, self.t_counter)
        self.t_counter -= 1
        return var

    def indent(self, amount=1):
        if amount > 0:
            self.cook()
            self.indentation += amount

    def outdent(self, amount=1):
        if amount > 0:
            self.cook()
            self.indentation -= amount

    def annotate(self, item):
        self.annotation = self.annotations[self.l_counter] = item

    def out(self, string):
        if isinstance(string, unicode) and self.encoding:
            string = string.encode(self.encoding)
        self.queue += string
            
    def cook(self):
        if self.queue:
            queue = self.queue
            self.queue = ''
            self.write(
                "%s(%s)" %
                (self.symbols.write, repr(queue)))

    def write(self, string):
        if isinstance(string, unicode) and self.encoding:
            string = string.encode(self.encoding)

        self.l_counter += len(string.split('\n'))-1
        self.cook()
        
        indent = self.indentation_string * self.indentation

        # if a source code annotation is set, write it as a comment
        # prior to the source code line
        if self.annotation:
            if isinstance(self.annotation, unicode) and self.encoding:
                self.annotation = self.annotation.encode(self.encoding)            
            BufferIO.write(
                self, "%s# %s\n" % (indent, self.annotation))
            self.annotation = None
            
        BufferIO.write(self, indent + string + '\n')

    def getvalue(self):
        self.cook()
        return BufferIO.getvalue(self)

    def escape(self, variable):
        self.write("if '&' in %s:" % variable)
        self.indent()
        self.write("%s = %s.replace('&', '&amp;')" % (variable, variable))
        self.outdent()
        self.write("if '<' in %s:" % variable)
        self.indent()
        self.write("%s = %s.replace('<', '&lt;')" % (variable, variable))
        self.outdent()
        self.write("if '>' in %s:" % variable)
        self.indent()
        self.write("%s = %s.replace('>', '&gt;')" % (variable, variable))
        self.outdent()
        self.write("if '\"' in %s:" % variable)
        self.indent()
        self.write("%s = %s.replace('\"', '&quot;')" % (variable, variable))
        self.outdent()

    def convert_to_string(self, variable):
        self.write("if isinstance(%s, unicode):" % variable)
        self.indent()
        self.write("%s = %s.encode('%s')" % (variable, variable, self.encoding))
        self.outdent()

    def coerce_to_string(self, variable):
        self.write("if isinstance(%s, unicode):" % variable)
        self.indent()
        self.write("%s = %s.encode('%s')" % (variable, variable, self.encoding))
        self.outdent()
        self.write("elif not isinstance(%s, str):" % variable)
        self.indent()
        self.write("%s = str(%s)" % (variable, variable))
        self.outdent()

    def coerce_to_unicode(self, variable):
        """Coerces variable to unicode (actually ``str``, because it's
        much faster)."""
        
        self.write("if not isinstance(%s, (str, unicode)):" % variable)
        self.indent()
        self.write("%s = str(%s)" % (variable, variable))
        self.outdent()
        
    def begin(self, clauses):
        if isinstance(clauses, (list, tuple)):
            for clause in clauses:
                self.begin(clause)
        else:
            clauses.begin(self)
                
    def end(self, clauses):
        if isinstance(clauses, (list, tuple)):
            for clause in reversed(clauses):
                self.end(clause)
        else:
            clauses.end(self)
