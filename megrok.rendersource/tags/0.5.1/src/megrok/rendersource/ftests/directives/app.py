"""
Do a functional doctest test on the app.
========================================

:Test-Layer: functional

Let's first create an instance of Testme at the top level:

   >>> root = getRootFolder()
   >>> root['app'] = Application()


Run tests in the testbrowser
----------------------------

The zope.testbrowser.browser module exposes a Browser class that
simulates a web browser similar to Mozilla Firefox or IE.  We use that
to test how our application behaves in a browser.  For more
information, see http://pypi.python.org/pypi/zope.testbrowser.

Create a browser and visit the instance you just created:

   >>> from zope.testbrowser.testing import Browser
   >>> browser = Browser()
   >>> browser.handleErrors  = False
   >>> browser.open('http://localhost/app')

Check include/raw/csv-table directives:

   >>> browser.open('http://localhost/app/base')
   <?xml version="1.0" encoding="utf-8" ?>
   <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
   <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
   <head>
   <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
   <meta name="generator" content="Docutils 0.6: http://docutils.sourceforge.net/" />
   <title></title>
   <link rel="stylesheet" href="http://localhost/&#64;&#64;/megrok.rendersource.ftests.directives/grok.css" type="text/css" />
   </head>
   <body>
   <div class="document">
   <p>start base-template</p>
   <p>include file:</p>
   <p>--included text--</p>
   <p>raw-file:</p>
   --included text--<p>csv-table:</p>
   <table border="1" class="docutils">
   <colgroup>
   <col width="100%" />
   </colgroup>
   <tbody valign="top">
   <tr><td>--included text--</td>
   </tr>
   </tbody>
   </table>
   <p>end base-template</p>
   </div>
   </body>
   </html>

Check some basic information about the page you visit:

   >>> browser.url
   'http://localhost/app/base'
   >>> browser.headers.get('Status').upper()
   '200 OK'

"""

import grokcore.component
import grokcore.view
import megrok.rendersource


class Application(grokcore.component.Context):
    pass


class Index(grokcore.view.View):
    grokcore.component.name('index.html')


class Base(grokcore.view.View):
    
    def namespace(self):
        # compute the stylesheet path to the file inside the 'static' folder, 
        # eg. 'grok.css'
        stylesheet=self.static['grok.css']()
        # enable absolut URL handling, disable embedding 
        return {'settings_overrides': {'stylesheet': stylesheet,
                                       'stylesheet_path': None,
                                       'embed_stylesheet': 0,
                                       'input_encoding': 'utf-8',
                                       'output_encoding': 'utf-8',
                                       }}
