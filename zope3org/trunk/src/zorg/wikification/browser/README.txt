Our Wiki is mainly a matter of representation. Therefore the main implementation
is found in this package.

Let's take our example site ...

    >>> from zorg.wikification.tests import buildSampleSite
    >>> site = buildSampleSite()

We have special WikiPage implementations for files and folders. Let's take
the index.html document of the site as an example for a WikiFilePage :

    >>> from wikipage import WikiFilePage
    >>> context = site[u"index.html"]
    >>> request = TestRequest()
    >>> index_page = WikiFilePage(context, request)

The page renders the content of the index.html document in a "wikified" version.
We use the renderBody method to include this "wikified" content into our
navigational structure, which is set aside for the moment :


    >>> print index_page.renderBody()
    <BLANKLINE>
        <p>Wikifiable</p>
        <p>An <a href=".../target/@@wiki.html">existing link</a></p>
        <p>A <a ... href=".../@@kupuadd.html?path=newitem">new page</a></p>
        <p>A <a ... href=".../@@kupuadd.html?path=folder1%2Fnewitem">...
        <p><a href=".../@@kupuadd.html?path=NewSubject">[New Subject]</a></p>
        <p>An <a href="http://www.google.org">external absolute link</a></p>
        <p>An <a href=".../target/@@wiki.html">internal absolute link</a></p>
    <BLANKLINE>

It uses the Dublin Core title (or "Untitled" if the title is not set).

    >>> from zope.app.dublincore.interfaces import IZopeDublinCore
    >>> index_page.title == IZopeDublinCore(context).title
    True

A user that wents up in the containment hierarchy should not get lost. We use
the container's index.html as the container content view as it is common :

    >>> from wikipage import WikiContainerPage
    >>> folder_page = WikiContainerPage(site, request)
    >>> folder_page.renderBody() == index_page.renderBody()
    True

More interesting is the question how one can add new content to an existing
place. Let's consider an empty folder as quite usual starting point :

    >>> empty_folder = site[u"folder"]
    >>> len(empty_folder)
    0
    >>> print WikiContainerPage(empty_folder, request).renderBody()
    <BLANKLINE>
      <p>No index.html found.<p>
      <p>Create a
          <a ... href=".../@@kupuadd.html?path=index.html">new index page</a>?
      </p>
    <BLANKLINE>
    
We can follow this link and are directed to a Kupu-Editor that allows us to
create a new index.html document.





