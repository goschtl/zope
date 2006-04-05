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

import simplejson

from zope.app import zapi
from zorg.live.globals import getRequest
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
from zorg.live.page.interfaces import IProgressEvent

from zorg.live.page.interfaces import IClientEventFactory


class JSONEventEncoder(simplejson.encoder.JSONEncoder) :
    """ Specialization of JSONEncoder that makes LivePageEvents serializable.
    """
    
    def default(self, o) :
        """ Overwritten default method that allows to serialize
            LivePageEvents.
        """
        
        if ILivePageEvent.providedBy(o) :
            return o.toDict()
        return super(JSONEventEncoder, self).default(o)
                
        

class LivePageEvent(object) :
    """ 
    LivePage events are broadcasted from server side LivePage clients
    to their browser counterparts via JSON.
        
    Event objects cannot be converted to JSON as such :
    
    >>> event = LivePageEvent()
    >>> simplejson.dumps(event)
    Traceback (most recent call last):
    ...
    TypeError: <...LivePageEvent object at ...> is not JSON serializable
     
    Therefore we convert each LivePageEvent into a serializable dict.

    >>> d = event.toDict()
    >>> sorted(d.items())
    [('name', 'event'), ('recipients', 'all'), ('where', None)]
    
    This dict is used by the JSONEventEncoder to decode the event object. The
    toJSON method calls these encoder :
    
    >>> event = LivePageEvent(description="uwe goes online")
    >>> event.toJSON()
    '{..."where":null...}'
    
    In order to convert JSON serialized event back into Python objects we
    use the dict2event function. This function uses the 'name' key 
    to look up a IClientEventFactory. This factory provides an object constructor
    that takes a python dict as its keyword arguments. This factory
    must be registered as a named utility:
    
    >>> from zope.component import provideUtility
    >>> provideUtility(LivePageEvent, IClientEventFactory, name="event")
    >>> decoded = dict2event(event.toDict())
    >>> decoded
    <zorg.live.page.event.LivePageEvent object at ...>
    
    Encoded and decoded objects are equivalent:
    
    >>> event.toDict() == decoded.toDict()
    True
        
       
        
  
  
    """
    
    implements(ILivePageEvent)
    
    recipients = "all"
    where = None
    name = "event"
    
    def __init__(self, **kw) :
        self.__dict__.update(kw)
        
    def toDict(self) :
        d = dict(self.__dict__)
        d.update(dict(name=self.name,
                        recipients=self.recipients,
                        where=self.where))
        return d
        
    def toJSON(self) :
        return simplejson.dumps(self, cls=JSONEventEncoder)
        
    def pprint(self) :
        for key, value in sorted(self.toDict().items()) :
            print key, ":", repr(value)

directlyProvides(LivePageEvent, IClientEventFactory)

class ErrorEvent(LivePageEvent) :
    """ An idle event that is send if no event is available. 
    
        >>> ErrorEvent(description="maximum recursion depth exceeded").pprint()
        description : 'maximum recursion depth exceeded'
        name : 'error'
        recipients : 'all'
        where : None
    
    """
    
    implements(IIdleEvent)
    
    name = "error"
    
    
class IdleEvent(LivePageEvent) :
    """ An idle event that is send if no event is available. 
    
        >>> IdleEvent().pprint()
        name : 'idle'
        recipients : 'all'
        where : None
    
    """
    
    implements(IIdleEvent)
    
    name = "idle"
   

directlyProvides(IdleEvent, IClientEventFactory)


class ReloadEvent(LivePageEvent) :
    """ A reload event that can be used to enforce a page reload 
    
        >>> ReloadEvent().pprint()
        name : 'reload'
        recipients : 'all'
        where : None
    
    """
    
    implements(IReloadEvent)
    
    name = "reload"
    
        
directlyProvides(ReloadEvent, IClientEventFactory)


