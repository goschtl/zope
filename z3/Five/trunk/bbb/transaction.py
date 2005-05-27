##############################################################################
#
# Copyright (c) 2005 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Transaction legacy package.

$Id$
"""
def begin():
    get_transaction().begin()

def commit(sub=False):
    get_transaction().commit(sub)

def abort(sub=False):
    get_transaction().abort(sub)

get_transaction = get = get_transaction
