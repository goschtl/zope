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
"""ctory.py,v 1.1.2.2 2002/04/02 02:20:40 srichter Exp $
"""

from Interface import Interface
import copy


class IRequestFactory(Interface):
    """This is a pure read-only interface, since the values are set through
       a ZCML directive and we shouldn't be able to change them.
    """

    def realize(db):
        """Realize the factory by initalizing the publication.

           The method returns the realized object.
        """
        

    def __call__(input_stream, output_steam, env):
        """Call the Request Factory"""





class RequestFactory:
    """This class will generically create RequestFactories. This way I do
       not have to create a method for each Server Type there is.
    """

    __implements__ =  IRequestFactory

    def __init__(self, publication, request):
        """Initialize Request Factory"""
        self._pubFactory = publication
        self._publication = None
        self._request = request


    ############################################################
    # Implementation methods for interface
    # Zope.StartUp.RequestFactory.IRequestFactory

    def realize(self, db):
        'See Zope.StartUp.RequestFactory.IRequestFactory'
        realized = copy.copy(self)
        realized._publication = realized._pubFactory(db)
        return realized
    

    def __call__(self, input_stream, output_steam, env):
        'See Zope.StartUp.RequestFactory.IRequestFactory'
        request = self._request(input_stream, output_steam, env)
        request.setPublication(self._publication)
        return request

    #
    ############################################################
