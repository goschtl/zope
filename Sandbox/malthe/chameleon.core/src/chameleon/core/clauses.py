from chameleon.core import types
from chameleon.core import config
from chameleon.core import etree
from chameleon.core import utils

class Assign(object):
    """
    >>> from chameleon.core import testing

    We'll define some values for use in the tests.

    >>> _out, _write, stream = testing.setup_stream()
    >>> one = types.value("1")
    >>> bad_float = types.value("float('abc')")
    >>> abc = types.value("'abc'")
    >>> ghi = types.value("'ghi'")
    >>> exclamation = types.value("'!'")
        
    Simple value assignment:
    
    >>> assign = Assign(one)
    >>> assign.begin(stream, 'a')
    >>> exec stream.getvalue()
    >>> a == 1
    True
    >>> assign.end(stream)
    
    Try-except parts (bad, good):
    
    >>> assign = Assign(types.parts((bad_float, one)))
    >>> assign.begin(stream, 'b')
    >>> exec stream.getvalue()
    >>> b == 1
    True
    >>> assign.end(stream)
    
    Try-except parts (good, bad):
    
    >>> assign = Assign(types.parts((one, bad_float)))
    >>> assign.begin(stream, 'b')
    >>> exec stream.getvalue()
    >>> b == 1
    True
    >>> assign.end(stream)
    
    Join:

    >>> assign = Assign(types.join((abc, ghi)))
    >>> assign.begin(stream, 'b')
    >>> exec stream.getvalue()
    >>> b == 'abcghi'
    True
    >>> assign.end(stream)

    Join with try-except parts:
    
    >>> assign = Assign(types.join((types.parts((bad_float, abc, ghi)), ghi)))
    >>> assign.begin(stream, 'b')
    >>> exec stream.getvalue()
    >>> b == 'abcghi'
    True
    >>> assign.end(stream)
    """

    def __init__(self, parts, variable=None):
        if not isinstance(parts, types.parts):
            parts = types.parts((parts,))

        self.parts = parts

        if isinstance(variable, tuple):
            variable = ", ".join(variable)
            
        self.variable = variable
        
    def begin(self, stream, variable=None):
        """First n - 1 expressions must be try-except wrapped."""

        variable = variable or self.variable

        for value in self.parts[:-1]:
            stream.write("try:")
            stream.indent()

            self._assign(variable, value, stream)
            
            stream.outdent()
            stream.write("except Exception, e:")
            stream.indent()

        value = self.parts[-1]
        self._assign(variable, value, stream)
        
        stream.outdent(len(self.parts)-1)

    def _assign(self, variable, value, stream):
        stream.annotate(value)
        symbols = stream.symbols.as_dict()

        if value.symbol_mapping:
            stream.symbol_mapping.update(value.symbol_mapping)

        if isinstance(value, types.template):
            value = types.value(value % symbols)
        if isinstance(value, types.value):
            stream.write("%s = %s" % (variable, value))
        elif isinstance(value, types.join):
            parts = []
            _v_count = 0

            for part in value:
                if isinstance(part, types.expression):
                    stream.symbol_mapping.update(part.symbol_mapping)
                if isinstance(part, types.template):
                    part = types.value(part % symbols)
                if isinstance(part, (types.parts, types.join)):
                    _v = stream.save()
                    assign = Assign(part, _v)
                    assign.begin(stream)
                    assign.end(stream)
                    _v_count +=1
                    parts.append(_v)
                elif isinstance(part, types.value):
                    parts.append(part)
                elif isinstance(part, unicode):
                    if stream.encoding:
                        parts.append(repr(part.encode(stream.encoding)))
                    else:
                        parts.append(repr(part))
                elif isinstance(part, str):
                    parts.append(repr(part))
                else:
                    raise ValueError("Not able to handle %s" % type(part))
                    
            format = "%s"*len(parts)

            stream.write("%s = '%s' %% (%s)" % (variable, format, ",".join(parts)))
            
            for i in range(_v_count):
                stream.restore()
        else:
            raise TypeError("Can't assign value of type %s" % type(value))
        
    def end(self, stream):
        pass

