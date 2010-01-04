===============
The Boston Skin
===============

The Boston skin is a new UI for the Zope Management Interface called ZMI.
Feel free to write comments, ideas and wishes to the zope3-dev mailinglist.

    >>> from zope.testbrowser.testing import Browser
    >>> browser = Browser()
    >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
    >>> browser.handleErrors = False

Check if the css viewlet is available in the Boston skin.

    >>> browser.open('http://localhost/++skin++Boston/@@contents.html')
    >>> browser.url
    'http://localhost/++skin++Boston/@@contents.html'
    >>> browser.contents
    '...href="http://localhost/++skin++Boston/@@/skin.css"...'
    >>> browser.contents
    '...href="http://localhost/++skin++Boston/@@/widget.css"...'
    >>> browser.contents
    '...href="http://localhost/++skin++Boston/@@/toolbar.css"...'
    >>> browser.contents
    '...href="http://localhost/++skin++Boston/@@/xmltree.css"...'

Check if the javascript viewlet is available in the Boston skin.

    >>> browser.open('http://localhost/++skin++Boston/@@contents.html')
    >>> browser.url
    'http://localhost/++skin++Boston/@@contents.html'
    >>> browser.contents
    '...src="http://localhost/++skin++Boston/@@/boston.js"...'
    >>> browser.contents
    '...src="http://localhost/++skin++Boston/@@/xmltree.js"...'

Check if the left viewlet is available in the Boston skin.

    >>> browser.open('http://localhost/++skin++Boston/@@contents.html')
    >>> browser.url
    'http://localhost/++skin++Boston/@@contents.html'
    >>> browser.contents
    '...id="ToolBar"...'
    >>> browser.contents
    '...id="xmltree"...'
    >>> browser.contents
    '...id="addinginfo"...'

Make sure the edit form "works":

    >>> browser.open(
    ...     'http://localhost/++skin++Boston/+/zope.app.dtmlpage.DTMLPage=')
