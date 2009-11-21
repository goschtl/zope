Catalogs
========

Catalogs are simple tools used to supppot searching.  A catalog
manages a collection of indexes, and aranges for objects to indexed
with it's contained indexes.

TODO: Filters
      Catalogs should provide the option to filter the objects the
      catalog. This would facilitate the use of separate catalogs for
      separate purposes.  It should be possible to specify a a
      collection of types (interfaces) to be cataloged and a filtering
      expression.  Perhaps another option would be to be the ability
      to specify a names filter adapter.

Catalogs use a unique-id tool to assign short (integer) ids to
objects.  Before creating a catalog, you must create a intid tool:

  >>> print http(r"""
  ... POST /++etc++site/default/@@+/action.html HTTP/1.1
  ... Authorization: Basic bWdyOm1ncnB3
  ... Content-Length: 78
  ... Content-Type: application/x-www-form-urlencoded
  ... Referer: http://localhost:8081/++etc++site/default/@@+
  ... 
  ... type_name=BrowserAdd__zope.intid.IntIds&id=&add=+Add+""",
  ... handle_errors=False)
  HTTP/1.1 303 ...

And register it:

  >>> print http(r"""
  ... POST /++etc++site/default/IntIds/addRegistration.html HTTP/1.1
  ... Authorization: Basic mgr:mgrpw
  ... Referer: http://localhost:8081/++etc++site/default/IntIds/
  ... Content-Type: multipart/form-data; boundary=----------CedQTrEQIEPbgfYhvcITAhQi2aJdgu3tYfJ0WYQmkpLQTt6OTOpd5GJ
  ... 
  ... ------------CedQTrEQIEPbgfYhvcITAhQi2aJdgu3tYfJ0WYQmkpLQTt6OTOpd5GJ
  ... Content-Disposition: form-data; name="field.name"
  ... 
  ... 
  ... ------------CedQTrEQIEPbgfYhvcITAhQi2aJdgu3tYfJ0WYQmkpLQTt6OTOpd5GJ
  ... Content-Disposition: form-data; name="field.provided"
  ... 
  ... zope.intid.interfaces.IIntIds
  ... ------------CedQTrEQIEPbgfYhvcITAhQi2aJdgu3tYfJ0WYQmkpLQTt6OTOpd5GJ
  ... Content-Disposition: form-data; name="field.provided-empty-marker"
  ... 
  ... 1
  ... ------------CedQTrEQIEPbgfYhvcITAhQi2aJdgu3tYfJ0WYQmkpLQTt6OTOpd5GJ
  ... Content-Disposition: form-data; name="field.comment"
  ... 
  ... 
  ... ------------CedQTrEQIEPbgfYhvcITAhQi2aJdgu3tYfJ0WYQmkpLQTt6OTOpd5GJ
  ... Content-Disposition: form-data; name="field.actions.register"
  ... 
  ... Register
  ... ------------CedQTrEQIEPbgfYhvcITAhQi2aJdgu3tYfJ0WYQmkpLQTt6OTOpd5GJ--
  ... """, handle_errors=False)
  HTTP/1.1 303 ...
  ...


Moving short-id management outside of catalogs make it possible to
join searches accross multiple catalogs and indexing tools
(e.g. relationship indexes).

TODO: Filters?
      Maybe unique-id tools should be filtered as well, however, this
      would limit the value of unique id tools for providing
      cross-catalog/cross-index merging.  At least the domain for a
      unique id tool would be broader than the domain of a catalog.
      The value of filtering in the unique id tool is that it limits
      the amount of work that needs to be done by catalogs.
      One obvious aplication is to provide separate domains for
      ordinary and meta content. If we did this, then we'd need to be
      able to select, and, perhaps, alter, the unique-id tool used by
      a catalog.
   
Once we have a unique-id tool, you can add a catalog:

  >>> print http(r"""
  ... POST /++etc++site/default/@@+/action.html HTTP/1.1
  ... Authorization: Basic bWdyOm1ncnB3
  ... Content-Length: 77
  ... Content-Type: application/x-www-form-urlencoded
  ... Referer: http://localhost:8081/++etc++site/default/@@+
  ... 
  ... type_name=BrowserAdd__zope.catalog.catalog.Catalog&id=&add=+Add+""")
  HTTP/1.1 303 ...

