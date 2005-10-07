Wikification
============

We want to be able to convert existing HTML documents into a collaborative Wiki.
As a minimal assumption we consider only file and folder content types.

Let's take some example pages :

>>> from tests import buildSampleSite
>>> site = buildSampleSite()

The site has the following structure
    
        root
            index.html          (with example1 as content)
            target              (an existing file)
            folder              (a sample folder)


    >>> sorted(site.keys())
    [u'folder', u'index.html', u'target']

The index.html is our starting point and contains the following HTML :

    >>> index_page = site[u"index.html"]
    >>> print index_page.data
    <html>
        <body>
            <p>Wikifiable</p>
            <p>An <a href="target">existing link</a></p>
            <p>A <a href="newitem">new page</a></p>
            <p>A <a href="folder1/newitem">new page in a subfolder</a></p>
            <p>A [New Subject]</a></p>
        </body>
    </html>


The links within the document may point to 
    1. external resources
    2. existing local documents, and
    3. non existing sub items of the site, which should be marked
       as wiki links

In many Wikis links to non existant pages are marked by question marks. 
If we assume that the first link in index.html works and the second is a dead
one, the resulting HTML could look as follows :


    >>> from wikification.browser.wikipage import WikiPage
    >>> page = WikiPage(index_page.__parent__, TestRequest("/index.html"))
    >>> print page.render(index_page.data)
    <html>
        <body>
            <p>Wikifiable</p>
            <p>An <a class="create-link" href="target">existing link</a></p>
            <p>A <a class="create-link" href="http://127.0.0.1/createLink?path=newitem">new page</a></p>
            <p>A <a class="create-link" href="http://127.0.0.1/createLink?path=folder1/newitem">new page in a subfolder</a></p>
            <p>A [New Subject]</a></p>
        </body>
    </html>
    
    The task of creating a new page is delegated to the createLink method of the 
    wiki page. We considered the possibility to adapt the traversal mechanism
    in order to throw add forms in case of TraversalErrors, but a simple
    page method seems to be the simplest solution:
    
    >>> request = TestRequest("/index.html", form={'path':'folder1/newitem', })
    >>> WikiPage(index_page.__parent__, request).createLink()
    >>> index_page.__parent__[u'folder1'][u'newitem']
    <zope.app.file.file.File object at ...>

Comments
--------

To Dos
------

RSS Support




Problems
--------

Resolving different link types:

/sdfsdf?jkkl        # strip query string and start traversal from wiki root

asdf/sdfa           # traverse relative to container

asdf                # traverse relative to container

http://asdfsd       # leave untouched

Hierarchical substructures are not Wiki-like?

How to handle moved items?

A mapping from old to new places is used to ensure that links point to
the current location of an object. This change can be done at move time or at
render time. Is this change done in response to events or triggered by 
dedicated user actions?

How to represent multiple parents?

A filesystem like solution using aliases requires additional tools for
the look up of multiple parents.


Using new traversal mechanism for various query types (e.g. search for author 
/about/joe, date 2005/12/24, keywords /news/sports/, see http://del.icio.us/)
or query extension (e.g. search?author=joe, date=2005/12/24)

  
Initial user guidance?

Examples for creating a page

Examples for other automatic features, e.g. pasting URLs or adaption to moved
content