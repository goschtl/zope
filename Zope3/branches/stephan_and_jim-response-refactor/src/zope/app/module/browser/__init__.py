##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Handle form to create module

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.proxy import removeAllProxies

class ViewModule(object):

    def getModuleObjects(self):
        module = removeAllProxies(self.context.getModule())
        remove_keys = ['__name__', '__builtins__', '_p_serial']

        L = [(getattr(obj, '__name__', id),
              getattr(obj, '__doc__', ''),
              type(obj).__name__)
             for id, obj in module.__dict__.items()
             if id not in remove_keys]
        L.sort()

        l_dict = [{"name": name, "doc": doc, "objtype": objtype}
                  for name, doc, objtype in L]

        for dic in l_dict:
                if dic['objtype'].find('Class') != -1:
                    dic['objtype'] = 'Class'
                if dic['objtype'].find('Function') != -1:
                    dic['objtype'] = 'Function'
        return l_dict