and register it:

  >>> print http(r"""
  ... POST /++etc++site/default/Catalog/addRegistration.html HTTP/1.1
  ... Authorization: Basic bWdyOm1ncnB3
  ... Referer: http://localhost:8081/++etc++site/default/Catalog/
  ... Content-Type: multipart/form-data; boundary=----------61t9UJyoacebBevQVdNrlvXP6T9Ik3Xo4RyXkwJJWvuhao65RTuAPRa
  ... 
  ... ------------61t9UJyoacebBevQVdNrlvXP6T9Ik3Xo4RyXkwJJWvuhao65RTuAPRa
  ... Content-Disposition: form-data; name="field.name"
  ... 
  ... 
  ... ------------61t9UJyoacebBevQVdNrlvXP6T9Ik3Xo4RyXkwJJWvuhao65RTuAPRa
  ... Content-Disposition: form-data; name="field.provided"
  ... 
  ... zope.catalog.interfaces.ICatalog
  ... ------------61t9UJyoacebBevQVdNrlvXP6T9Ik3Xo4RyXkwJJWvuhao65RTuAPRa
  ... Content-Disposition: form-data; name="field.provided-empty-marker"
  ... 
  ... 1
  ... ------------61t9UJyoacebBevQVdNrlvXP6T9Ik3Xo4RyXkwJJWvuhao65RTuAPRa
  ... Content-Disposition: form-data; name="field.comment"
  ... 
  ... 
  ... ------------61t9UJyoacebBevQVdNrlvXP6T9Ik3Xo4RyXkwJJWvuhao65RTuAPRa
  ... Content-Disposition: form-data; name="field.actions.register"
  ... 
  ... Register
  ... ------------61t9UJyoacebBevQVdNrlvXP6T9Ik3Xo4RyXkwJJWvuhao65RTuAPRa--
  ... """)
  HTTP/1.1 303 ...


Once we have a catalog, we can add indexes to it.  Before we add an
index, let's add a templated page.  When adding indexes, existing
objects are indexed, so the document we add now will appear in the
index:

  >>> print http(r"""
  ... POST /+/zope.app.zptpage.ZPTPage%3D HTTP/1.1
  ... Authorization: Basic bWdyOm1ncnB3
  ... Content-Length: 780
  ... Content-Type: multipart/form-data; boundary=---------------------------1425445234777458421417366789
  ... Referer: http://localhost:8081/+/zope.app.zptpage.ZPTPage=
  ... 
  ... -----------------------------1425445234777458421417366789
  ... Content-Disposition: form-data; name="field.source"
  ... 
  ... <html>
  ... <body>
  ... Now is the time, for all good dudes to come to the aid of their country.
  ... </body>
  ... </html>
  ... -----------------------------1425445234777458421417366789
  ... Content-Disposition: form-data; name="field.expand.used"
  ... 
  ... 
  ... -----------------------------1425445234777458421417366789
  ... Content-Disposition: form-data; name="field.evaluateInlineCode.used"
  ... 
  ... 
  ... -----------------------------1425445234777458421417366789
  ... Content-Disposition: form-data; name="UPDATE_SUBMIT"
  ... 
  ... Add
  ... -----------------------------1425445234777458421417366789
  ... Content-Disposition: form-data; name="add_input_name"
  ... 
  ... dudes
  ... -----------------------------1425445234777458421417366789--
  ... """)
  HTTP/1.1 303 ...

Perhaps the most common type of index to be added is a text index.
Most indexes require the specification of an interface, an attribute,
and an indication of whether the attribute must be called.

TODO: Simplify the UI for selecting interfaces and attributes
      There are a number of ways the UI for this could be made more
      user friendly:

      - If the user selects an interface, we could then provide a
        select list of possible attributes and we could determine the
        callability.  Perhaps selection of an interface should be
        required. 

      - An index should have a way to specify default values. In
        particular, text indexes usially use ISearchableText and
        searchableText. 

For text indexes, one generally uses
`zope.index.text.interfaces.ISearchableText`,
`getSearchableText` and True.

  >>> print http(r"""
  ... POST /++etc++site/default/Catalog/+/AddTextIndex%3D HTTP/1.1
  ... Authorization: Basic bWdyOm1ncnB3
  ... Content-Length: 1008
  ... Content-Type: multipart/form-data; boundary=---------------------------12609588153518590761493918424
  ... Referer: http://localhost:8081/++etc++site/default/Catalog/+/AddTextIndex=
  ... 
  ... -----------------------------12609588153518590761493918424
  ... Content-Disposition: form-data; name="field.interface"
  ... 
  ... zope.index.text.interfaces.ISearchableText
  ... -----------------------------12609588153518590761493918424
  ... Content-Disposition: form-data; name="field.interface-empty-marker"
  ... 
  ... 1
  ... -----------------------------12609588153518590761493918424
  ... Content-Disposition: form-data; name="field.field_name"
  ... 
  ... getSearchableText
  ... -----------------------------12609588153518590761493918424
  ... Content-Disposition: form-data; name="field.field_callable.used"
  ... 
  ... 
  ... -----------------------------12609588153518590761493918424
  ... Content-Disposition: form-data; name="field.field_callable"
  ... 
  ... on
  ... -----------------------------12609588153518590761493918424
  ... Content-Disposition: form-data; name="UPDATE_SUBMIT"
  ... 
  ... Add
  ... -----------------------------12609588153518590761493918424
  ... Content-Disposition: form-data; name="add_input_name"
  ... 
  ... 
  ... -----------------------------12609588153518590761493918424--
  ... """, handle_errors=False)
  HTTP/1.1 303 ...


