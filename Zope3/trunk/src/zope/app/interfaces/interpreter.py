##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Interfaces for Code Interpreters

$Id: interpreter.py,v 1.2 2003/08/21 14:19:23 srichter Exp $
"""
from zope.interface import Interface

class IInterpreterService(Interface):
    """An interpreter service manages the available code interpreters.

    Code interpreters are registered by type, which should be valid content
    type entries based on the W3C standards. An example would be
    'text/server-python'.
    """

    def getInterpreter(type):
        """Return the interpreter for this type.

        If no interpreter is found, raise a ComponentLookupError.
        """

    def queryInterpreter(type, default=None):
        """Return the interpreter for this type.

        If no interpreter is found, return the default value.
        """


class IGlobalInterpreterService(IInterpreterService):

    def provideInterpreter(type, interpreter):
        """Register a new interpreter with the service."""


class IInterpreter(Interface):

    def evaluate(code, globals):
        """Evaluate the code given the global variables."""

    def evaluateRawCode(code, globals):
        """Evaluate the code given the global variables.

        However, this method does a little bit more. Sometimes (or in our case
        often) code might come from an uncontrolled environment, like a page
        template and is not properly formatted, i.e. indentation, so that some
        cleanup is necessary. This method does the cleanup before evaluating
        the code.
        """
