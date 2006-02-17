##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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

$Id: interfaces.py 39651 2005-10-26 18:36:17Z oestermeier $
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface
from zope.interface import Attribute
from zope.interface.common.mapping import IEnumerableMapping

from zope.schema import Bytes, BytesLine

from zope.app.container.interfaces import IContainer
from zope.i18n import MessageIDFactory

from zorg.ajax.interfaces import IAjaxPage

_ = MessageIDFactory("zorg.live")



class ILivePage(IAjaxPage) :
    """ A web page that is able to subcribe to server events and updates
        automatically via javascript calls.
    """

    def notify(event) :
        """ An event handler that informs clients about changes. """
               
    def nextClientId() :
        """ Returns a new client id. """
        
    def output(uuid, outputNum) :
        """ Returns the output (descriptions of changes) of a single client. """
        
    def input(uuid, handler_name, arguments) :
        """ Sends input to livepages. """
        
    def sendResponse(response, group_id, recipients="all") :
        """
        
        Sends a livepage response to the clients of a group. 
        
        A response consits of a leading command line 
        and optional html body data.
            
        Should be implemented as a classmethod.
        """
    
    def render() :
        """ Renders the HTML representation of the client. """


class ILivePageManager(Interface) :
    """ A global utility that provides access to LivePageClients. """
    
        
    def cacheResult(result) :
        """ 
        Caches a result for efficient access. 
        
        Returns a UUID which can be used to retrive the result.
        """
        
    def fetchResult(uuid, clear=True) :
        """ 
        Accesses the cached result and clears the memory
        """
        
    def register(client, uuid=None) :
        """
        Register a client. 
        
        Uses the provided uuid or generates a new one.
        """
     
    def unregister(client) :
        """
        Unregister a client. 
        """
    
    def getClientsFor(user_id, group_id=None) :
        """ Get clients for a specific user.
        """
 
    def get(uuid, default=None) :
        """
        Returns a client that is registered under the uuid or 
        returns the provided default.
        """
        
    def checkAlive(verbose=False) :
        """ Checks whether clients are alive. """        
        
    def __iter__(self) :
        """
        Iterates over all clients which are still alive.
        Unregisters all unnecessary clients.
        """
        
    def addOutput(output, group_id=None, recipients="all") :
        """
        Adds a notification to the the clients specified by group_id
        and / or recipients.
        """

    def whoIsOnline(group_id) :
        """ Returns the ids of the principals that are using livepages. """
         
        
    
class ILivePageClient(Interface) :
    """ The server side internal representation of a livepage client. """
    