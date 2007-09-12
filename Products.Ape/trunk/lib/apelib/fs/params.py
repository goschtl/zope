##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Functions for encoding/decoding parameter strings.

$Id$
"""

import re

token_re = re.compile(r'([" \t]|\\["\\trn])')
token_replacements = {
    '\\"': '"',
    '\\\\': '\\',
    '\\t': '\t',
    '\\r': '\r',
    '\\n': '\n',
    }

key_re = re.compile(r'[A-Za-z_-][A-Za-z0-9_-]*$')


def split_params(s):
    tokens = re.split(token_re, s)
    params = []
    param = []
    quoting = 0
    for tok in tokens:
        if tok:
            v = token_replacements.get(tok)
            if v:
                param.append(v)
            elif not quoting and (tok == ' ' or tok == '\t'):
                if param:
                    params.append(''.join(param))
                    param = []
            else:
                if tok == '"':
                    quoting = not quoting
                    if not quoting:
                        params.append(''.join(param))
                        param = []
                else:
                    param.append(tok)
    leftover = ''.join(param).strip()
    if leftover:
        params.append(leftover)
    return params


def escape_param(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace(
        '\r', '\\r').replace('\n', '\\n').replace('\t', '\\t')


def string_to_params(s):
    """Decodes a string of the format 'a="..." b="..."'.

    Returns a list of (key, value) pairs.
    """
    params = split_params(s)
    res = []
    for param in params:
        p = param.split('=', 1)
        if len(p) == 1:
            k = p[0]
            v = ''
        else:
            k, v = p
        res.append((k, v))
    return res


def params_to_string(params):
    """Encodes a list of (key, value) pairs as a string."""
    parts = []
    for k, v in params:
        if not key_re.match(k):
            raise ValueError, 'Bad parameter name: %s' % repr(k)
        if v:
            parts.append('%s="%s"' % (k, escape_param(v)))
        else:
            parts.append(k)
    return ' '.join(parts)

