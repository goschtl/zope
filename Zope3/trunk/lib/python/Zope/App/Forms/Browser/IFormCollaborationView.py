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
$Id: IFormCollaborationView.py,v 1.2 2002/11/18 22:41:39 jim Exp $
"""

from Interface import Interface

class IFormCollaborationView(Interface):
    """Views that collaborate to create a single form

    When a form is applied, the changes in the form need to
    be applied to individual views, which update objects as
    necessary. 
    """

    def __call__():
       """Render the view as a part of a larger form.

       Form input elements should be included, prefixed with the
       prefix given to setPrefix.

       'form' and 'submit' elements should not be included. They
       will be provided for the larger form.
       """

    def setPrefix(prefix):
       """Set the prefix used for names of input elements

       Element names should begin with the given prefix,
       followed by a dot.
       """

    def update():
       """Update the form with data from the request.
       """

__doc__ = IFormCollaborationView.__doc__ + __doc__
