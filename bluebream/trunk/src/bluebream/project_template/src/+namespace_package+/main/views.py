from zope.publisher.browser import BrowserView

class RootDefaultView(BrowserView):

    def __call__(self):
        return """\
<html><head><title>Welcome to BlueBream!</title></head><body>
<h1>Welcome to BlueBream!</h1>
<ul>
<li><a href="http://pypi.python.org/pypi/bluebream">PyPI page</a></li>
<li><a href="http://packages.python.org/bluebream">Documentation</a></li>
<li><a href="https://mail.zope.org/mailman/listinfo/zope3-users">Mailing list</a></li>
<li><a href="http://webchat.freenode.net/?randomnick=1&channels=bluebream">IRC Channel: #bluebream at irc.freenode.net</a></li>
</ul>
</body></html>
"""
