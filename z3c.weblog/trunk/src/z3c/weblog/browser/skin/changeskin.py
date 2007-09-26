from z3c.weblog.interfaces import IWeblog

def objectSkin(event):
    if IWeblog.providedBy(event.object) and event.request.principal.id == 'zope.anybody':
        event.request.setPresentationSkin('weblog')
