import re
import parser

from zope import interface
from zope import component

from chameleon.core import types
from chameleon.core import parsing

import interfaces

class ExpressionTranslator(object):
    """Base class for TALES expression translation."""

    interface.implements(interfaces.IExpressionTranslator)
    
    re_pragma = re.compile(r'^\s*(?P<pragma>[a-z]+):')
    re_method = re.compile(r'^(?P<name>[A-Za-z0-9_]+)'
                           '(\((?P<args>[A-Za-z0-9_]+\s*(,\s*[A-Za-z0-9_]+)*)\))?')

    def __init__(self):
        self.translator = self
    
    def pragma(self, name):
        return component.queryUtility(
            interfaces.IExpressionTranslator, name=name) or \
            component.queryAdapter(
            self, interfaces.IExpressionTranslator, name=name)
    
    def declaration(self, string):
        """Variable declaration.
        
        >>> declaration = ExpressionTranslator().declaration

        Single variable:

        >>> declaration("variable")
        declaration('variable')

        Multiple variables:

        >>> declaration("variable1, variable2")
        declaration('variable1', 'variable2')

        Repeat not allowed:

        >>> declaration('repeat')
        Traceback (most recent call last):
         ...
        ValueError: Invalid variable name 'repeat' (reserved).

        >>> declaration('_disallowed')
        Traceback (most recent call last):
         ...
        ValueError: Invalid variable name '_disallowed' (starts with an underscore).
        """

        variables = []
        for var in string.split(', '):
            var = var.strip()

            if var in ('repeat',):
                raise ValueError, "Invalid variable name '%s' (reserved)." % var

            if var.startswith('_') and not var.startswith('_tmp'):
                raise ValueError(
                    "Invalid variable name '%s' (starts with an underscore)." % var)

            variables.append(var)

        return types.declaration(variables)

    def mapping(self, string):
        """Semicolon-separated mapping.
        
        >>> mapping = ExpressionTranslator().mapping

        >>> mapping("abc def")
        mapping(('abc', 'def'),)

        >>> mapping("abc def;")
        mapping(('abc', 'def'),)

        >>> mapping("abc")
        mapping(('abc', None),)

        >>> mapping("abc;")
        mapping(('abc', None),)

        >>> mapping("abc; def ghi")
        mapping(('abc', None), ('def', 'ghi'))
        """

        defs = string.split(';')
        mappings = []
        for d in defs:
            d = d.strip()
            if d == '':
                continue

            while '  ' in d:
                d = d.replace('  ', ' ')

            parts = d.split(' ')
            if len(parts) == 1:
                mappings.append((d, None))
            elif len(parts) == 2:
                mappings.append((parts[0], parts[1]))
            else:
                raise ValueError, "Invalid mapping (%s)." % string

        return types.mapping(mappings)

    def definitions(self, string):
        """Semi-colon separated variable definitions.
        
        >>> class MockExpressionTranslator(ExpressionTranslator):
        ...     def tales(self, string, escape=None):
        ...         if string == '' or ';' in string.replace("';'", "''"):
        ...             raise SyntaxError()
        ...         return types.value(string.strip())

        >>> definitions = MockExpressionTranslator().definitions
        
        Single define:
        
        >>> definitions("variable expression")
        definitions((declaration('variable'), value('expression')),)
        
        Multiple defines:
        
        >>> definitions("variable1 expression1; variable2 expression2")
        definitions((declaration('variable1'), value('expression1')),
                    (declaration('variable2'), value('expression2')))

        Defines are only split on semi-colon if a valid declaration is
        available.
        
        >>> definitions("variable1 ';'+expression1; variable2 expression2")
        definitions((declaration('variable1'), value("';'+expression1")),
                    (declaration('variable2'), value('expression2')))

        Tuple define:
        
        >>> definitions("(variable1, variable2) (expression1, expression2)")
        definitions((declaration('variable1', 'variable2'),
                    value('(expression1, expression2)')),)

        Global defines:

        >>> definitions("global variable expression")
        definitions((declaration('variable', global_scope=True), value('expression')),)

        >>> definitions("variable1 expression1; global variable2 expression2")
        definitions((declaration('variable1'), value('expression1')),
                    (declaration('variable2', global_scope=True), value('expression2')))

        Space, the 'in' operator and '=' may be used to separate
        variable from expression.

        >>> definitions("variable in expression")
        definitions((declaration('variable'), value('expression')),)        
        
        >>> definitions("variable1 = expression1; variable2 = expression2")
        definitions((declaration('variable1'), value('expression1')),
                    (declaration('variable2'), value('expression2')))

        >>> definitions("variable1=expression1; variable2=expression2")
        definitions((declaration('variable1'), value('expression1')),
                    (declaration('variable2'), value('expression2')))
        
        A define clause that ends in a semicolon:
        
        >>> definitions("variable expression;")
        definitions((declaration('variable'), value('expression')),)
        
        A define clause with a trivial expression (we do allow this):
        
        >>> definitions("variable")
        definitions((declaration('variable'), None),)
        
        A proper define clause following one with a trivial expression:
        
        >>> definitions("variable1 expression; variable2")
        definitions((declaration('variable1'), value('expression')),
                    (declaration('variable2'), None))
        """

        string = string.replace('\n', '').strip()

        defines = []
        i = 0
        while i < len(string):
            while string[i] == ' ':
                i += 1

            global_scope = False
            if string[i:].startswith('global'):
                global_scope = True
                i += 6

            # get variable definition
            if string[i] == '(':
                j = string.find(')', i+1)
                if j == -1:
                    raise ValueError, "Invalid variable tuple definition (%s)." % string
                var = self.declaration(string[i+1:j])
                j += 1
            else:
                j = string.find('=', i + 1)
                k = string.find(' ', i + 1)
                if k < j and k > -1 or j < 0:
                    j = k
                
                if j < 0:
                    var = self.declaration(string[i:])
                    j = len(string)
                else:
                    var = self.declaration(string[i:j])

            var.global_scope = global_scope
            
            # get expression
            i = j + len(string) - j - len(string[j:].lstrip())

            token = string[i:]
            if token.startswith('=='):
                raise ValueError("Invalid variable definition (%s)." % string)
            elif token.startswith('='):
                i += 1
            elif token.startswith('in '):
                i += 3

            try:
                expr = self.tales(string[i:], ';')
                j = -1
            except SyntaxError, e:
                expr = None
                j = len(string)
            
            while j > i:
                j = string.rfind(';', i, j)
                if j < 0:
                    raise e

                try:
                    expr = self.tales(string[i:j], ';')
                except SyntaxError, e:
                    if string.rfind(';', i, j) > 0:
                        continue
                    raise e
                
                break
                
            defines.append((var, expr))

            if j < 0:
                break
            
            i = j + 1

        return types.definitions(defines)

    def definition(self, string):
        defs = self.definitions(string)
        if len(defs) != 1:
            raise ValueError, "Multiple definitions not allowed."

        return defs[0]

    def output(self, string):
        """String output; supports 'structure' keyword.
        
        >>> class MockExpressionTranslator(ExpressionTranslator):
        ...     def translate(self, string, escape=None):
        ...         return types.value(string)

        >>> output = MockExpressionTranslator().output

        >>> output("context/title")
        escape(value('context/title'),)

        >>> output("context/pretty_title_or_id|context/title")
        escape(value('context/pretty_title_or_id'), value('context/title'))

        >>> output("structure context/title")
        value('context/title')        
        """
        
        if string.startswith('structure '):
            return self.tales(string[len('structure'):])
        
        expression = self.tales(string)

        if isinstance(expression, types.parts):
            return types.escape(expression)

        return types.escape((expression,))
            
    def tales(self, string, escape=None):
        """We need to implement the ``validate`` and
        ``translate``-methods. Let's define that an expression is
        valid if it contains an odd number of characters.
        
        >>> class MockExpressionTranslator(ExpressionTranslator):
        ...     def translate(self, string, escape=None):
        ...         return types.value(string)

        >>> tales = MockExpressionTranslator().tales
                
        >>> tales('a')
        value('a')

        >>> tales('a|b')
        parts(value('a'), value('b'))
        """

        string = string.replace('\n', '').strip()

        if not string:
            return types.parts()

        parts = []

        # default translator is ``self``
        translator = self

        i = j = 0
        while i < len(string):
            match = self.re_pragma.match(string[i:])
            if match is not None:
                pragma = match.group('pragma')
                translator = self.pragma(pragma)
                if translator is not None:
                    i += match.end()
                    continue

                translator = self

            j = string.find('|', j + 1)
            if j == -1:
                j = len(string)

            expr = string[i:j]

            try:
                value = translator.translate(expr, escape)
            except Exception, e:
                if j < len(string):
                    continue

                # re-raise with traceback
                value = translator.translate(expr, escape)

            parts.append(value)
            translator = self
            
            i = j + 1

        if len(parts) == 1:
            return parts[0]

        return types.parts(parts)

    def split(self, string):
        return parsing.interpolate(string, self.translator.tales)

