##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
"""
Objects for packages that have been uninstalled.
"""
import string, SimpleItem, Globals, Acquisition
from Acquisition import Acquired
import Persistence
from thread import allocate_lock
from zLOG import LOG, WARNING

broken_klasses={}
broken_klasses_lock = allocate_lock()

class BrokenClass(Acquisition.Explicit, SimpleItem.Item, 
                  Persistence.Overridable):
    _p_changed=0
    meta_type='Broken Because Product is Gone'
    icon='p_/broken'
    product_name='unknown'
    id='broken'

    manage_page_header = Acquired
    manage_page_footer = Acquired

    def __getstate__(self):
        raise SystemError, (
            """This object was originally created by a product that
            is no longer installed.  It cannot be updated.
            """)

    def __getattr__(self, name):
        if name[:3]=='_p_':
            return BrokenClass.inheritedAttribute('__getattr__')(self, name)
        raise AttributeError, name

    manage=manage_main=Globals.DTMLFile('dtml/brokenEdit',globals())
    manage_workspace=manage
    

def Broken(self, oid, pair):
    broken_klasses_lock.acquire()
    try:
        if broken_klasses.has_key(pair):
            klass = broken_klasses[pair]
        else:
            module, klassname = pair
            d={'BrokenClass': BrokenClass}
            exec ("class %s(BrokenClass): ' '; __module__=%s"
                  % (klassname, `module`)) in d
            klass = broken_klasses[pair] = d[klassname]
            module=string.split(module,'.')
            if len(module) > 2 and module[0]=='Products':
                klass.product_name= module[1]
            klass.title=(
                'This object from the %s product '
                'is broken!' %
                klass.product_name)
            klass.info=(
                'This object\'s class was %s in module %s.' %
                (klass.__name__, klass.__module__))
            LOG('ZODB', WARNING, 'Could not import class %s '
                'from module %s' % (`klass.__name__`, `klass.__module__`))
    finally:
        broken_klasses_lock.release()
    if oid is None: return klass
    i=klass()
    i._p_oid=oid
    i._p_jar=self
    return i
