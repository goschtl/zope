from zope.publisher.interfaces import INotFound
from zope.interface.common.interfaces import IException
from zope.exceptions.interfaces import IUserError

import grok

class NotFound(grok.View):
      grok.context(INotFound)
      grok.name('index.html')
      
class SystemError(grok.View):
      grok.context(IException)
      grok.name('index.html')
            
class UserError(grok.View):
      grok.context(IUserError)
      grok.name('index.html')
      
