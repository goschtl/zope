======
README
======

This package provides a persistent search query implementation. This search 
query is implemented as a filter object which can use search criteria for build
the search query. This package also offers some z3c.form based management views
which allo us to manage the search filter and it's search criteria. Let's 
define a site with indexes which allows us to build search filter for.

Note, this package depends on the new z3c.indexer package which offers a  
modular indexing concept. But you can use this package with the 
zope.app.catalog package too. You only have to build our own search citerium. 


Start a simple test setup
-------------------------

Setup some helpers:

  >>> import zope.component
  >>> from zope.site import folder
  >>> from zope.site import LocalSiteManager
  >>> from z3c.indexer.interfaces import IIndex

Setup a site

  >>> class SiteStub(folder.Folder):
  ...     """Sample site."""
  >>> site = SiteStub()

  >>> root['site'] = site
  >>> sm = LocalSiteManager(site)
  >>> site.setSiteManager(sm)

And set the site as the current site. This is normaly done by traversing to a 
site:

  >>> from zope.app.component import hooks
  >>> hooks.setSite(site)

Setup a IIntIds utility:

  >>> from zope.intid import IntIds
  >>> from zope.intid.interfaces import IIntIds
  >>> intids = IntIds()
  >>> sm['default']['intids'] = intids
  >>> sm.registerUtility(intids, IIntIds)


TextIndex
---------

Setup a text index:

  >>> from z3c.indexer.index import TextIndex
  >>> textIndex = TextIndex()
  >>> sm['default']['textIndex'] = textIndex
  >>> sm.registerUtility(textIndex, IIndex, name='textIndex')


FieldIndex
----------

Setup a field index:

  >>> from z3c.indexer.index import FieldIndex
  >>> fieldIndex = FieldIndex()
  >>> sm['default']['fieldIndex'] = fieldIndex
  >>> sm.registerUtility(fieldIndex, IIndex, name='fieldIndex')


ValueIndex
----------

Setup a value index:

  >>> from z3c.indexer.index import ValueIndex
  >>> valueIndex = ValueIndex()
  >>> sm['default']['valueIndex'] = valueIndex
  >>> sm.registerUtility(valueIndex, IIndex, name='valueIndex')


SetIndex
--------

Setup a set index:

  >>> from z3c.indexer.index import SetIndex
  >>> setIndex = SetIndex()
  >>> sm['default']['setIndex'] = setIndex
  >>> sm.registerUtility(setIndex, IIndex, name='setIndex')


DemoContent
-----------

Define a content object:

  >>> import persistent
  >>> import zope.interface
  >>> from zope.app.container import contained
  >>> from zope.schema.fieldproperty import FieldProperty

  >>> class IDemoContent(zope.interface.Interface):
  ...     """Demo content."""
  ...     title = zope.schema.TextLine(
  ...         title=u'Title',
  ...         default=u'')
  ... 
  ...     body = zope.schema.TextLine(
  ...         title=u'Body',
  ...         default=u'')
  ... 
  ...     field = zope.schema.TextLine(
  ...         title=u'a field',
  ...         default=u'')
  ... 
  ...     value = zope.schema.TextLine(
  ...         title=u'A value',
  ...         default=u'')
  ... 
  ...     iterable = zope.schema.Tuple(
  ...         title=u'A sequence of values',
  ...         default=())

  >>> class DemoContent(persistent.Persistent, contained.Contained):
  ...     """Demo content."""
  ...     zope.interface.implements(IDemoContent)
  ... 
  ...     title = FieldProperty(IDemoContent['title'])
  ...     body = FieldProperty(IDemoContent['body'])
  ...     field = FieldProperty(IDemoContent['field'])
  ...     value = FieldProperty(IDemoContent['value'])
  ...     iterable = FieldProperty(IDemoContent['iterable'])
  ... 
  ...     def __init__(self, title=u''):
  ...         self.title = title
  ... 
  ...     def __repr__(self):
  ...         return '<%s %r>' % (self.__class__.__name__, self.title)

Create and add the content object to the site:

  >>> demo = DemoContent(u'Title')
  >>> demo.body = u'Body text'
  >>> demo.field = u'Field'
  >>> demo.value = u'Value'
  >>> demo.iterable = (1, 2, 'Iterable')
  >>> site['demo'] = demo

