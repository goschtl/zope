Adding a site catalog:

This also presupposes a product called "blog", which allows you to create
content objects - this should apply equally to any other content objects
in your own zope install, presuming they have attributes with values ;)

Add Utility Service to ++etc++site.  Make sure it's marked "Active".

Add a new folder to ++etc++site to keep things clean, called 'searches'.

Go to /++etc++site/searches, the new folder

Add a Catalog, called 'blogCatalog'.  This will take you to a "New Utility
Registration" page.  Enter a name of 'blogCatalog' (this is the name you
will use to find the utility via getUtility()), a provided interface of
"ICatalogQuery" (the interface we implement for a queryable object), a
permission of zope.View, and make it active.

Now we have a utility that implements ICatalogQuery named 'blogCatalog'.
Look in ++etc++site, Utility service, see that it's registered.

Make the blogCatalog have a fieldindex for 'author' - click on the blogCatalog
object, select the "Indexes" tab, and add a Field Index.  Interface can be
zope.interface.Interface, field name should be 'author'.

Add a blog object with an author field to the content space.

Now we add a search interface:

Add the Views Service to ++etc++site.  Make sure it's marked "Active".

Add a module to ++etc++site/default called 'module'. Insert code:

"""
from zope.app import zapi 
from zope.app.catalog.interfaces.catalog import ICatalogQuery

class CatalogView: 
    def search(self): 
        request = self.request 
        catalog = zapi.getUtility(
            self.context,
            ICatalogQuery, 
            name='blogCatalog') 
        terms = request['terms'] 
        return catalog.searchResults(author=terms)
"""

The "name" in the getUtility call is the name you gave the catalog utility
when you added it.

Go to ++etc++site/searches, add a page folder, 'pageFolder', click on it and
go to Default Registration tab. Specify the following properties:

  For interface: zope.interface.Interface
  Dotted name of factory: module.CatalogView
  Permission: zope.View

Add a page, 'search' to etc/searches/pageFolder:

"""
<html>
  <tal:block define="results view/search">
    <b>Results:</b>
    <div tal:repeat="result results">
      <a tal:define="url result/@@absolute_url"
         tal:attributes="href url"
         tal:content="url" />
    </div>
  </tal:block>
</html>
"""

You can now access http://$ZOPE:$PORT/search?terms=authorname
Where search is the name of the page in the pageFolder, authorname is the
author name you wish to search for.
