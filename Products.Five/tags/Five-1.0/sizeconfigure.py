##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Use structured monkey-patching to enable ``ISized`` adapters for
Zope 2 objects.

$Id$
"""
from zope.app.size.interfaces import ISized
from Products.Five.fiveconfigure import isFiveMethod

def get_size(self):
    size = ISized(self, None)
    if size is not None:
	unit, amount = size.sizeForSorting()
	if unit == 'byte':
	    return amount
    method = getattr(self, '__five_original_get_size', None)
    if method is not None:
        return self.__five_original_get_size()

get_size.__five_method__ = True

def classSizable(class_):
    """Monkey the class to be sizable through Five"""
    # tuck away the original method if necessary
    if hasattr(class_, "get_size") and not isFiveMethod(class_.get_size):
	class_.__five_original_get_size = class_.get_size
    class_.get_size = get_size
    
def sizable(_context, class_):
    _context.action(
        discriminator = ('five:sizable', class_),
        callable = classSizable,
        args=(class_,)
        )
