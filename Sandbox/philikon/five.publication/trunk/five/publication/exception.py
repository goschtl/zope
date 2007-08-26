from zope.publisher.browser import BrowserPage

class SystemError(BrowserPage):

    def __call__(self):
        self.request.response.setStatus(500)
        self.request.response.setHeader('Content-Type', 'text/plain')
        return 'A system error occurred.'

class Redirect(BrowserPage):

    def __call__(self):
        self.request.response.redirect(self.context.args[0])
