##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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

Revision information:
$Id: Logger.py,v 1.4 2002/12/05 13:44:13 stevea Exp $
"""

from ISubscriber import ISubscriber
from zLOG import LOG,BLATHER
from pprint import pprint
from StringIO import StringIO

class Logger:

    __implements__ = ISubscriber

    def __init__(self,severity=BLATHER):
        self.severity = severity
        
    def notify(self, event):
        c = event.__class__
        detail = StringIO()
        #data = event.__dict__.items()
        #data.sort()
        #pprint(data, detail)
        print >>detail, 'XXX detail temporarily disabled'
        LOG('Event.Logger',
            self.severity,
            c.__module__+'.'+c.__name__,
            detail.getvalue())
        
    
