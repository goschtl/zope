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
"""

$Id: Arguments.py,v 1.2 2002/07/22 20:15:28 jeremy Exp $
"""

import re
from Persistence.PersistentMapping import PersistentMapping
from Interface.Common.Mapping import IEnumerableMapping

unparmre = re.compile(r'([\000- ]*([^\000- ="]+))')
parmre = re.compile(r'([\000- ]*([^\000- ="]+)=([^\000- ="]+))')
qparmre = re.compile(r'([\000- ]*([^\000- ="]+)="([^"]*)")')

InvalidParameter = 'Invalid Parameter'

class Arguments(PersistentMapping):
    """Hold arguments of SQL Script"""

    __implements__ = IEnumerableMapping


def parseArguments(text, result=None):
    """Parse argument string."""

    # Make some initializations
    if result is None:
        result  = {}

    __traceback_info__ = text

    # search for the first argument assuming a default value (unquoted) was
    # given
    match_object = parmre.match(text)

    if match_object:
        name    = match_object.group(2)
        value   = {'default': match_object.group(3)}
        length  = len(match_object.group(1))

    else:
        # search for an argument having a quoted default value 
        match_object = qparmre.match(text)

        if match_object:
            name    = match_object.group(2)
            value   = {'default': match_object.group(3)}
            length  = len(match_object.group(1))

        else:
            # search for an argument without a default value
            match_object = unparmre.match(text)

            if match_object:
                name    = match_object.group(2)
                value   = {}
                length  = len(match_object.group(1))
            else:
                # We are done parsing
                if not text or not text.strip():
                    return Arguments(result)
                raise InvalidParameter, text

    # Find type of argument (int, float, string, ...)
    lt = name.find(':')
    if lt > 0:
        if len(name) > lt+1 and name[lt+1] not in ('"', "'", '='):
            value['type'] = name[lt+1:]
            name = name[:lt]
        else:
            raise InvalidParameter, text

    result[name] = value

    return parseArguments(text[length:], result)
