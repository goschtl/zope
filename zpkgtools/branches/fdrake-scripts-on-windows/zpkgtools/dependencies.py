##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Support for handling dependency information.

Dependencies are stored in a file format with one dependency per line.
Leading and trailing whitespace is ignored.  Blank lines and lines
with "\#" as the first non-blank character are ignored.  Dependencies
are identified using resource identifiers.

"""

import sets


def load(f):
    """Load a set of dependencies from an open file.

    :return: A set of dependencies listed in `f`.
    :rtype: `sets.Set`

    :param f: File object to read from.

    """
    deps = sets.Set()
    for line in f:
        line = line.strip()
        if line[:1] in ("", "#"):
            continue
        deps.add(line)
    return deps