We can visit the advanced tab of the catalog to get some index
statistics.  Doing so, we see that we have a single document and that
the total word count is 8. The word count is only 8 because ssome stop
words have been eliminated.


  >>> print http(r"""
  ... GET /++etc++site/default/Catalog/@@advanced.html HTTP/1.1
  ... Authorization: Basic bWdyOm1ncnB3
  ... Referer: http://localhost:8081/++etc++site/default/Catalog/@@contents.html
  ... """)
  HTTP/1.1 200 ...
  ...
  <table class="listing" summary="Indexes">
     <tr><th>Index</th>
         <th>Document Count</th>
         <th>Word Count</th>
     </tr>
     <tr>
         <td>TextIndex</td>
         <td>1</td>
         <td>8</td>
      </tr>
  </table>
  ...

Now lets add some more pages:

  >>> print http(r"""
  ... POST /+/zope.app.zptpage.ZPTPage%3D HTTP/1.1
  ... Authorization: Basic bWdyOm1ncnB3
  ... Content-Length: 754
  ... Content-Type: multipart/form-data; boundary=---------------------------1213614620286666602740364725
  ... Referer: http://localhost:8081/+/zope.app.zptpage.ZPTPage=
  ... 
  ... -----------------------------1213614620286666602740364725
  ... Content-Disposition: form-data; name="field.source"
  ... 
  ... <html>
  ... <body>
  ... Dudes, we really need to switch to Zope 3 now.
  ... </body>
  ... </html>
  ... -----------------------------1213614620286666602740364725
  ... Content-Disposition: form-data; name="field.expand.used"
  ... 
  ... 
  ... -----------------------------1213614620286666602740364725
  ... Content-Disposition: form-data; name="field.evaluateInlineCode.used"
  ... 
  ... 
  ... -----------------------------1213614620286666602740364725
  ... Content-Disposition: form-data; name="UPDATE_SUBMIT"
  ... 
  ... Add
  ... -----------------------------1213614620286666602740364725
  ... Content-Disposition: form-data; name="add_input_name"
  ... 
  ... zope3
  ... -----------------------------1213614620286666602740364725--
  ... """)
  HTTP/1.1 303 ...

  >>> print http(r"""
  ... POST /+/zope.app.zptpage.ZPTPage%3D HTTP/1.1
  ... Authorization: Basic bWdyOm1ncnB3
  ... Content-Length: 838
  ... Content-Type: multipart/form-data; boundary=---------------------------491825988706308579952614349
  ... Referer: http://localhost:8081/+/zope.app.zptpage.ZPTPage=
  ... 
  ... -----------------------------491825988706308579952614349
  ... Content-Disposition: form-data; name="field.source"
  ... 
  ... <html>
  ... <body>
  ... <p>Writing tests as doctests makes them much more understandable.</p>
  ... <p>Python 2.4 has major enhancements to the doctest module.</p>
  ... </body>
  ... </html>
  ... -----------------------------491825988706308579952614349
  ... Content-Disposition: form-data; name="field.expand.used"
  ... 
  ... 
  ... -----------------------------491825988706308579952614349
  ... Content-Disposition: form-data; name="field.evaluateInlineCode.used"
  ... 
  ... 
  ... -----------------------------491825988706308579952614349
  ... Content-Disposition: form-data; name="UPDATE_SUBMIT"
  ... 
  ... Add
  ... -----------------------------491825988706308579952614349
  ... Content-Disposition: form-data; name="add_input_name"
  ... 
  ... doctest
  ... -----------------------------491825988706308579952614349--
  ... """)
  HTTP/1.1 303 ...

Now, if we visit the catalog advanced tab, we can see that the 3
documents have been indexed and that the word count has increased to 30:

  >>> print http(r"""
  ... GET /++etc++site/default/Catalog/@@advanced.html HTTP/1.1
  ... Authorization: Basic bWdyOm1ncnB3
  ... Referer: http://localhost:8081/++etc++site/default/Catalog/@@contents.html
  ... """)
  HTTP/1.1 200 ...
  ...
  <table class="listing" summary="Indexes">
     <tr><th>Index</th>
         <th>Document Count</th>
         <th>Word Count</th>
     </tr>
     <tr>
         <td>TextIndex</td>
         <td>3</td>
         <td>30</td>
      </tr>
  </table>
  ...


Now that we have a catalog with some documents indexed, we can search
it.  The catalog is really meant to be used from Python:

  >>> root = getRootFolder()

We'll make our root folder the site (this would normally be done by
the publisher):

  >>> from zope.component.hooks import setSite
  >>> setSite(root)

Now, we'll get the catalog:

  >>> import zope.component
  >>> from zope.catalog.interfaces import ICatalog
  >>> catalog = zope.component.getUtility(ICatalog)

And search it to find the names of all of the documents that contain
the word 'now':

  >>> results = catalog.searchResults(TextIndex='now')
  >>> [result.__name__ for result in results]
  [u'dudes', u'zope3']

TODO
   This stuff needs a lot of work.  The indexing interfaces, despite
   being rather elaborate are still a bit too simple.  There really
   should be more provision for combining result.  In particular,
   catalog should have a search interface that returns ranked docids,
   rather than documents.

You don't have to use the search algorithm build into the catalog. You
can implement your own search algorithms and use them with a catalog's
indexes.   
