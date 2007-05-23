##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
$Id: layer.py 197 2007-04-13 05:03:32Z rineichen $
"""

import zope.interface
from z3c.website import sample
from z3c.demo.howto import interfaces


class HowToSample(sample.Sample):
    """The HowToSample object must provide the ISample interface.
    
    The simples way to do this is, if you use the z3c.website.sample.Sample
    class as base.
    
    You can enhance this object here if you need to or mixin other base classes
    as well.
    """

    zope.interface.implements(interfaces.IHowToSample)