The zope event subscriber for __setitem__ whould call the IIntIds register
method for our content object. But we didn't setup the relevant subscribers, so
we do this here:

  >>> uid = intids.register(demo)


Indexer
-------

Setup a indexer adapter for our content object.

  >>> from z3c.indexer.indexer import MultiIndexer
  >>> class DemoIndexer(MultiIndexer):
  ...     zope.component.adapts(IDemoContent)
  ... 
  ...     def doIndex(self):
  ... 
  ...         # index context in valueIndex
  ...         valueIndex = self.getIndex('textIndex')
  ...         txt = '%s %s' % (self.context.title, self.context.body)
  ...         valueIndex.doIndex(self.oid, txt)
  ... 
  ...         # index context in fieldIndex
  ...         fieldIndex = self.getIndex('fieldIndex')
  ...         fieldIndex.doIndex(self.oid, self.context.field)
  ... 
  ...         # index context in setIndex
  ...         setIndex = self.getIndex('setIndex')
  ...         setIndex.doIndex(self.oid, self.context.iterable)
  ... 
  ...         # index context in valueIndex
  ...         valueIndex = self.getIndex('valueIndex')
  ...         valueIndex.doIndex(self.oid, self.context.value)

Register the indexer adapter as a named adapter:

  >>> zope.component.provideAdapter(DemoIndexer, name='DemoIndexer')


Indexing
--------

Before we start indexing, we check the index:

  >>> textIndex.documentCount()
  0

  >>> fieldIndex.documentCount()
  0

  >>> setIndex.documentCount()
  0

  >>> valueIndex.documentCount()
  0

Now we can index our demo object:

  >>> from z3c.indexer.indexer import index
  >>> index(demo)

And check our indexes:

  >>> textIndex.documentCount()
  1

  >>> fieldIndex.documentCount()
  1

  >>> setIndex.documentCount()
  1

  >>> valueIndex.documentCount()
  1


Search Filter
-------------

Now we are ready and can start with our search filter implementation.
The following search filter returns no results by default because it defines 
NoTerm as getDefaultQuery. This is usefull if you have a larg set of data and 
you like to start with a empty query if no cirterium is selected.

  >>> from z3c.searcher import interfaces
  >>> from z3c.searcher.filter import EmptyTerm
  >>> from z3c.searcher.filter import SearchFilter

  >>> class IContentSearchFilter(interfaces.ISearchFilter):
  ...     """Search filter for content objects."""

  >>> class ContentSearchFilter(SearchFilter):
  ...     """Content search filter."""
  ... 
  ...     zope.interface.implements(IContentSearchFilter)
  ... 
  ...     def getDefaultQuery(self):
  ...         return EmptyTerm()


Search Criterium
----------------

And we define a criterium for our demo content. This text search criterium uses
the text index registered as ``textIndex`` above:

  >>> from z3c.searcher import criterium
  >>> class TextCriterium(criterium.TextCriterium):
  ...     """Full text search criterium for ``textIndex`` index."""
  ... 
  ...     indexOrName = 'textIndex'

Such a criterium can search in our index. Let's start with a empty search query:

  >>> from z3c.indexer.search import SearchQuery
  >>> searchQuery = SearchQuery()

You can see that the searchQuery returns a empty result.

  >>> len(searchQuery.searchResults())
  0

showcase
~~~~~~~~

Now we can create a criterium instance and give them a value:

  >>> sampleCriterium = TextCriterium()
  >>> sampleCriterium.value = u'Bod*'

Now the criterium is able to search in it's related index within the given 
value within a given (emtpy) search query. This empty query is only used as
a chainable query object. Each result get added or removed from this chain
dependent on it's connector ``And``, ``OR`` or ``Not``:

  >>> searchQuery = sampleCriterium.search(searchQuery)

Now you can see that our criterium found a result from the text index:

  >>> len(searchQuery.searchResults())
  1

  >>> content = list(searchQuery.searchResults())[0]
  >>> content.body
  u'Body text'


Search Criterium Factory
------------------------

The test above shows you how criterium can search in indexes. But that's not 
all. Our concept offers a search filter which can manage more then one search
criterium in a filter. A criterium is an adapter for a filter. This means we
need to create an adapter factory and register this factory as an adapter
for our filter. Let's now create this criterium adapter factory:

  >>> textCriteriumFactory = criterium.factory(TextCriterium, 'fullText')

