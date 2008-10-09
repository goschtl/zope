import grok

import zope.component
from zope.exceptions import DuplicationError

class Demosite(grok.Application, grok.Container):
    pass

class Index(grok.View):
    pass

class Robots(grok.View):
    grok.name('robots.txt')
    
@grok.subscribe(Demosite, grok.IObjectAddedEvent)
def handle(obj, event):
    applications=(('gbeguestbook.app.Application','Guestbook'),
                  ('gbe99bottles.app.Song','Song'),
                  ('gbewiki.app.WikiPage','Wiki'),
                  ('gbepastebin.app.Application','Pastebin'),
                  )
    for application, name in applications:
        app = zope.component.getUtility(grok.interfaces.IApplication,
                                        name=application)
        try:
            obj[name] = app()
        except DuplicationError:
            pass
