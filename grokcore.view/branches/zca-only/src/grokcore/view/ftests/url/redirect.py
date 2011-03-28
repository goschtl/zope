"""
Views have a redirect() method to easily create redirects:

  >>> root = getRootFolder()
  >>> root['manfred'] = manfred = Mammoth()

Since the index view redirects to mammoth, we expect to see the URL
point to mammoth:

  >>> from infrae.testbrowser.browser import Browser
  >>> application = getApplication()
  >>> browser = Browser(application)
  >>> browser.options.handle_errors = False

  >>> browser.open('http://localhost/manfred')
  >>> browser.url
  '/manfred'

  >>> status = browser.open('http://localhost/manfred/trustedredirect')
  >>> browser.status_code
  302
  >>> browser.location
  'http://www.google.com/ncr'

  >>> browser.open('http://localhost/manfred/redirectwithstatus')
  Traceback (most recent call last):
  ...
  HTTPError: HTTP Error 418: Unknown
  >>> browser.url
  '/manfred/redirectwithstatus'

"""
import grokcore.view as grok


class Mammoth(grok.Context):
    pass


class Index(grok.View):
    def render(self):
        self.redirect(self.url('another'))


class TrustedRedirect(grok.View):

    def update(self):
        super(TrustedRedirect, self).update()
        self.redirect('http://www.google.com/ncr', trusted=True)

    def render(self):
        return self.response


class RedirectWithStatus(grok.View):
    def render(self):
        self.redirect(self.url(), status=418)


class Another(grok.View):
    def render(self):
        return "Another view"
