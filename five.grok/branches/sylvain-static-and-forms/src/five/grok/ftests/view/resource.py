"""

  >>> from five.grok.ftests.view.argument import *

  >>> from Products.Five.testbrowser import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

  We can access to our CSS file:

  >>> browser.open("http://localhost/++resource++five.grok.ftests.view/style.css")
  >>> print browser.contents
  body {
     color: green;
  }
  >>> print browser.headers['content-type']
  text/css; charset=iso-8859-15

  And the template file:

  >>> browser.open("http://localhost/++resource++five.grok.ftests.view/template.pt")
  >>> print browser.contents
  <tal:test>This template should be considered as a file.</tal:test>
  >>> print browser.headers['content-type']
  text/html; charset=iso-8859-15

  
"""
