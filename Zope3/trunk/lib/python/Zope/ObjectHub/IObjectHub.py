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
$Id: IObjectHub.py,v 1.3 2002/06/25 10:45:46 dannu Exp $
"""

from Zope.Event.IEventChannel import IEventChannel

class IObjectHub(IEventChannel):
    """ObjectHub.
    
    Receives Object Modify Events from the Event Service, and
    changes these into RUID Object Modify Events, then passes
    these on to its PlugIns (possibly via some other EventChannels).
       
    To map Object Modify Events onto RUID Object Modify Events, take
    the location from the Object Modify Event, look up the RUID for this
    location, and create an equivalent RUID Object Modify Event using this
    RUID.
       
    Note that we are concerned with locations and not with Objects.
    An object may have more than one location. That doesn't concern
    us here.
       
    Table of decisions about maintaining the location<->ruid lookup:
       
      Register
      
         if location already in lookup:
             raise ObjectHubError, as this is implies bad state somewhere
         generate new ruid
         place ruid<->location into lookup, to say that we have an
             interesting object
             
         send out ruid object register event to plug-ins, via event channels
         
      Unregister
         
         if location not in lookup:
             raise ObjectHubError, as this is implies bad state somewhere
         remove location<->ruid from lookup
            
         send out ruid unregister event to plug-ins, via event channels
       
      Add (specialises Register)
         
         as Register, except at the end send out ruid object add event
         instead
         
      Modify
         
         if location not in lookup:
             ignore this event, as we're not interested in this object
         else:
             look up ruid for the location
             send out ruid object modify event to plug-ins,
                 via event channels
                
      Move 

         if old_location not in lookup:
             ignore this event, as we're not interested in this object
         elif new_location is in lookup:
             raise ObjectHubError
         else:
             look up ruid for old_location
             change lookup:
                 remove ruid<->old_location
                 add ruid<->new_location
             send out ruid object context-change event to plug-ins,
                 via event channels
         
      Remove (specialises Unregister)

         if old_location not in lookup:
             ignore this event, as we're not interested in this object
         else:
             look up ruid for old_location
             change lookup:
                 remove ruid<->old_location
             send out ruid object remove event to plug-ins,
                 via event channels
    
     # XXX: Possibly add Link to EventChannel.
     #      This implies multiple locations for a ruid. 
     #      We'll refactor later if needed.
        
     # Possibly also add registerObject and unregisterObject methods
     # unless these are better handled by events, or unless we don't
     # need them.
     """

        
    def lookupRuid(location):
        """Returns the ruid int that is mapped to the given location.
        
        Location is either a string, or a sequence of strings.
        It must be absolute, so if it is a string it must start with a '/',
        and if it is a sequence, it must start with an empty string.
        
        ('','whatever','whatever2')
        '/whatever/whatever2'
        
        If there is no ruid, raise Zope.Exceptions.NotFoundError.
        
        """
        
    def lookupLocation(ruid):
        """Returns a location as a string.
        
        If there is no location, raise Zope.Exceptions.NotFoundError.
        """
        
    def getObject(ruid):
        """Returns an object for the given ruid.
        
        If there is no such ruid, raise Zope.Exceptions.NotFoundError.
        If there is no such object, passes through whatever error
        the traversal service raises.
        """

    def register(location):
        """Returns a new ruid for the given location if it is not 
        already registered. 

        It also emits a RuidObjectRegisteredEvent.  Raises an 
        ObjectHubError if the location was previously registered. 
        """

    def unregister(ruid_or_location):
        """Unregister an object identified either by location or by ruid.

        It also emits a RuidObjectUnregisteredEvent. 
        If the Ruid or location wasn't registered a 
        Zope.Exceptions.NotFoundError is raised.
        """ 
