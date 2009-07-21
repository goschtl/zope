"""
  >>> from five.grok.ftests.view.codeview import *
  >>> id = getRootFolder()._setObject("manfred", CodeMammoth(id='manfred'))

  >>> from Products.Five.testbrowser import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> browser.open("http://localhost/manfred/@@codepainting")
  >>> print browser.contents
  Mona Lisa

"""
from five import grok

class CodeMammoth(grok.Model):

    def __init__(self, id):
        super(CodeMammoth, self).__init__(id=id)
        self.id = id

class CodePainting(grok.CodeView):
    
    def render(self):
        return "Mona Lisa"
