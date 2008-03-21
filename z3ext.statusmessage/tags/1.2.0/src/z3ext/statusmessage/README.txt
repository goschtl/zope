=====================
Portal status message
=====================

Instead include notification messages directly to template,
 developer can use messaging service.

Main interface is IStatusMessage, it is adapter for IBrowserRequest
so we can have different implementations, for example cookie based or session.

By default only session based service implemented.

   >>> from zope import interface, component
   >>> from zope.interface.verify import verifyClass

   >>> from z3ext.statusmessage import tests
   >>> from z3ext.statusmessage import interfaces, session, message, browser

   >>> verifyClass(interfaces.IStatusMessage, session.SessionMessageService)
   True

   >>> component.provideAdapter(session.getSessionMessageService)

   >>> from zope.publisher.browser import TestRequest
   >>> request = TestRequest()

   >>> service = interfaces.IStatusMessage(request)

   >>> service.hasMessages()
   False

   >>> service.add('Test message')
   Traceback (most recent call last):
   ...
   ComponentLookupError: ...

   >>> service.clear()
   ()


Before we can use message service we need register message type.

   >>> verifyClass(interfaces.IMessage, message.InformationMessage)
   True

   >>> component.provideUtility(message.InformationMessage, 
   ...   interfaces.IMessageFactory, 'info')

Now we can add messages.

   >>> service.add('Test message')

   >>> service.hasMessages()
   True

   >>> service.list()
   [<z3ext.statusmessage.message.InformationMessage ...>]


Let's register another message type.

   >>> verifyClass(interfaces.IMessage, message.WarningMessage)
   True

   >>> component.provideUtility(message.WarningMessage, 
   ...   interfaces.IMessageFactory, 'warning')

   >>> service.add('Warning message', 'warning')

   >>> service.list()
   [<...InformationMessage ...>, <...WarningMessage ...>]

Also we can add message directly

   >>> verifyClass(interfaces.IMessage, message.ErrorMessage)
   True

Error message, we can add exception object

   >>> service.addMessage(message.ErrorMessage(Exception('Error message')))

or text message

   >>> service.addMessage(message.ErrorMessage('Error message'))

   >>> service.list()
   [<...InformationMessage ...>, <...WarningMessage ...>, <...ErrorMessage ...>, <...ErrorMessage ...>]


Message renderes
----------------

We should provider IMesasgeView adater for each message type.

   >>> msg = service.list()[0]
   >>> renderer = component.getMultiAdapter((msg, request), interfaces.IMessageView)
   >>> renderer.render()
   '<div class="statusMessage">Test message</div>'

Same for other mesages

   >>> msg = service.list()[1]
   >>> renderer = component.getMultiAdapter((msg, request), interfaces.IMessageView)
   >>> renderer.render()
   '<div class="statusWarningMessage">Warning message</div>'

   >>> msg = service.list()[2]
   >>> renderer = component.getMultiAdapter((msg, request), interfaces.IMessageView)
   >>> renderer.render()
   '<div class="statusStopMessage">Exception: Error message</div>'

To render all messages, we can use 'statusMessage' content provider.
Also 'statusMessage' provider clears service

   >>> from zope.contentprovider.interfaces import IContentProvider
   >>> renderer = component.getMultiAdapter(
   ...     (None, request, None), IContentProvider, 'statusMessage')
   >>> renderer.update()
   >>> print renderer.render()
   <div class="statusMessage">Test message</div>
   <div class="statusWarningMessage">Warning message</div>
   <div class="statusStopMessage">Exception: Error message</div>
   <div class="statusStopMessage">Error message</div>

   >>> service.hasMessages()
   False

It is possible to add new messages to service with 'statusMessages' provider

   >>> renderer.add('Test message')
   >>> service.list()
   [<...InformationMessage ...>]

With different type:

   >>> renderer.add('Warning message', 'warning')
   >>> service.list()
   [<...InformationMessage ...>, <...WarningMessage ...>]

   >>> renderer.addIf('')
   >>> len(service.list())
   2

   >>> renderer.addIf('test')
   >>> len(service.list())
   3

   >>> t = service.clear()


Clearing service
----------------

clear() method return all messages and clear service.

   >>> service.addMessage(message.ErrorMessage('Error message'))

   >>> service.clear()
   [<...ErrorMessage ...>]

   >>> service.hasMessages()
   False
