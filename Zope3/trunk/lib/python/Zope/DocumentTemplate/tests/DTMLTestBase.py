##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
"""Document Template Tests

$Id: DTMLTestBase.py,v 1.2 2002/07/11 00:54:01 srichter Exp $
"""

import os
import unittest
from Zope.DocumentTemplate.DT_HTML import HTML


if __name__=='__main__':
    here = os.curdir
else:
    from Zope.DocumentTemplate import tests
    here = tests.__path__[0]

def read_file(name):
    f = open(os.path.join(here, name), 'r')
    res = f.read()
    f.close()
    return res


class ObjectStub:
    def __init__(self, **kw):
        for k, v in kw.items():
            self.__dict__[k]=v

    def __repr__(self):
        return "D(%s)" % `self.__dict__`

def dict(**kw):
    return kw


class DTMLTestBase(unittest.TestCase):

    doc_class = HTML
