Wikification
============

We want to be able to convert existing HTML documents into a collaborative Wiki.

Let's take some example pages.

>>> from tests import buildSampleSite
>>> from tests import renderWikiPage
>>> from zope.app import zapi
>>> site = buildSampleSite()
>>> sorted(site.keys())
[u'folder1', u'folder2', u'index.html']
>>> index_page = site[u"index.html"]
>>> print index_page.data
<html>
<body>
<p>Wikifiable</p>
<p>An <a href="folder1/target">existing link</a></p>
<p>A <a href="folder1/newitem">new page</a></p>
<p>A <a href="folder1/subfolder/newitem">new page in a subfolder</a></p>
<p>A [New Subject]</a></p>
</body>
</html>


If a given HTML document links may point to external places or existing local
documents as well as not yet existing local objects, which are marked in Wikis
by questions marks. If we assume that the first link above has an existing
counterpart in the object hierarchy and the second link not, the resulting
HTML should look as follows :

>>> zapi.traverse(site, [u'folder1', u'target'])
<zope.app.file.file.File object at 0x12c4630>
>>> zapi.traverse(site, [u'folder1', u'newitem'])

>>> print renderWikiPage(index_page)
<html>
<body>
<p>Wikifiable</p>
<p>An <a href="folder1/target">existing link</a></p>
<p>A <a class="create-link" href="folder1/createLink?path=newitem">new page</a></p>
<p>A <a class="create-link" href="folder1/createLink?path=NewSubject1">[New Subject]</a></p>
<p>A <a class="create-link" href="folder1/createLink?path=subfolder/newitem">new page in a subfolder</a></p>
</body>
</html>




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