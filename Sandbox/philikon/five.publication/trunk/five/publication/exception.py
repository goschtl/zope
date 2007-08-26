from zope.publisher.browser import BrowserPage

class SystemError(BrowserPage):

    def __call__(self):
        self.request.response.setStatus(500)
        self.request.response.setHeader('Content-Type', 'text/plain')
        return 'A system error occurred.'

class Redirect(BrowserPage):

    def __call__(self):
        self.request.response.redirect(self.context.args[0])

class NotFound(BrowserPage):

    def __call__(self):
        self.request.response.setStatus(404)
        self.request.response.setHeader('Content-Type', 'text/plain')
        return 'Not found'

class Unauthorized(BrowserPage):

    def __call__(self):
        self.request.response.setStatus(401)
        self.request.response.setHeader('Content-Type', 'text/plain')
        return 'Unauthorized'