This search criterium factory class implements ISearchCriteriumFactory:

  >>> interfaces.ISearchCriteriumFactory.implementedBy(textCriteriumFactory)
  True

and we register this adapter for our content search filter:

  >>> zope.component.provideAdapter(textCriteriumFactory, 
  ...     (IContentSearchFilter,), name='fullText')

showcase
~~~~~~~~

Now you can see that our content search filter knows about the search criterium
factories:

  >>> contentSearchFilter = ContentSearchFilter()
  >>> contentSearchFilter.criteriumFactories
  [(u'fullText', <z3c.searcher.criterium.TextCriteriumFactory object at ...>)]

Since the search criterium factory is an adapter for our search filter, the 
factory can adapt our contentSearchFilter:

  >>> textCriteriumFactory = textCriteriumFactory(contentSearchFilter)
  >>> textCriteriumFactory
  <z3c.searcher.criterium.TextCriteriumFactory object at ...>

Now we can call the factory and we will get back our search criterium instance:

  >>> textCriterium = textCriteriumFactory()
  >>> textCriterium
  <TextCriterium object at ...>

Our search criterium provides ISearchCriterium:

  >>> interfaces.ISearchCriterium.providedBy(textCriterium)
  True


Search Example
--------------

Now we are ready to search within our filter construct. First let's create a 
plain content search filter:

  >>> sampleFilter = ContentSearchFilter()

Then let's add a criterium by it's factory name:

  >>> sampleCriterium = sampleFilter.createCriterium('fullText')

Now we can set a value for the criterium:

  >>> sampleCriterium.value = u'Title'

And add the criterium to our filter:

  >>> sampleFilter.addCriterium(sampleCriterium)

That's all, now our filter is a ble to genearet a query:

  >>> sampleQuery = sampleFilter.generateQuery()

And the sample search query can return the result:

  >>> len(sampleQuery.searchResults())
  1

  >>> content = list(sampleQuery.searchResults())[0]
  >>> content.title
  u'Title'


Search Session
--------------

Before we show how to use the criterium and filter within z3c.form components,
we will show you how the search session is working. Let's register and create
a search session:

  >>> from z3c.searcher import session
  >>> zope.component.provideAdapter(session.SearchSession)

Now we can create a test request and get the session as adapter for a request:

  >>> import z3c.form.testing
  >>> request = z3c.form.testing.TestRequest()
  >>> searchSession = interfaces.ISearchSession(request)
  >>> searchSession
  <z3c.searcher.session.SearchSession object at ...>

The search session offers an API for store and manage filters: 

  >>> searchSession.addFilter('foo', sampleFilter)

And we can get such filters from the search session by name.

  >>> searchSession.getFilter('foo')
  <ContentSearchFilter object at ...>

Or we can get all search filters sotred in this session:

  >>> searchSession.getFilters()
  [<ContentSearchFilter object at ...>]

And we can remove a filter by it's name:

  >>> searchSession.removeFilter('foo')
  >>> searchSession.getFilters()
  []

There is also another argument called ``key`` in the search session methods. 
This argument can be used as namespace. If you need to support a specific 
filter only for one object instance, you can use a key which is unique to that 
object as discriminator.

  >>> myFilter = ContentSearchFilter()
  >>> searchSession.addFilter('foo', myFilter, key='myKey')

Such filters are only available if the right ``key`` is used:

  >>> searchSession.getFilter('foo') is None
  True

  >>> searchSession.getFilter('foo', key='myKey')
  <ContentSearchFilter object at ...>

  >>> searchSession.getFilters()
  []

Now let's cleanup our search session and remove the filter stored by the key:

  >>> searchSession.getFilters('myKey')
  [<ContentSearchFilter object at ...>]

  >>> searchSession.removeFilter('foo', 'myKey')
  >>> searchSession.getFilters('myKey')
  []


Criterium Form
--------------
Now we will show you how the form part is working. Each criterium can render 
itself within a form. We offer a CriteriumForm class for doing this. Let's
create and render such a criterium form:

  >>> import z3c.form.testing
  >>> from z3c.searcher import form
  >>> criteriumRow = form.CriteriumForm(textCriterium, request)
  >>> criteriumRow
  <z3c.searcher.form.CriteriumForm object at ...>