class Define(object):
    """
    >>> from chameleon.core import testing

    Variable scope:

    >>> _out, _write, stream = testing.setup_stream()
    >>> define = Define("a", testing.pyexp("b"))
    >>> b = object()
    >>> define.begin(stream)
    >>> exec stream.getvalue()
    >>> a is b
    True
    >>> del a
    >>> define.end(stream)
    >>> exec stream.getvalue()
    >>> a
    Traceback (most recent call last):
        ...
    NameError: name 'a' is not defined
    >>> b is not None
    True

    Multiple defines:

    >>> _out, _write, stream = testing.setup_stream()
    >>> define1 = Define("a", testing.pyexp("b"))
    >>> define2 = Define("c", testing.pyexp("d"))
    >>> d = object()
    >>> define1.begin(stream)
    >>> define2.begin(stream)
    >>> exec stream.getvalue()
    >>> a is b and c is d
    True
    >>> define2.end(stream)
    >>> define1.end(stream)
    >>> del a; del c
    >>> exec stream.getvalue()
    >>> a
    Traceback (most recent call last):
        ...
    NameError: name 'a' is not defined
    >>> c
    Traceback (most recent call last):
        ...
    NameError: name 'c' is not defined
    >>> b is not None and d is not None
    True

    Redefining a variable which is in scope:
    
    >>> _out, _write, stream = testing.setup_stream()
    >>> define1 = Define("a", testing.pyexp("b"))
    >>> define2 = Define("a", testing.pyexp("c"))
    >>> b = object()
    >>> c = object()
    >>> define1.begin(stream)
    >>> define2.begin(stream)
    >>> exec stream.getvalue()
    >>> a is c
    True
    >>> define2.end(stream)
    >>> define1.end(stream)
    >>> del a
    >>> exec stream.getvalue()
    >>> a
    Traceback (most recent call last):
        ...
    NameError: name 'a' is not defined
    
    Tuple assignments:

    >>> _out, _write, stream = testing.setup_stream()
    >>> define = Define(types.declaration(('e', 'f')), testing.pyexp("[1, 2]"))
    >>> define.begin(stream)
    >>> exec stream.getvalue()
    >>> e == 1 and f == 2
    True
    >>> define.end(stream)

    Verify scope is preserved on tuple assignment:

    >>> _out, _write, stream = testing.setup_stream()
    >>> e = None; f = None
    >>> stream.scope[-1].add('e'); stream.scope[-1].add('f')
    >>> stream.scope.append(set())
    >>> define.begin(stream)
    >>> define.end(stream)
    >>> exec stream.getvalue()
    >>> e is None and f is None
    True

    Using semicolons in expressions within a define:

    >>> _out, _write, stream = testing.setup_stream()
    >>> define = Define("a", testing.pyexp("';'"))
    >>> define.begin(stream)
    >>> exec stream.getvalue()
    >>> a
    ';'
    >>> define.end(stream)

    Scope:

    >>> _out, _write, stream = testing.setup_stream()
    >>> a = 1
    >>> stream.scope[-1].add('a')
    >>> stream.scope.append(set())
    >>> define = Define("a", testing.pyexp("2"))
    >>> define.begin(stream)
    >>> define.end(stream)
    >>> exec stream.getvalue()
    >>> a
    1
    """

    assign = None
    
    def __init__(self, declaration, expression=None, dictionary=None):
        if not isinstance(declaration, types.declaration):
            declaration = types.declaration((declaration,))

        if len(declaration) == 1:
            variable = declaration[0]
        else:
            variable = u"(%s,)" % ", ".join(declaration)

        if dictionary is not None:
           variable = "%s['%s'] = %s" % (dictionary, variable, variable)

        if expression is not None:
            self.assign = Assign(expression, variable)
            
        self.declaration = declaration
        self.dictionary = dictionary
        
    def begin(self, stream):
        if self.declaration.global_scope:
            # if the declaration belongs to a global scope, remove this
            # symbol from previous scopes
            for scope in stream.scope:
                for variable in self.declaration:
                    if variable in scope:
                        scope.remove(variable)
        else:
            # save local variables already in in scope
            for var in self.declaration:
                temp = stream.save()

                # If we didn't set the variable in this scope already
                if var not in stream.scope[-1]:

                    # we'll check if it's set in one of the older scopes
                    for scope in stream.scope[:-1]:
                        if var in scope:
                            # in which case we back it up
                            stream.write('%s = %s' % (temp, var))

                    stream.scope[-1].add(var)

        if self.assign is not None:
            self.assign.begin(stream)

    def end(self, stream):
        if self.assign is not None:
            self.assign.end(stream)

        if not self.declaration.global_scope:
            # restore the variables that were previously in scope
            for var in reversed(self.declaration):
                temp = stream.restore()

                # if we set the variable in this scope already
                if var in stream.scope[-1]:
                    # we'll check if it's set in one of the older scopes
                    for scope in stream.scope[:-1]:
                        if var in scope:
                            # in which case we restore it
                            stream.write('%s = %s' % (var, temp))
                            break
                    else:
                        stream.write("del %s" % var)
                    stream.scope[-1].remove(var)
                            
