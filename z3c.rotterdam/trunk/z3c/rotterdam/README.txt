z3c.rotterdam.Rotterdam
========================

This skin is a derivative of the zope.app.rotterdam.Rotterdam skin, which
supports pagelets, forms and javascript forms.

It includes the information needed to configure itself. To add it
to your configuration;

    1.  Add it to your buildout...

        eggs=...
            z3c.rotterdam

    2.  To use the skin, you can use a traversal adapter:

        http://localhost:8080/++skin++z3c_rotterdam/index.html

    3.  To configure this as your default skin, add this line to your
        site.zcml file:

        <includeOverrides package="z3c.rotterdam" file="default_skin.zcml" />

----------------------------------------------------------------------------

    >>> from zope.testbrowser.testing import Browser
    >>> browser = Browser()
    >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
    >>> browser.handleErrors = False

Verify that a standard view works with the z3c.rotterdam skin

    >>> browser.open('http://localhost/++skin++z3c_rotterdam/@@contents.html')
    >>> browser.url
    'http://localhost/++skin++z3c_rotterdam/@@contents.html'

Make sure the edit form "works":

    >>> browser.open(
    ...     'http://localhost/++skin++z3c_rotterdam/+/zope.app.dtmlpage.DTMLPage=')

A demo pagelet is defined in demo.py. Load the pagelet.

    >>> browser.open('http://localhost/++skin++z3c_rotterdam/@@demo.html')
    >>> browser.contents
    '...PAGELET CONTENT...'

Verify standard viewlets 

    >>> browser.open('http://localhost/++skin++z3c_rotterdam/@@demo.html')
    >>> browser.contents
    '...demo.css...'
    >>> browser.contents
    '...demo.js...'

Verify that the CSS for forms is included

    >>> browser.open('http://localhost/++skin++z3c_rotterdam/@@demo_form.html')
    >>> browser.contents
    '...div-form.css...'

Verify that formjs works

    >>> browser.open('http://localhost/++skin++z3c_rotterdam/@@demo_formjs.html')
    >>> browser.contents
    '...div-form.css...'
    >>> browser.contents
    '...jquery.js...'
    >>> browser.contents
    '...alert...'