Before we can render the form, we need to register the templates:

  >>> from zope.configuration import xmlconfig
  >>> import zope.component
  >>> import zope.viewlet
  >>> import zope.app.component
  >>> import zope.app.security
  >>> import zope.app.publisher.browser
  >>> import z3c.template
  >>> import z3c.macro
  >>> import z3c.formui
  >>> xmlconfig.XMLConfig('meta.zcml', zope.component)()
  >>> xmlconfig.XMLConfig('meta.zcml', zope.viewlet)()
  >>> xmlconfig.XMLConfig('meta.zcml', zope.app.component)()
  >>> xmlconfig.XMLConfig('meta.zcml', zope.app.security)()
  >>> xmlconfig.XMLConfig('meta.zcml', zope.app.publisher.browser)()
  >>> xmlconfig.XMLConfig('meta.zcml', z3c.macro)()
  >>> xmlconfig.XMLConfig('meta.zcml', z3c.template)()
  >>> xmlconfig.XMLConfig('div-form.zcml', z3c.formui)()
  >>> context = xmlconfig.file('meta.zcml', z3c.template)
  >>> context = xmlconfig.string("""
  ... <configure
  ...     xmlns:z3c="http://namespaces.zope.org/z3c">
  ...  <configure package="z3c.searcher">
  ...  <z3c:template
  ...      template="filter.pt"
  ...      for=".form.FilterForm"
  ...      />
  ...  <z3c:template
  ...      template="criterium.pt"
  ...      for=".form.CriteriumForm"
  ...      />
  ...  <z3c:template
  ...      template="search.pt"
  ...      for=".form.SearchForm"
  ...      />
  ...  <z3c:template
  ...      template="table.pt"
  ...      for=".table.SearchTable"
  ...      />
  ... </configure>
  ... </configure>
  ... """, context=context)

And we also need some widgets from z3c.form:

  >>> import z3c.form.testing
  >>> z3c.form.testing.setupFormDefaults()

Now we can render the criterium form:

  >>> criteriumRow.update()
  >>> print criteriumRow.render()
  <tr>
    <td style="padding-right:5px;">
      <span>Text</span>
    </td>
    <td style="padding-right:5px;">
      <b>matches</b>
    </td>
    <td style="padding-right:5px;">
      <input type="text" id="form-widgets-value"
         name="form.widgets.value"
         class="text-widget required textline-field" value="" />
      <span class="option">
    <label for="form-widgets-connectorName-0">
      <input type="radio" id="form-widgets-connectorName-0"
             name="form.widgets.connectorName:list"
             class="radio-widget required choice-field"
             value="OR" checked="checked" />
      <span class="label">or</span>
    </label>
  </span><span class="option">
    <label for="form-widgets-connectorName-1">
      <input type="radio" id="form-widgets-connectorName-1"
             name="form.widgets.connectorName:list"
             class="radio-widget required choice-field"
             value="AND" />
      <span class="label">and</span>
    </label>
  </span><span class="option">
    <label for="form-widgets-connectorName-2">
      <input type="radio" id="form-widgets-connectorName-2"
             name="form.widgets.connectorName:list"
             class="radio-widget required choice-field"
             value="NOT" />
      <span class="label">not</span>
    </label>
  </span>
  <input name="form.widgets.connectorName-empty-marker"
         type="hidden" value="1" />
    </td>
    <td style="padding-right:5px;">
      <input type="submit" id="form-buttons-remove"
         name="form.buttons.remove"
         class="submit-widget button-field" value="Remove" />
    </td>
  </tr>


Filter Form
------------

There is also a filter form which can represent the SearchFilter. This form
includes the CriteriumForm part. Note we uses a dumy context becaue it's not
relevant where you render this form because the form will get the filters
from the session.

  >>> filterForm = form.FilterForm(object(), request)
  >>> filterForm
  <z3c.searcher.form.FilterForm object at ...>

But before we can use the form, we need to set our search filter class as 
factory. Because only this search filter knows our criteria:

  >>> filterForm.filterFactory = ContentSearchFilter

