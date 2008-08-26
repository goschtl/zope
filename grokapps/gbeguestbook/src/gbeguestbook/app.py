from datetime import datetime
import uuid
from zope.interface import Interface
from zope import schema
from zope.app.security.interfaces import IUnauthenticatedPrincipal
import grok

class Application(grok.Application, grok.Container):
    pass

class IGreeting(Interface):
    author = schema.Field(title=u'Author')
    content = schema.Text(title=u'Content')
    date = schema.Datetime(title=u'Date')

class Greeting(grok.Model):
    grok.implements(IGreeting)

class MainPage(grok.View):
    grok.context(Application)
    grok.name('index')

    def render(self):
        out=['<html><body>']    
        out.append('<h1>Grok-by-Example: Guestbook</h1>')
        greetings=[(x.date, x) for x in self.context.values()]
        greetings=list(reversed(sorted(greetings)))
        for date,greeting in greetings[:10]:
            if IUnauthenticatedPrincipal.providedBy(greeting.author):
                out.append('An anonymous person wrote:')
            else:
                out.append('<b>%s</b> wrote:' % greeting.author.getLogin())
            out.append('<blockquote>%s</blockquote>' %
                                  greeting.content)
        out.append("""
              <form action="%s/sign" method="post">
                <div><textarea name="content" rows="3" cols="60"></textarea></div>
                <div><input type="submit" value="Sign Guestbook"></div>
              </form>
            </body>
          </html>""" % self.application_url())
        return ''.join(out)

class Guestbook(grok.View):
    grok.context(Application)
    grok.name('sign')

    def render(self):
        if self.request.method.upper() != 'POST':
            return self.redirect(self.application_url())
        greeting = Greeting()
        greeting.author = self.request.principal
        greeting.content = self.request.get('content')
        greeting.date = datetime.now()
        id=str(uuid.uuid4())
        self.context[id]=greeting
        self.redirect(self.application_url())
