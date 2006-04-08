##############################################################################
#
# Copyright (c) 2005, 2006 Zope Corporation and Contributors.
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

"""
$Id$
"""

from zope.generic.directlyprovides.helper import updateDirectlyProvided



def updateProvides(field, before=None, after=None):
    def decorator(f):
        def new_f(self, value):
            # remember the previous value
            previous_value = getattr(self, field.__name__)

            if previous_value != value:
                # invoke before
                if before:
                    before(self, value, previous_value)

                # call decorated function
                result = f(self, value)

                # update directly provides
                updateDirectlyProvided(self, value, previous_value)

                # invoke after
                if after:
                    after(self, value, previous_value)

                return result
            return None

        new_f.func_name = f.func_name
        return new_f
    return decorator