class PythonTranslator(ExpressionTranslator):
    """Implements Python expression translation."""
    
    def translate(self, string, escape=None):
        """We use the ``parser`` module to determine if
        an expression is a valid python expression."""

        if isinstance(string, unicode):
            string = string.encode('utf-8')
            
        parser.expr(string.strip())
        
        if isinstance(string, str):
            string = string.decode('utf-8')

        return types.value(string.strip())

python_translator = PythonTranslator()

class StringTranslator(ExpressionTranslator):
    """Implements string translation expression."""

    component.adapts(interfaces.IExpressionTranslator)
    
    re_interpolation = re.compile(r'(?P<prefix>[^\\]\$|^\$)({((?P<expression>.*)})?|'
                                  '(?P<variable>[A-Za-z][A-Za-z0-9_]*))')
    
    def __init__(self, translator):
        self.translator = translator

    def translate(self, string, escape=None):
        parts = self.split(string)
        
        if escape is not None:
            parts = map(
                lambda part: isinstance(part, types.expression) and \
                part or self._unescape(part, escape), parts)

        return types.join(parts)            

    def _unescape(self, string, symbol):
        """
        >>> unescape = StringTranslator(None)._unescape
        
        >>> unescape('string:Hello World', ';')
        'string:Hello World'
        
        >>> unescape('; string:Hello World', ';')
        Traceback (most recent call last):
         ...
        SyntaxError: Must escape symbol ';'.

        >>> unescape(';; string:Hello World', ';')
        '; string:Hello World'

        >>> unescape('string:Hello World;', ';')
        'string:Hello World;'
        """

        i = string.rfind(symbol)
        if i < 0 or i == len(string) - 1:
            return string
        
        j = string.rfind(symbol+symbol)
        if j < 0 or i != j + 1:
            raise SyntaxError(
                "Must escape symbol %s." % repr(symbol))
        
        return string.replace(symbol+symbol, symbol)

