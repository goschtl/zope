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

$Id: event.py 39651 2005-10-26 18:36:17Z oestermeier $
"""
__docformat__ = 'restructuredtext'

from zope.interface import implements
from zope.interface import directlyProvides

from zope.app import zapi

from zorg.live.page.interfaces import ILivePageEvent
from zorg.live.page.interfaces import IIdleEvent
from zorg.live.page.interfaces import IReloadEvent
from zorg.live.page.interfaces import ICloseEvent
from zorg.live.page.interfaces import IErrorEvent
from zorg.live.page.interfaces import ILoginEvent
from zorg.live.page.interfaces import ILogoutEvent
from zorg.live.page.interfaces import IAppend
from zorg.live.page.interfaces import IUpdate
from zorg.live.page.interfaces import ISetAttribute
from zorg.live.page.interfaces import IModifyElementEvent
from zorg.live.page.interfaces import IClientEventFactory

class LivePageEvent(object) :
    """ LivePage events are broadcasted from server side LivePage clients
        to their browser counterparts.
        
        Each event consist of description line and optional extra infos.
        
        We use a structured object here because we often have the situation
        that a single DOM element is frequently modified.
        
        The format of the description line is free, it's up to the
        client to interpret the description in the intended way.
        
        The __str__ method serializes the event in a way that it can be
        interpreted by the JavaScript Client.
        
        >>> event = LivePageEvent(description="uwe goes online")
        >>> str(event)
        'uwe goes online'
    """
    
    implements(ILivePageEvent)
    
    recipients = "all"
    where = None
    
    def __init__(self, **kw) :
        self.__dict__.update(kw)
        
    def __str__(self) :
        return self.description

class ErrorEvent(LivePageEvent) :
    """ An idle event that is send if no event is available. 
    
        >>> str(ErrorEvent(description="maximum recursion depth exceeded"))
        'error maximum recursion depth exceeded' 
    
    """
    
    implements(IIdleEvent)
    
    verb = "error"
    
    def __str__(self) :
        return "%s %s" % (self.verb, self.description)


class IdleEvent(LivePageEvent) :
    """ An idle event that is send if no event is available. 
    
        >>> str(IdleEvent())
        'idle' 
    
    """
    
    implements(IIdleEvent)
    
    verb = "idle"
    
    def __init__(self) :
        pass

    def __str__(self) :
        return self.verb

directlyProvides(IdleEvent, IClientEventFactory)


class ReloadEvent(LivePageEvent) :
    """ A reload event that can be used to enforce a page reload 
    
        >>> str(ReloadEvent())
        'reload' 
    
    """
    
    implements(IReloadEvent)
    
    verb = "reload"
    
    def __str__(self) :
        return self.verb
        
directlyProvides(ReloadEvent, IClientEventFactory)

       
class CloseEvent(LivePageEvent) :
    """ A user has closed the browser window
    
        >>> str(CloseEvent(uuid='client_uuid'))
        'reload' 
    
    """
    
    implements(ICloseEvent)
    
    verb = "close"
    
    def __str__(self) :
        return "%s %s" % (self.verb, self.uuid)

directlyProvides(CloseEvent, IClientEventFactory)
        

class LoginEvent(LivePageEvent) :
    """ A login event that can be used to notify about new users. 
    
        >>> str(LoginEvent(who='member.uoe', where='location'))
        'login member.uoe location' 
    
    """    
    implements(ILoginEvent)
    
    verb = "login"
    
    def __str__(self) :
        return "%s %s %s" % (self.verb, self.who, self.where)

directlyProvides(LoginEvent, IClientEventFactory)
      
      
class LogoutEvent(LivePageEvent) :
    """ A logout event that can be used to notify about leaving users. 
    
        >>> str(LoginEvent(who='member.uoe', where='location'))
        'login member.uoe location' 
    
    """    
    implements(ILogoutEvent)

    verb = "logout"
    
    def __str__(self) :
        return "%s %s %s" % (self.verb, self.who, self.where)

directlyProvides(LogoutEvent, IClientEventFactory)

    
class ModifyElementEvent(LivePageEvent) :
    """ Describes a modification of a page element. The modification
        is described by a verb and an id. 
        
        The description line is simply a string
        with words seperated by spaces.
                
    
        >>> event = ModifyElementEvent(id="comments")
        >>> str(event)
        'noop comments'
        
    """    
    implements(IModifyElementEvent)
    
    verb = "noop"

    def __str__(self) :
        return "%s %s" % (self.verb, self.id)


class SetAttribute(ModifyElementEvent) :
    """ Set a property of a DOM element.
    
        >>> event = SetAttribute(id="img", key="src", value="./demo.png")
        >>> str(event)
        'set img src ./demo.png'
    
    """
    
    implements(ISetAttribute)

    verb = "set"

    def __str__(self) :
        return "%s %s %s %s" % (self.verb, self.id, self.key, self.value)

directlyProvides(SetAttribute, IClientEventFactory)
   
   
class HTMLUpdateEvent(ModifyElementEvent) :
    """ An update event that contains a html fragment in addition to the
        description line. 
    """
    
    extra = ""
    
    def __str__(self) :
        return "%s %s %s\n%s" % (self.verb, self.id, self.extra, self.html)
        
        
class Append(HTMLUpdateEvent) :
    """ Append a html fragment as a child node to an existing DOM element. 

        >>> event = Append(id='comments', html='<div id="comment1"></div>')
        >>> print str(event)
        append comments 
        <div id="comment1"></div>
        
    """
    implements(IAppend)
      
    verb = "append"
    
directlyProvides(Append, IClientEventFactory)
    
    
class Update(HTMLUpdateEvent) :
    """ Append a html fragment as a child node to an existing DOM element. 

        >>> event = Update(id='comments', html='<div id="comment1"></div>')
        >>> print str(event)
        update comments 
        <div id="comment1"></div>
        
    """
    
    implements(IUpdate)

    verb = "update"

directlyProvides(Update, IClientEventFactory)

    
def dict2event(args) :
    """ Converts a dict into an event.
    
    Uses named utilities to lookup the event.
    
    Throws a ComponentLookupError if the dict cannot be converted.
    
    """
    
    verb = args.get('verb', None)
    del args['verb']
    factory = zapi.getUtility(IClientEventFactory, name=verb)
    return factory(**args)    