class Condition(object):
    """
    >>> from chameleon.core import testing, etree

    Unlimited scope:

    >>> _out, _write, stream = testing.setup_stream()
    >>> _validate = etree.validate
    >>> true = Condition(testing.pyexp("True"))
    >>> false = Condition(testing.pyexp("False"))
    >>> true.begin(stream)
    >>> stream.write("print 'Hello'")
    >>> true.end(stream)
    >>> false.begin(stream)
    >>> stream.write("print 'Universe!'")
    >>> false.end(stream)
    >>> stream.write("print 'World!'")
    >>> exec stream.getvalue()
    Hello
    World!

    Finalized limited scope:

    >>> _out, _write, stream = testing.setup_stream()
    >>> true = Condition(testing.pyexp("True"), [Write(testing.pyexp("'Hello'"))])
    >>> false = Condition(testing.pyexp("False"), [Write(testing.pyexp("'Hallo'"))])
    >>> true.begin(stream)
    >>> true.end(stream)
    >>> false.begin(stream)
    >>> false.end(stream)
    >>> exec stream.getvalue()
    >>> _out.getvalue()
    'Hello'

    Open limited scope:

    >>> _out, _write, stream = testing.setup_stream()
    >>> true = Condition(testing.pyexp("True"), [Tag('div')], finalize=False)
    >>> false = Condition(testing.pyexp("False"), [Tag('span')], finalize=False)
    >>> true.begin(stream)
    >>> stream.out("Hello World!")
    >>> true.end(stream)
    >>> false.begin(stream)
    >>> false.end(stream)
    >>> exec stream.getvalue()
    >>> _out.getvalue()
    '<div>Hello World!</div>'

    """
      
    def __init__(self, value, clauses=None, finalize=True, invert=False):
        self.assign = Assign(value)
        self.clauses = clauses
        self.finalize = finalize
        self.invert = invert
        
    def begin(self, stream):
        temp = stream.save()
        self.assign.begin(stream, temp)

        if self.invert:
            stream.write("if not (%s):" % temp)
        else:
            stream.write("if %s:" % temp)
            
        stream.indent()
        if self.clauses:
            for clause in self.clauses:
                clause.begin(stream)
            if self.finalize:
                for clause in reversed(self.clauses):
                    clause.end(stream)
                stream.restore()
            stream.outdent()
        elif self.finalize:
            stream.restore()
            
    def end(self, stream):
        if self.clauses:
            if not self.finalize:
                temp = stream.restore()
                stream.write("if %s:" % temp)
                stream.indent()
                for clause in reversed(self.clauses):
                    clause.end(stream)
                    stream.outdent()
        else:
            if not self.finalize:
                stream.restore()
            stream.outdent()
        self.assign.end(stream)

