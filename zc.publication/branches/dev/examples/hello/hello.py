
import zope.publisher.browser

class Hello(zope.publisher.browser.BrowserPage):

   def __init__(self, request):
       self.request = request

   def __call__(self):
       return """<html><body>
       Hello world
       </body></html>
       """
