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

class ILivePageEvent(Interface) :
    """ LivePage events are broadcasted from server side LivePage clients
        to their browser counterparts.
        
        Each event consist of description line and optional extra infos.
        
        We use a structured object here because we often have the situation
        that a single DOM element is frequently modified.
        
        The format of the description line is free, it's up to the
        client to interpret the description in the intended way.
        
    """
                
    def __str__() :
        """
        The __str__ method serializes the event in a way that it can be
        interpreted by the JavaScript Client.
        """
        
class IVerbEvent(ILivePageEvent) :
    """ An abstract event with an associated verb that can be used
        as a utility name for event factories and other purposes.
    """
    
    verb = Attribute("Describes the event in a single word.")

class ILocationEvent(ILivePageEvent) :
    """ An abstract event that carries information about the location of the
        event.
    """

    where = Attribute("Identifies the location of the event.")

class IPersonEvent(ILivePageEvent) :
    """ An abstract event that carries information about the user who
        triggered the event.
    """

    who = Attribute("Identifies the location of the event.")


class IIdleEvent(IVerbEvent) :
    """ An idle event that describes that nothing happened. """

class IReloadEvent(IVerbEvent) :
    """ A reload event that can be used to enforce a page reload. """

class ICloseEvent(IVerbEvent) :
    """ A user has closed the browser window.
    """
    
    uuid = Attribute("Identifies the client browser page.")

class IErrorEvent(IVerbEvent) :
    """ Am error event that can be used to inform the clients about
        server errors.
    """
    
class ILoginEvent(ILocationEvent, IPersonEvent) :
    """ A login event that can be used to notify about new users. 
    """
            
class ILogoutEvent(ILocationEvent, IPersonEvent) :
    """ A logout event that can be used to notify about leaving users. 
    """
    
   
class IModifyElementEvent(IVerbEvent) :
    """ Describes a modification of a page element. The modification
        is described by a verb and an id. 
        
        The description line is simply a string
        with words seperated by spaces.
    """  

class ISetAttribute(IModifyElementEvent) :
    """ Set an attribute of a DOM element.    
    """            


class IHTMLUpdateEvent(IModifyElementEvent) :
    """ A page update event that provides a html fragment in addition
        to the description.
    """
    
    html = Attribute("A HTML fragment.")

   
class IAppend(IHTMLUpdateEvent) :
    """ Append a html fragment as a child node to an existing DOM element. 
    """    
    
class IUpdate(IHTMLUpdateEvent) :
    """ Update the inner HTML of a dom element with the HTML fragment. 
    """

class IClientEventFactory(Interface) :
    """ A named utility that returns a factory for ILivePageEvents. """
    
class ILivePage(IAjaxPage) :
    """ A web page that is able to subscribe to server events and updates
        automatically via ILivePageEvent events.
    """

    def notify(event) :
        """ An event handler that informs clients about changes. """
               
    def nextClientId() :
        """ Returns a new client id. """
        
    def output(uuid) :
        """ Returns the output event for a single client. """
        
    def input(uuid, event) :
        """ Sends an input event to the livepages specified
            by the events recipients attribute.
        """
        
    def sendEvent(event) :
        """        
        Sends a livepage event to the recipients of this event.
                   
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
    
    def getClientsFor(user_id, where=None) :
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
        
    def addEvent(event) :
        """
        Adds a notification to the the clients specified by where
        and / or recipients.
        """

    def whoIsOnline(where) :
        """ Returns the ids of the principals that are using livepages. """
         
        
    
class ILivePageClient(Interface) :
    """ The server side internal representation of a livepage client. """
    