class Else(object):
    def __init__(self, clauses=None):
        self.clauses = clauses
        
    def begin(self, stream):
        stream.write("else:")
        stream.indent()
        if self.clauses:
            for clause in self.clauses:
                clause.begin(stream)
            for clause in reversed(self.clauses):
                clause.end(stream)
            stream.outdent()
        
    def end(self, stream):
        if not self.clauses:
            stream.outdent()

class Group(object):
    def __init__(self, clauses):
        self.clauses = clauses
        
    def begin(self, stream):
        for clause in self.clauses:
            clause.begin(stream)
        for clause in reversed(self.clauses):
            clause.end(stream)

    def end(self, stream):
        pass

class Visit(object):
    def __init__(self, node):
        self.node = node
        
    def begin(self, stream):
        self.node.visit()

    def end(self, stream):
        pass

class Tag(object):
    """
    >>> from chameleon.core import testing

    Dynamic attribute:

    >>> _out, _write, stream = testing.setup_stream()
    >>> tag = Tag('div', dict(alt=testing.pyexp(repr('Hello World!'))))
    >>> tag.begin(stream)
    >>> stream.out('Hello Universe!')
    >>> tag.end(stream)
    >>> exec stream.getvalue()
    >>> _out.getvalue()
    '<div alt="Hello World!">Hello Universe!</div>'

    >>> _out, _write, stream = testing.setup_stream('utf-8')
    >>> tag = Tag('div', dict(alt=testing.pyexp(repr('Hello World!'))))
    >>> tag.begin(stream)
    >>> stream.out('Hello Universe!')
    >>> tag.end(stream)
    >>> exec stream.getvalue()
    >>> _out.getvalue()
    '<div alt="Hello World!">Hello Universe!</div>'

    Verify that unicode data is handled correctly.

    >>> _out, _write, stream = testing.setup_stream()
    >>> tag = Tag('div', dict(
    ...     alt=testing.pyexp(repr(unicode('La Pe\xc3\xb1a', 'utf-8')))))
    >>> tag.begin(stream)
    >>> stream.out('Hello Universe!')
    >>> tag.end(stream)
    >>> exec stream.getvalue()
    >>> 'Hello' in _out.getvalue()
    True

    Dictionary attributes:

    >>> _out, _write, stream = testing.setup_stream()
    >>> tag = Tag('div', expression=testing.pyexp(repr({'alt': 'Hello World!'})))
    >>> tag.begin(stream)
    >>> stream.out('Hello Universe!')
    >>> tag.end(stream)
    >>> exec stream.getvalue()
    >>> _out.getvalue()
    '<div alt="Hello World!">Hello Universe!</div>'
    
    >>> _out, _write, stream = testing.setup_stream('utf-8')
    >>> tag = Tag('div', expression=testing.pyexp(repr({'alt': 'Hello World!'})))
    >>> tag.begin(stream)
    >>> stream.out('Hello Universe!')
    >>> tag.end(stream)
    >>> exec stream.getvalue()
    >>> _out.getvalue()
    '<div alt="Hello World!">Hello Universe!</div>'

    Self-closing tag:

    >>> _out, _write, stream = testing.setup_stream()
    >>> tag = Tag('br', {}, True)
    >>> tag.begin(stream)
    >>> tag.end(stream)
    >>> exec stream.getvalue()
    >>> _out.getvalue()
    '<br />'
    """

    def __init__(self, tag, attributes=None,
                 selfclosing=False, expression=None, cdata=False):
        self.tag = tag.split('}')[-1]
        self.selfclosing = selfclosing
        self.attributes = attributes or {}
        self.expression = expression and Assign(expression)
        self.cdata = cdata
        
    def begin(self, stream):
        if self.cdata:
            stream.out('<![CDATA['); return

        stream.out('<%s' % self.tag)

        static = filter(
            lambda (attribute, value): \
            not isinstance(value, types.expression),
            self.attributes.items())

        # sort static attribute alphabetically by name
        static.sort(key=lambda (name, value): name)

        dynamic = filter(
            lambda (attribute, value): \
            isinstance(value, types.expression),
            self.attributes.items())

        temp = stream.save()
        temp2 = stream.save()
        
        if self.expression:
            self.expression.begin(stream, stream.symbols.tmp)
            # loop over all attributes
            stream.write("for %s, %s in %s.items():" % \
                         (temp, temp2, stream.symbols.tmp))            
            stream.indent()

            # only include attribute if expression is not None
            stream.write("if %s is not None:" % temp2)                
            stream.indent()

            # if an encoding is specified, we need to check
            # whether we're dealing with unicode strings or not,
            # before writing out the attribute
            if stream.encoding is not None:
                stream.convert_to_string(temp)
                stream.coerce_to_string(temp2)
            else:
                stream.coerce_to_unicode(temp2)
                
            # escape expression
            stream.escape(temp2)

            # write out
            stream.write("%s(' %%s=\"%%s\"' %% (%s, %s))" % \
                         (stream.symbols.write, temp, temp2))

            stream.outdent()
            stream.outdent()
            
        for attribute, value in dynamic:
            assign = Assign(value)
            assign.begin(stream, temp)

            # only include attribute if expression is not ``None`` or ``False``
            stream.write("if %s is not None and %s is not False:" % (temp, temp))
            stream.indent()

            # if an encoding is specified, we need to check
            # whether we're dealing with unicode strings or not,
            # before writing out the attribute
            if stream.encoding is not None:
                stream.coerce_to_string(temp)
            else:
                stream.coerce_to_unicode(temp)
                
            # escape expression
            stream.escape(temp)

            # print attribute
            stream.write("%s(' %s=\"'+%s+'\"')" % (
                stream.symbols.write, attribute, temp))

            stream.outdent()
            assign.end(stream)

        stream.restore()
        stream.restore()

        for attribute, expression in static:
            if isinstance(expression, unicode) and stream.encoding:
                expression = expression.encode(stream.encoding)

            # escape expression
            expression = utils.escape(expression, '"', stream.encoding)

            # if there are dynamic expressions, we only want to write
            # out static attributes if they're not in the dynamic
            # expression dictionary
            if self.expression:
                stream.write("if '%s' not in %s:" % (attribute, stream.symbols.tmp))
                stream.indent()
                
            stream.out(' %s="%s"' % (attribute, expression))

            if self.expression:
                stream.outdent()
                
        if self.selfclosing:
            stream.out(" />")
        else:
            stream.out(">")

    def end(self, stream):
        if self.cdata:
            stream.out(']]>'); return
            
        if not self.selfclosing:
            stream.out('</%s>' % self.tag)

