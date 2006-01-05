Our Wiki is mainly a matter of representation. Therefore the main implementation
is found in this package.

Let's take our example site ...

    >>> from zorg.wikification.tests import buildSampleSite
    >>> site = buildSampleSite()

We have special WikiPage implementations for files and folders. Let's take
the index.html document of the site as an example for a WikiFilePage :

    >>> from zorg.wikification.browser.wikipage import WikiFilePage
    >>> context = site[u"index.html"]
    >>> request = TestRequest()
    >>> index_page = WikiFilePage(context, request)

Let's look at the unmodified content of the index.html page:

    >>> print context.data
    <html>
        <body>
            <p>Wikifiable</p>
            <p>An <a href="target">existing file</a></p>
            <p>An <a href="folder">existing folder</a></p>
            <p>An <a href="index.html">existing page</a></p>
            <p>A <a href="newitem">new page</a></p>
            <p>A <a href="folder1/newitem">new page in a subfolder</a></p>
            <p>A [New Subject]</p>
            <p>An <a href="http://www.google.org">external absolute link</a></p>
            <p>An <a href="http://127.0.0.1/site/target">internal absolute link</a></p>
            <p>A <a href="http://127.0.0.1/site/newitem">new absolute link</a></p>
        </body>
    </html>
  
    
The page renders the content of the index.html document in a "wikified" version.
We use the renderBody method to include this "wikified" content into our
navigational structure, which is set aside for the moment :


    >>> print index_page.renderBody()
    <BLANKLINE>
            <p>Wikifiable</p>
            <p>An <a href="http://127.0.0.1/site/target">existing file</a></p>
            <p>An <a href="http://127.0.0.1/site/folder/@@wiki.html">existing folder</a></p>
            <p>An <a href="http://127.0.0.1/site/index.html/@@wiki.html">existing page</a></p>
            <p>A <a href="http://127.0.0.1/site/@@wikiedit.html?add=newitem" class="wiki-link">new page</a></p>
            <p>A <a href="http://127.0.0.1/site/@@wikiedit.html?add=folder1%2Fnewitem" class="wiki-link">new page in a subfolder</a></p>
            <p>A <a class="wiki-link" href="http://127.0.0.1/site/@@wikiedit.html?add=NewSubject">[New Subject]</a></p>
            <p>An <a href="http://www.google.org">external absolute link</a></p>
            <p>An <a href="http://127.0.0.1/site/target">internal absolute link</a></p>
            <p>A <a href="http://127.0.0.1/site/@@wikiedit.html?add=newitem" class="wiki-link">new absolute link</a></p>
    <BLANKLINE>

It uses the Dublin Core title (or "Untitled" if the title is not set).

    >>> from zope.app.dublincore.interfaces import IZopeDublinCore
    >>> index_page.title == IZopeDublinCore(context).title
    True

A user that wents up in the containment hierarchy should not get lost. We use
the container's index.html as the container content view as it is common :

    >>> from zorg.wikification.browser.wikipage import WikiContainerPage
    >>> folder_page = WikiContainerPage(site, request)
    >>> folder_page.renderBody() == index_page.renderBody()
    True
    
If we go into a subfolder the wikified links are adapted accordingly :

    >>> subfolder_page = WikiContainerPage(site[u'folder'][u'filledsubfolder'], TestRequest())
    >>> print subfolder_page.renderBody(debug=True)
    <BLANKLINE>
            <p>Wikifiable</p>
            <p>A <a class="wiki-link" href="http://127.0.0.1/site/folder/filledsubfolder/@@wikiedit.html?add=NewSubject">[New Subject]</a></p>
    <BLANKLINE>
    

More interesting is the question how one can add new content to an existing
place. Let's consider an empty folder as quite usual starting point :

    >>> empty_folder = site[u"folder"][u"emptysubfolder"]
    >>> len(empty_folder)
    0
    >>> print WikiContainerPage(empty_folder, request).renderBody()
    <div id="main">
         <p class="intro">This Wiki allows you to create pages and upload files by clicking placeholders.
            Such placeholders are marked by red dotted borders.
            If you click a placeholder you will be led to
            a page editor and other edit options.
         </p>
    <BLANKLINE>
         <p class="intro">You are looking currently at a folder without index.html file.</p>
         <p class="intro">Do you want to create a 
            <a class="wiki-link" href="./@@wikiedit.html?add=index.html">
                new index page
             </a>?
         </p>
    </div>
    <BLANKLINE>
    
    
We can follow this link and are directed to a WYSIWYG-Editor that allows us to
create a new index.html document.


Since we use Ajax we can also make the link modification more dynamic. This
is mainly a matter of registering a different ILinkProcessor :

    >>> from zorg.wikification.browser.interfaces import IWikiPage
    >>> from zorg.wikification.browser.interfaces import ILinkProcessor
    >>> from zorg.wikification.browser.wikilink import AjaxLinkProcessor
    >>> import zope.component
    >>> zope.component.provideAdapter(AjaxLinkProcessor, [IWikiPage], 
    ...                                                     ILinkProcessor)
    
The resulting HTML is more complex since it contains additional JavaScript
calls and menu items. The additional menu is rendered for text links in 
brackets and HTML links ...

    >>> print index_page.renderBody()
    <BLANKLINE>
    ...
    ...dropdownlinkmenu...>new page</a>...
    ...
    ...dropdownlinkmenu...>[New Subject]</a>...
    ...
    </div>
    ...   
   
   
Some of the menu items allow the user to edit the link within the view page.

    >>> from zorg.wikification.browser.wikipage import EditWikiPage
    >>> edit_page = EditWikiPage(site[u"index.html"], request)

The "Change Label" command shows that we can change a page without editor 
quite easily:

    >>> request.form = dict(label='New Label')
    >>> print edit_page.modifyLink(cmd='rename', link_id='wiki-link5')
    <BLANKLINE>
    ...
    ...dropdownlinkmenu...[New Label]...
    ...
    </div>
    ...      
    
One of the most usefull options is to upload a new file in one step:
        
    >>> request.form = dict(data='Some Content')
    >>> edit_page.uploadFile(link_id='wiki-link5')
    >>> print edit_page.renderBody()
    <BLANKLINE>
    ...
    <p>A <a href="http://127.0.0.1/site/New%20Label">New Label</a></p>
    ...

  


