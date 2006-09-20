##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Skin Browser Module

$Id$
"""
__docformat__ = 'restructuredtext'
import zope.interface
from zope.tal import dummyengine, htmltalparser, talinterpreter

class Devnull(object):
    def write(self, s):
        pass


class ValidatorEngine(dummyengine.DummyEngine):

    def __init__(self, macros=None):
        self.expressions = []
        dummyengine.DummyEngine.__init__(self, macros)

    def evaluate(self, expression):
        assert (expression.startswith("$") and expression.endswith("$"),
                expression)
        expression = expression[1:-1]
        match = dummyengine.name_match(expression)
        if match:
            type, expr = match.group(1, 2)
        else:
            type = "path"
            expr = expression
        # Only support path for now; we probably want to support string as well
        if type == 'path':
            if expr not in self.expressions:
                self.expressions.append((expr, self.position))
        elif type == "not":
            self.evaluate(expr)

        return ''

    def evaluateSequence(self, expr):
        self.evaluate(expr)
        return (0,) # dummy

    def evaluateBoolean(self, expr):
        self.evaluate(expr)
        return True # dummy


def getUsedExpressions(filename, macro=None):

    engine = ValidatorEngine()

    engine.file = filename
    p = htmltalparser.HTMLTALParser()
    p.parseFile(filename)
    program, macros = p.getCode()

    if macro is not None:
        program = macros[macro]

    talinterpreter.TALInterpreter(
        program, macros, engine, stream=Devnull(), metal=False)()
    return engine.expressions


class ValidationMessage(object):
    """A validation message."""
    title = u'Message'
    description = u''

    def __init__(self, expression, position, variable):
        self.expression = expression
        self.line, self.column = position
        self.variable = variable

class ValidationError(ValidationMessage):
    pass

class ValidationWarning(ValidationMessage):
    pass

class FieldMissing(ValidationError):
    title = u'Field Missing'
    description = (u'The field is not defined in the view interface or the '
                   u'implementation (view class).')

class InterfaceFieldMissing(ValidationWarning):
    title = u'Interface Field Missing'
    description = (u'The field is not defined in the view interface but '
                   u'implemented in the view class.')

class ContextDirectlyUsed(ValidationWarning):
    title = u'Context Used'
    description = (u'The context namespace was directly used in the '
                   u'template.')


def compareExpressionsToView(expressions, factory):
    # Get a list of attributes/fields and methods
    implements = zope.interface.implementedBy(factory)
    iface_names = zope.interface.interface.InterfaceClass(
        'ITemporary', tuple(implements.interfaces())).names(True)
    obj_names = list(factory.__dict__)
    # Create the notification container
    messages = []
    for expression, position in expressions:
        path = expression.split('/')
        if path[0] == 'view':
            if path[1] not in iface_names:
                if path[1] not in obj_names:
                    messages.append(
                        FieldMissing(expression, position, path[1]))
                else:
                    messages.append(
                        InterfaceFieldMissing(expression, position, path[1]))
        elif path[0] == 'context':
            messages.append(
                ContextDirectlyUsed(expression, position, path[1]))
    return messages
