z3c.boston.Boston
=================

This skin is a derivative of the zope.app.boston.Boston skin, which
supports pagelets, forms and javascript forms.

It includes the information needed to configure itself. To add it
to your configuration;

    1.  Add it to your buildout...

        eggs=...
            z3c.boston

    2.  To use the skin, you can use a path adapter:

        http://localhost:8080/++skin++z3c_boston/index.html

    3.  To configure this as your default skin, add this line to your
        site.zcml file:

        <includeOverrides package="z3c.boston" file="default_skin.zcml" />

----------------------------------------------------------------------------

    >>> from zope.testbrowser.testing import Browser
    >>> browser = Browser()
    >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
    >>> browser.handleErrors = False

Check if the css viewlet is available in the z3c_boston skin.

    >>> browser.open('http://localhost/++skin++z3c_boston/@@contents.html')
    >>> browser.url
    'http://localhost/++skin++z3c_boston/@@contents.html'
    >>> browser.contents
    '...href="http://localhost/++skin++z3c_boston/@@/skin.css"...'
    >>> browser.contents
    '...href="http://localhost/++skin++z3c_boston/@@/widget.css"...'
    >>> browser.contents
    '...href="http://localhost/++skin++z3c_boston/@@/toolbar.css"...'
    >>> browser.contents
    '...href="http://localhost/++skin++z3c_boston/@@/xmltree.css"...'

Check if the javascript viewlet is available in the Boston skin.

    >>> browser.open('http://localhost/++skin++z3c_boston/@@contents.html')
    >>> browser.url
    'http://localhost/++skin++z3c_boston/@@contents.html'
    >>> browser.contents
    '...src="http://localhost/++skin++z3c_boston/@@/boston.js"...'
    >>> browser.contents
    '...src="http://localhost/++skin++z3c_boston/@@/xmltree.js"...'

Check if the left viewlet is available in the Boston skin.

    >>> browser.open('http://localhost/++skin++z3c_boston/@@contents.html')
    >>> browser.url
    'http://localhost/++skin++z3c_boston/@@contents.html'
    >>> browser.contents
    '...id="ToolBar"...'
    >>> browser.contents
    '...id="xmltree"...'
    >>> browser.contents
    '...id="addinginfo"...'

Make sure the edit form "works":

    >>> browser.open(
    ...     'http://localhost/++skin++z3c_boston/+/zope.app.dtmlpage.DTMLPage=')

A demo pagelet is defined in demo.py. Load the pagelet.

    >>> browser.open('http://localhost/++skin++z3c_boston/@@demo.html')
    >>> browser.contents
    '...PAGELET CONTENT...'

Verify standard viewlets 

    >>> browser.open('http://localhost/++skin++z3c_boston/@@demo.html')
    >>> browser.contents
    '...demo.css...'
    >>> browser.contents
    '...demo.js...'

Verify that the CSS for forms is included

    >>> browser.open('http://localhost/++skin++z3c_boston/@@demo_form.html')
    >>> browser.contents
    '...div-form.css...'

Verify that formjs works

    >>> browser.open('http://localhost/++skin++z3c_boston/@@demo_formjs.html')
    >>> browser.contents
    '...div-form.css...'
    >>> browser.contents
    '...jquery.js...'
    >>> browser.contents
    '...alert...'