class ProgressEvent(LivePageEvent) :
    """ Indicates the progress of a long enduring task.

        >>> event = Progress(percent=20)
        >>> event.pprint()
        html : '<div id="comment1"></div>'
        id : 'comments'
        name : 'update'
        recipients : 'all'
        where : None
    
    """
    
    implements(IProgressEvent)
    
    name = "progress"

directlyProvides(ProgressEvent, IClientEventFactory)

       
class CloseEvent(LivePageEvent) :
    """ A user has closed the browser window
    
        >>> CloseEvent(uuid='client_uuid').pprint()
        name : 'close'
        recipients : 'all'
        uuid : 'client_uuid'
        where : None
    
    """
    
    implements(ICloseEvent)
    
    name = "close"
    

directlyProvides(CloseEvent, IClientEventFactory)
        

class LoginEvent(LivePageEvent) :
    """ A login event that can be used to notify about new users. 
    
        >>> LoginEvent(who='member.uoe', where='location').pprint()
        name : 'login'
        recipients : 'all'
        where : 'location'
        who : 'member.uoe'
    
    """    
    implements(ILoginEvent)
    
    name = "login"
    

directlyProvides(LoginEvent, IClientEventFactory)
      
      
class LogoutEvent(LivePageEvent) :
    """ A logout event that can be used to notify about leaving users. 
    
        >>> LogoutEvent(who='member.uoe', where='location').pprint()
        name : 'logout'
        recipients : 'all'
        where : 'location'
        who : 'member.uoe'
    
    """    
    implements(ILogoutEvent)

    name = "logout"
    

directlyProvides(LogoutEvent, IClientEventFactory)

    
class ModifyElementEvent(LivePageEvent) :
    """ Describes a modification of a page element. The modification
        is described by a name and an id. 
        
        The description line is simply a string
        with words seperated by spaces.
                
        >>> event = ModifyElementEvent(id="comments")
        >>> event.pprint()
        id : 'comments'
        name : 'modify'
        recipients : 'all'
        where : None
        
    """    
    implements(IModifyElementEvent)
    
    name = "modify"



class SetAttribute(ModifyElementEvent) :
    """ Set a property of a DOM element.
    
        >>> event = SetAttribute(id="img", key="src", value="./demo.png")
        >>> event.pprint()
        id : 'img'
        key : 'src'
        name : 'set'
        recipients : 'all'
        value : './demo.png'
        where : None
    
    """
    
    implements(ISetAttribute)

    name = "set"


directlyProvides(SetAttribute, IClientEventFactory)
   
   
class HTMLUpdateEvent(ModifyElementEvent) :
    """ An update event that contains a html fragment in addition to the
        description line. 
    """
    
    extra = ""
            
        
class Append(HTMLUpdateEvent) :
    """ Append a html fragment as a child node to an existing DOM element. 

        >>> event = Append(id='comments', html='<div id="comment1"></div>')
        >>> event.pprint()
        html : '<div id="comment1"></div>'
        id : 'comments'
        name : 'append'
        recipients : 'all'
        where : None
        
    """
    implements(IAppend)
      
    name = "append"
    
directlyProvides(Append, IClientEventFactory)
    
    
class Update(HTMLUpdateEvent) :
    """ Append a html fragment as a child node to an existing DOM element. 

        >>> event = Update(id='comments', html='<div id="comment1"></div>')
        >>> event.pprint()
        html : '<div id="comment1"></div>'
        id : 'comments'
        name : 'update'
        recipients : 'all'
        where : None
        
    """
    
    implements(IUpdate)

    name = "update"

directlyProvides(Update, IClientEventFactory)

    

def dict2event(args) :
    """ Converts a dict into an event.
    
    Uses named utilities to lookup the event.
    
    Throws a ComponentLookupError if the dict cannot be converted.
    
    """
    
    name = args.get('name', None)
    del args['name']
    factory = zapi.getUtility(IClientEventFactory, name=name)
    return factory(**args)    

def request2event() :
    """ Converts the form data of the current request to an event.
    
    """
    request = getRequest()
    args = {}
    for k, v in request.form.items() :
        args[str(k)] = v.encode("utf-8")
    return dict2event(args)
  
