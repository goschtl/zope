##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
$Id: FileUpload.py,v 1.1 2002/11/11 21:05:16 jim Exp $
"""

__metaclass__ = type

from Zope.App.Forms.Views.Browser.Widget import FileWidget
from Zope.App.Forms.Widget import CustomWidget

class FileUpload:
    """File editing mix-in that uses a file-upload widget.
    """

    data = CustomWidget(FileWidget)
    
    

__doc__ = FileUpload.__doc__ + __doc__