class Repeat(object):
    """
    >>> from chameleon.core import testing

    We need to set up the repeat object.

    >>> from chameleon.core import utils
    >>> repeat = utils.repeatdict()

    Simple repeat loop and repeat data structure:

    >>> _out, _write, stream = testing.setup_stream()
    >>> _repeat = Repeat("i", testing.pyexp("range(5)"))
    >>> _repeat.begin(stream)
    >>> stream.write("r = repeat['i']")
    >>> stream.write(
    ...     "print (i, r.index, r.start, r.end, r.number(), r.odd(), r.even())")
    >>> _repeat.end(stream)
    >>> exec stream.getvalue()
    (0, 0, True, False, 1, False, True)
    (1, 1, False, False, 2, True, False)
    (2, 2, False, False, 3, False, True)
    (3, 3, False, False, 4, True, False)
    (4, 4, False, True, 5, False, True)
    >>> _repeat.end(stream)

    A repeat over an empty set.

    >>> _out, _write, stream = testing.setup_stream()
    >>> _repeat = Repeat("j", testing.pyexp("range(0)"))
    >>> _repeat.begin(stream)
    >>> _repeat.end(stream)
    >>> exec stream.getvalue()

    A repeat over a non-iterable raises an exception.

    >>> _out, _write, stream = testing.setup_stream()
    >>> _repeat = Repeat("j", testing.pyexp("None"))
    >>> _repeat.begin(stream)
    >>> _repeat.end(stream)
    >>> exec stream.getvalue()
    Traceback (most recent call last):
     ...
    TypeError: Can only repeat over an iterable object (None).

    Simple for loop:
  
    >>> _out, _write, stream = testing.setup_stream()
    >>> _for = Repeat("i", testing.pyexp("range(3)"), repeatdict=False)
    >>> _for.begin(stream)
    >>> stream.write("print i")
    >>> _for.end(stream)
    >>> exec stream.getvalue()
    0
    1
    2
    >>> _for.end(stream)

    """

    def __init__(self, v, e, scope=(), repeatdict=True):
        self.variable = v
        #self.expression = e
        self.define = Define(v)
        self.assign = Assign(e)
        self.repeatdict = repeatdict
        self.e = e
        
    def begin(self, stream):
        variable = self.variable

        # initialize variable scope
        self.define.begin(stream)

        # assign iterator
        iterator = stream.save()
        self.assign.begin(stream, iterator)

        if self.repeatdict:
            stream.write("%s = repeat.insert('%s', %s)" % (
                iterator, variable, iterator))
            stream.write("try:")
            stream.indent()
            stream.write("%s = None" % variable)
            stream.write("%s = %s.next()" % (variable, iterator))
            stream.write("while True:")
            stream.indent()
        else:
            stream.write("for %s in %s:" % (variable, iterator))
            stream.indent()

    def end(self, stream):
        # cook before leaving loop
        stream.cook()
        iterator = stream.restore()
        
        if self.repeatdict:
            stream.write("%s = %s.next()" % (self.variable, iterator))
            
        stream.out('\n')
        stream.outdent()
        
        if self.repeatdict:
            stream.outdent()
            stream.write("except StopIteration:")
            stream.indent()
            stream.write("pass")
            stream.outdent()

        self.assign.end(stream)
        self.define.end(stream)

