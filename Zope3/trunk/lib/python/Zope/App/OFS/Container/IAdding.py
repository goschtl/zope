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

$Id: IAdding.py,v 1.2 2002/10/02 21:35:47 jeremy Exp $
"""

from Interface.Attribute import Attribute

from Zope.ComponentArchitecture.IView import IView

class IAdding(IView):

    def add(content):
         """Add content object to container.

         Add using the name in contentName.  Returns the added object
         in the context of its container.

         If contentName is already used in container, raises
         Zope.App.OFS.Container.Exceptions.DuplicateIDError.
         """

    contentName=Attribute(
         """the content name, as usually set by the Adder traverser.

         If the content name hasn't been defined yet, returns None.

         Some creation views might use this to optionally display the
         name on forms.
         """
         )

    def nextURL():
         """Return the URL that the creation view should redirect to

         This is called by the creation view after calling add.

         It is the adder's responsibility, not the creation view's to
         decide what page to display after content is added.
         """
