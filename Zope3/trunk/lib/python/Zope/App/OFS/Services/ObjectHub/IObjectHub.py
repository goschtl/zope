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
$Id: IObjectHub.py,v 1.3 2002/11/26 19:02:49 stevea Exp $
"""

from Zope.Event.IEventChannel import IEventChannel

class ObjectHubError(Exception):
    pass

class IObjectHub(IEventChannel):
    """ObjectHub.
    
    Receives Object Modify Events from the Event Service, and
    changes these into Hub Id Object Modify Events, then passes
    these on to its subscribers.
       
    To map Object Modify Events onto Hub Id Object Modify Events, take
    the location from the Object Modify Event, look up the Hub Id for this
    location, and create an equivalent Hub Id Object Modify Event using this
    Hub Id.
       
    Note that we are concerned with locations and not with Objects.
    An object may have more than one location. That doesn't concern
    us here.
    
    We're only interested in what happens during the time during which
    an object is registered with the hub -- between ObjectRegistered
    and ObjectUnregistered events.  As one consequence of that, we do
    care about object removals, but not (directly) about object
    additions.
       
    Table of decisions about maintaining the location<->Hub Id lookup:
       
      Register
      
         if location already in lookup:
             raise ObjectHubError, as this is implies bad state somewhere
         generate new hub id
         place hub id<->location into lookup, to say that we have an
             interesting object
             
         send out hub id object register event to subscribers
         
      Unregister
         
         if location not in lookup:
             raise ObjectHubError, as this is implies bad state somewhere
         remove location<->hub id from lookup
            
         send out hub id unregister event to subscribers
         
      Modify
         
         if location not in lookup:
             ignore this event, as we're not interested in this object
         else:
             look up hub id for the location
             send out hub id object modify event to subscribers
                
      Move 

         if old_location not in lookup:
             ignore this event, as we're not interested in this object
         elif new_location is in lookup:
             raise ObjectHubError
         else:
             look up hub id for old_location
             change lookup:
                 remove hub id<->old_location
                 add hub id<->new_location
             send out hub id object context-change event to subscribers

      Remove (specializes Unregister)

         if old_location not in lookup:
             ignore this event, as we're not interested in this object
         else:
             look up hub id for old_location
             change lookup:
                 remove hub id<->old_location
             send out hub id object remove event to subscribers
     """
    
    def getHubId(obj_or_loc):
        """Returns the hub id int that is mapped to the given location
        or wrapped object.
        
        Location is either a unicode, or a tuple of unicodes, or an
        ascii string, or a tuple of ascii strings.
        (See Zope/App/Traversing/__init__.py)
        It must be absolute, so if it is a string it must start with a u'/',
        and if it is a tuple, it must start with an empty string.
        
        (u'',u'whatever',u'whatever2')
        u'/whatever/whatever2'
        
        If there is no hub id, raise Zope.Exceptions.NotFoundError.
        """
        
    def getLocation(hubid):
        """Returns a location as a tuple of unicodes.
        
        If there is no location, raise Zope.Exceptions.NotFoundError.
        """
        
    def getObject(hubid):
        """Returns an object for the given hub id.
        
        If there is no such hub id, raise Zope.Exceptions.NotFoundError.
        If there is no such object, passes through whatever error
        the traversal service raises.
        """

    def register(obj_or_loc):
        """Returns a new hub id for the given location or wrapped object
        if it is not already registered. 

        It also emits a HubIdObjectRegisteredEvent.  Raises an 
        ObjectHubError if the location was previously registered. 
        """

    def unregister(obj_or_loc_or_hubid):
        """Unregister an object by wrapped object, by location, or by hubid.

        It also emits a HubIdObjectUnregisteredEvent. 
        If the hub id or location wasn't registered a 
        Zope.Exceptions.NotFoundError is raised.
        """

    def numRegistrations():
        """Returns the number of location<-->hubid registrations held.
        """

    def registrations(location='/'):
        """Returns a sequence of the registrations at and within the
        given location.

        A registration a tuple (location, hib_id).
        """