class Write(object):
    """
    >>> from chameleon.core import testing, etree

    Basic write:

    >>> _out, _write, stream = testing.setup_stream()
    >>> _validate = etree.validate
    >>> write = Write(testing.pyexp("'New York'"))
    >>> write.begin(stream)
    >>> write.end(stream)
    >>> exec stream.getvalue()
    >>> _out.getvalue()
    'New York'

    >>> _out, _write, stream = testing.setup_stream('utf-8')
    >>> write = Write(testing.pyexp("'New York'"))
    >>> write.begin(stream)
    >>> write.end(stream)
    >>> exec stream.getvalue()
    >>> _out.getvalue()
    'New York'

    Try-except parts:

    >>> _out, _write, stream = testing.setup_stream()
    >>> write = Write(testing.pyexp('undefined', '"New Delhi"'))
    >>> write.begin(stream)
    >>> write.end(stream)
    >>> exec stream.getvalue()
    >>> _out.getvalue()
    'New Delhi'

    Unicode:

    >>> _out, _write, stream = testing.setup_stream('utf-8')
    >>> write = Write(types.value(repr('La Pe\xc3\xb1a'.decode('utf-8'))))
    >>> write.begin(stream)
    >>> write.end(stream)
    >>> exec stream.getvalue()
    >>> val = _out.getvalue()
    >>> val == 'La Pe\xc3\xb1a'
    True
    >>> type(val) == str
    True
    """

    value = assign = None
    
    def __init__(self, value, defer=False):
        self.assign = Assign(value)
        self.structure = not isinstance(value, types.escape)
        self.defer = defer
        
    def begin(self, stream):
        if not self.defer:
            self.write(stream)
            
    def end(self, stream):
        stream.cook()
        if self.defer:
            self.write(stream)
    
    def write(self, stream):
        temp = stream.save()
        symbols = stream.symbols.as_dict()
        value = self.value
        
        if isinstance(value, types.template):
            value = types.value(value % symbols)

        def write(template):
            stream.write(template % symbols)
            
        if value:
            expr = value
        else:
            self.assign.begin(stream, temp)
            expr = temp

        stream.write("%s = %s" % (stream.symbols.tmp, expr))
        write("if %(tmp)s is not None:")
        stream.indent()

        if stream.encoding is not None:
            stream.coerce_to_string(stream.symbols.tmp)
        else:
            stream.coerce_to_unicode(stream.symbols.tmp)
                        
        if self.structure:
            write("%(write)s(%(tmp)s)")
        else:
            stream.escape(stream.symbols.tmp)
            write("%(write)s(%(tmp)s)")

        stream.outdent()

        # validate XML if enabled
        if config.VALIDATION:
            try:
                _et = etree.import_elementtree()
            except ImportError:
                raise ImportError(
                    "ElementTree (required when XML validation is enabled).")

            stream.symbol_mapping[stream.symbols.validate] = etree.validate
            write("%(validate)s(%(tmp)s)")

        if self.assign:
            self.assign.end(stream)
        stream.restore()