Now we can render our filter form:

  >>> filterForm.update()
  >>> print filterForm.render()
  <fieldset>
  <legend>Filter</legend>
  <div>
    <label for="filterformnewCriterium">
      New Criterium
    </label>
    <select name="filterformnewCriterium" size="1">
      <option value="fullText">fullText</option>
    </select>
    <input type="submit" id="filterform-buttons-add"
           name="filterform.buttons.add"
           class="submit-widget button-field" value="Add" />
  </div>
  <div>
    <input type="submit" id="filterform-buttons-search"
           name="filterform.buttons.search"
           class="submit-widget button-field" value="Search" />
    <input type="submit" id="filterform-buttons-clear"
           name="filterform.buttons.clear"
           class="submit-widget button-field" value="Clear" />
  </div>
  </fieldset>


Search Form
-----------

There is also a search form which allows you to simply define a search page.
This search form uses the criterium and filter form and allows you to simply
create a search page. Let's define a custom search page:

  >>> class ContentSearchForm(form.SearchForm):
  ... 
  ...     filterFactory = ContentSearchFilter

Before we can use the form, our request needs to provide the form UI layer:

  >>> from zope.interface import alsoProvides
  >>> from z3c.formui.interfaces import IDivFormLayer
  >>> alsoProvides(request, IDivFormLayer)

That's all you need for write a simple search form. This form uses it's own
content search filter and of corse the criteria configured for this filter.

  >>> searchForm = ContentSearchForm(object(), request)
  >>> searchForm.update()
  >>> print searchForm.render()
  <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="edit-form"
        name="form" id="form">
    <div class="viewspace">
        <div class="required-info">
           <span class="required">*</span>
           &ndash; required
        </div>
      <div>
    <fieldset>
  <legend>Filter</legend>
  <div>
    <label for="filterformnewCriterium">
      New Criterium
    </label>
    <select name="filterformnewCriterium" size="1">
      <option value="fullText">fullText</option>
    </select>
    <input type="submit" id="filterform-buttons-add"
           name="filterform.buttons.add"
           class="submit-widget button-field" value="Add" />
  </div>
  <div>
    <input type="submit" id="filterform-buttons-search"
           name="filterform.buttons.search"
           class="submit-widget button-field" value="Search" />
    <input type="submit" id="filterform-buttons-clear"
           name="filterform.buttons.clear"
           class="submit-widget button-field" value="Clear" />
  </div>
  </fieldset>
    </div>
      <div>
      </div>
    </div>
    <div>
      <div class="buttons">
      </div>
    </div>
  </form>


Search Table
------------

There is also a search table. This search table uses the criterium and filter
form and allows you to simply create a search page which will list the results
as table. Let's define a custom search table:

  >>> from z3c.searcher import table
  >>> class ContentSearchTable(table.SearchTable):
  ... 
  ...     filterFactory = ContentSearchFilter

Before we can use the form, our request needs to provide the form UI layer:

  >>> from zope.interface import alsoProvides
  >>> from z3c.formui.interfaces import IDivFormLayer
  >>> alsoProvides(request, IDivFormLayer)

That's all you need for write a simple search form. This form uses it's own
content search filter and of corse the criteria configured for this filter.

  >>> searchTable = ContentSearchTable(object(), request)
  >>> searchTable.update()
  >>> print searchTable.render()
  <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="edit-form"
        name="formTable" id="formTable">
    <div class="viewspace">
        <div class="required-info">
           <span class="required">*</span>
           &ndash; required
        </div>
      <div>
      <div class="filterForm">
        <fieldset>
  <legend>Filter</legend>
  <div>
    <label for="filterformnewCriterium">
      New Criterium
    </label>
    <select name="filterformnewCriterium" size="1">
      <option value="fullText">fullText</option>
    </select>
    <input type="submit" id="filterform-buttons-add"
         name="filterform.buttons.add"
         class="submit-widget button-field" value="Add" />
  </div>
  <div>
    <input type="submit" id="filterform-buttons-search"
         name="filterform.buttons.search"
         class="submit-widget button-field" value="Search" />
    <input type="submit" id="filterform-buttons-clear"
         name="filterform.buttons.clear"
         class="submit-widget button-field" value="Clear" />
  </div>
  </fieldset>
      </div>
      <div>
      </div>
    </div>
    </div>
    <div>
      <div class="buttons">
      </div>
    </div>
  </form>
