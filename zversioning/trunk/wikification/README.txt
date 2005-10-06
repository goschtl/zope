Wikification
============

We want to be able to convert existing HTML documents into a collaborative Wiki.

Let's take some example pages.

>>> from tests import buildSampleSite
>>> site = buildSampleSite()
>>> sorted(site.keys())
[u'folder1', u'folder2', u'index.html']
>>> print site[u"index.html"].data
<html><body><p>Wikifiable</p>
<p>An <a href="folder1/target">existing link</a></p>
<p>A <a href="folder1/newitem">new page</a></p>
</body></html>