class UnicodeWrite(Write):
    """
    >>> from chameleon.core import testing, etree

    Basic write:

    >>> _out, _write, stream = testing.setup_stream()
    >>> _validate = etree.validate
    >>> write = Write(types.value("'New York'"))
    >>> write.begin(stream)
    >>> write.end(stream)
    >>> exec stream.getvalue()
    >>> _out.getvalue()
    'New York'

    Unicode:

    >>> _out, _write, stream = testing.setup_stream('utf-8')
    >>> write = Write(types.value(repr(unicode('La Pe\xc3\xb1a', 'utf-8'))))
    >>> write.begin(stream)
    >>> write.end(stream)
    >>> exec stream.getvalue()
    >>> val = _out.getvalue()
    >>> val == 'La Pe\xc3\xb1a'
    True
    >>> type(val) == str
    True

    Invalid:

    >>> _out, _write, stream = testing.setup_stream()
    >>> write = Write(types.value("None"))
    >>> write.begin(stream)
    >>> write.end(stream)
    >>> exec stream.getvalue()
    >>> _out.getvalue()
    ''
    """

    def write(self, stream):
        temp = stream.save()

        if self.value:
            expr = self.value
        else:
            self.assign.begin(stream, temp)
            expr = temp

        stream.write("%s(%s)" % (stream.symbols.write, expr))
        
        if not self.value:
            self.assign.end(stream)

        stream.restore()

class Out(object):
    """
    >>> from chameleon.core import testing
      
    >>> _out, _write, stream = testing.setup_stream()
    >>> out = Out('Hello World!')
    >>> out.begin(stream)
    >>> out.end(stream)
    >>> exec stream.getvalue()
    >>> _out.getvalue()
    'Hello World!'
    """
    
    def __init__(self, string, defer=False):
        self.string = string
        self.defer = defer
        
    def begin(self, stream):
        if not self.defer:
            stream.out(self.string)
        
    def end(self, stream):
        stream.cook()
        if self.defer:
            stream.out(self.string)

class UpdateScope(object):
    """Updates variable scope."""
    
    def __init__(self, scope, remote):
        self.scope = scope
        self.remote = remote

    def begin(self, stream):
        stream.write("%s.update(%s)" % (self.scope, self.remote))

    def end(self, stream):
        pass

class Method(object):
    """
    >>> from chameleon.core import testing
      
    >>> _out, _write, stream = testing.setup_stream()
    >>> _scope = {}
    >>> method = Method('test', ('a', 'b', 'c'))
    >>> method.begin(stream)
    >>> stream.write('print a, b, c')
    >>> method.end(stream)
    >>> exec stream.getvalue()
    >>> test(1, 2, 3)
    1 2 3
      
    """

    ret = None
    
    def __init__(self, name, args, ret=None):
        self.name = name
        self.args = args

        if ret is not None:
            self.ret = Assign(ret, '_ret')

    def begin(self, stream):
        stream.write('def %s(%s):' % (self.name, ", ".join(self.args)))
        stream.indent()

    def end(self, stream):
        if self.ret is not None:
            self.ret.begin(stream)
            stream.write('return _ret')
            self.ret.end(stream)
        
        stream.outdent()
        assign = Assign(
            types.value(self.name), "%s['%s']" % \
            (stream.symbols.scope, self.name))
        assign.begin(stream)
        assign.end(stream)
        
