from zope.publisher.browser import BrowserView
from zope.container.interfaces import INameChooser
from zope.formlib import form

from interfaces import ISampleApplication
from app import SampleApplication

class AddSampleApplication(form.AddForm):

    form_fields = form.Fields(ISampleApplication)

    def createAndAdd(self, data):
        name = data['name']
        description = data.get('description')
        namechooser = INameChooser(self.context)
        app = SampleApplication()
        name = namechooser.chooseName(name, app)
        self.context[name] = app
        self.request.response.redirect(name)


class SampleApplicationDefaultView(BrowserView):

    def __call__(self):
        return """Welcome to the Sample application"""


class RootDefaultView(BrowserView):

    def __call__(self):
        return """\
<html><head><title>Welcome to BlueBream!</title></head><body>
<h1>Welcome to BlueBream!</h1>
<ul>
<li><a href="http://pypi.python.org/pypi/bluebream">PyPI page</a></li>
<li><a href="http://packages.python.org/bluebream">Documentation</a></li>
<li><a href="https://launchpad.net/bluebream">Issue Tracker</a></li>
<li><a href="http://wiki.zope.org/bluebream">Wiki</a></li>
<li><a href="http://twitter.com/bluebream">Twitter</a></li>
<li><a href="https://mail.zope.org/mailman/listinfo/zope3-users">Mailing list</a></li>
<li><a href="http://webchat.freenode.net/?randomnick=1&channels=bluebream">IRC Channel: #bluebream at irc.freenode.net</a></li>
</ul>
<a href="@@login.html">Login</a>
<br/>
<a href="@@add">Add Sample application</a>
</body></html>
"""
