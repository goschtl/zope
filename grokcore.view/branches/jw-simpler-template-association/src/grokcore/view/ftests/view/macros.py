"""
  >>> getRootFolder()["manfred"] = Mammoth()

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> browser.open("http://localhost/manfred/@@painting")
  >>> print browser.contents
  <html>
  <body>
  <h1>GROK MACRO!</h1>
  <div>
  GROK SLOT!
  </div>
  </body>
  </html>

Views without a template do not support macros:

  >>> browser.open("http://localhost/manfred/@@dancing")
  Traceback (most recent call last):
  AttributeError: 'DancingHall' object has no attribute 'template'

If the view has an attribute with the same name as a macro, the macro
shadows the view. XXX This should probably generate a warning at runtime.

  >>> browser.open("http://localhost/manfred/@@grilldish")
  >>> print browser.contents
  <html>
  Curry
  </html>

You can skip the "macro" part of the macro call, but this is deprecated:

  >>> from grokcore.view.testing import warn
  >>> import warnings
  >>> saved_warn = warnings.warn
  >>> warnings.warn = warn

  >>> browser.open("http://localhost/manfred/@@burnt")
  From grok.testing's warn():
  ... DeprecationWarning: Calling macros directly on the view is deprecated. Please use context/@@viewname/macros/macroname
  ...

  >>> warnings.warn = saved_warn

"""
import grokcore.view as grok

class Mammoth(grok.Context):
    pass

class DancingHall(grok.View):

    def render(self):
        return "A nice large dancing hall for mammoths."

class Grilled(grok.View):

    def update(self):
        self.spices = "Pepper and salt"

class Painting(grok.View):
    grok.template('painting')

class Layout(grok.View):
    grok.template('layout')

class Dancing(grok.View):
    grok.template('dancing')

class GrillDish(grok.View):
    grok.template('grilldish')

class Burnt(grok.View):
    grok.template('burnt')

class Grilled(grok.View):
    grok.template('grilled')

