=========
Z3C Table
=========

The goal of this package is to offer a modular table rendering library. We use 
the content provider pattern and the column are implemented as adapters which 
will give us a powerfull base conept.


Some important concepts we use
------------------------------

- separate impleentation in update render parts, This allows to manipulate 
  data after update call before we render.

- allo to use page templates if needed

- allow to use the rendered batch outside the existing table HTML part. This
  could be done if you use a view which takes care and offers table and batch 
  varaiables as a you know from model - view - controller patterns.
  If you use viewlets, it gets a little bit harder to separate the table and
  batch into different components. But this is also possible. You can implement
  a table as named adapter for context, request and implement content a 
  provider or viewlets for batch and table. With this separation you can call 
  the batch before the table because you can get the named table adapter and 
  update the data. After update and render the batch you can later access the 
  table content provider and get the named adapter again and only render the 
  table. This supports not calling the table adapters update method more then 
  once.


Note
----

As you probably know, batching is only possible after sorting columns. This is 
a nightmare if it comes to performance. The reason is, all data need to get 
sorted before the batch can start at the given position. And sorting can most 
the time only be done by touching each object. This means you have to take care
if you are using a large set of data, even if you use batching.


Sample data setup
-----------------

Let's create a sample container which we can use as our iterable context:

  >>> from zope.app.container import btree
  >>> class Container(btree.BTreeContainer):
  ...     """Sample container."""
  >>> container = Container()

and create a sample content object which we use as container item:

  >>> class Content(object):
  ...     """Sample content."""
  ...     def __init__(self, title, number):
  ...         self.title = title
  ...         self.number = number

Now setup some items:

  >>> container[u'first'] = Content('First', 1)
  >>> container[u'second'] = Content('Second', 2)
  >>> container[u'third'] = Content('Third', 3)


Table
-----

Create a test request and represent the table:

  >>> from zope.publisher.browser import TestRequest
  >>> from z3c.table import table
  >>> request = TestRequest()
  >>> plainTable = table.Table(container, request)

Now we can update and render the table:

  >>> plainTable.update()
  >>> plainTable.render()
  u''


Column Adapter
--------------

Now we can register a column for our table:

  >>> import zope.component
  >>> from z3c.table import interfaces
  >>> from z3c.table import column

  >>> class TitleColumn(column.Column):
  ... 
  ...     weight = 10
  ... 
  ...     def renderHeadCell(self):
  ...         return u'Title'
  ... 
  ...     def renderCell(self, item):
  ...         return u'Title: %s' % item.title

Now we can register our column adapter.

  >>> zope.component.provideAdapter(TitleColumn,
  ...     (None, None, interfaces.ITable), provides=interfaces.IColumn,
  ...      name='firstColumn')

Now we can render the table again:

  >>> plainTable.update()
  >>> print plainTable.render()
  <table>
    <thead>
      <tr>
        <th>Title</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Title: First</td>
      </tr>
      <tr>
        <td>Title: Second</td>
      </tr>
      <tr>
        <td>Title: Third</td>
      </tr>
    </tbody>
  </table>

We can also use the predefined name column:

  >>> zope.component.provideAdapter(column.NameColumn,
  ...     (None, None, interfaces.ITable), provides=interfaces.IColumn,
  ...      name='secondColumn')

Now we will get a nother additional column:

  >>> plainTable.update()
  >>> print plainTable.render()
  <table>
    <thead>
      <tr>
        <th>Name</th>
        <th>Title</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>first</td>
        <td>Title: First</td>
      </tr>
      <tr>
        <td>second</td>
        <td>Title: Second</td>
      </tr>
      <tr>
        <td>third</td>
        <td>Title: Third</td>
      </tr>
    </tbody>
  </table>


Colspan
-------

Now let's show how we can define a colspan condition of 2 for an column:

  >>> class ColspanColumn(column.NameColumn):
  ... 
  ...     weight = 999
  ... 
  ...     def getColspan(self, item):
  ...         # colspan condition
  ...         if item.__name__ == 'first':
  ...             return 2
  ...         else:
  ...             return 0
  ... 
  ...     def renderHeadCell(self):
  ...         return u'Colspan'
  ... 
  ...     def renderCell(self, item):
  ...         return u'colspan: %s' % item.title

Now we register this column adapter as colspanColumn:

  >>> zope.component.provideAdapter(ColspanColumn,
  ...     (None, None, interfaces.ITable), provides=interfaces.IColumn,
  ...      name='colspanColumn')


Now you can see that the colspan of the ColspanAdapter is larger then the table
columns. This wil raise a VlaueError:

  >>> plainTable.update()
  Traceback (most recent call last):
  ...
  ValueError: Colspan for column '<ColspanColumn u'colspanColumn'>' larger then table.

But if we set the column as first row, it weill render the colspan correct:

  >>> class CorrectColspanColumn(ColspanColumn):
  ...     """Colspan with correct weight."""
  ... 
  ...     weight = 0

Register and render the table again:

  >>> zope.component.provideAdapter(CorrectColspanColumn,
  ...     (None, None, interfaces.ITable), provides=interfaces.IColumn,
  ...      name='colspanColumn')

  >>> plainTable.update()
  >>> print plainTable.render()
  <table>
    <thead>
      <tr>
        <th>Colspan</th>
        <th>Name</th>
        <th>Title</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td colspan="2">colspan: First</td>
        <td>Title: First</td>
      </tr>
      <tr>
        <td>colspan: Second</td>
        <td>second</td>
        <td>Title: Second</td>
      </tr>
      <tr>
        <td>colspan: Third</td>
        <td>third</td>
        <td>Title: Third</td>
      </tr>
    </tbody>
  </table>


Setup columns
-------------

The existing implementation allows us to define a table in a class without
to use the modular adapter pattern for columns. 

First we need to define a column which cna render a value for our items:

  >>> class SimpleColumn(column.Column):
  ... 
  ...     weight = 0
  ... 
  ...     def renderCell(self, item):
  ...         return item.title

Let's define our table which defines the columns explicit. you can also see,
that we do not return the columns in the correct order:

  >>> class PrivateTable(table.Table):
  ... 
  ...     def setUpColumns(self):
  ...         firstColumn = TitleColumn(self.context, self.request, self)
  ...         firstColumn.__name__ = u'title'
  ...         firstColumn.weight = 1
  ...         secondColumn = SimpleColumn(self.context, self.request, self)
  ...         secondColumn.__name__ = u'simple'
  ...         secondColumn.weight = 2
  ...         secondColumn.header = u'The second column'
  ...         return [secondColumn, firstColumn]

Now we can create, update and render the table and see that this renders a nice
table too:

  >>> privateTable = PrivateTable(container, request) 
  >>> privateTable.update()
  >>> print privateTable.render()
  <table>
    <thead>
      <tr>
        <th>Title</th>
        <th>The second column</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Title: First</td>
        <td>First</td>
      </tr>
      <tr>
        <td>Title: Second</td>
        <td>Second</td>
      </tr>
      <tr>
        <td>Title: Third</td>
        <td>Third</td>
      </tr>
    </tbody>
  </table>


Cascading Style Sheet
---------------------

Our table and column implementation supports css class assignment. Let's define 
a table and columns with some css class values:

  >>> class CSSTable(table.Table):
  ... 
  ...     cssClasses = {'table': 'table',
  ...                   'thead': 'thead',
  ...                   'tbody': 'tbody',
  ...                   'th': 'th',
  ...                   'tr': 'tr',
  ...                   'td': 'td'}
  ... 
  ...     def setUpColumns(self):
  ...         firstColumn = TitleColumn(self.context, self.request, self)
  ...         firstColumn.__name__ = u'title'
  ...         firstColumn.__parent__ = self
  ...         firstColumn.weight = 1
  ...         firstColumn.cssClasses = {'th':'thCol', 'td':'tdCol'}
  ...         secondColumn = SimpleColumn(self.context, self.request, self)
  ...         secondColumn.__name__ = u'simple'
  ...         secondColumn.__parent__ = self
  ...         secondColumn.weight = 2
  ...         secondColumn.header = u'The second column'
  ...         return [secondColumn, firstColumn]

Now let's see if we got the cs class assigned which we defined in the table and
column. Note that the ``th`` and ``td`` got CSS declarations from the table and
from the column.

  >>> cssTable = CSSTable(container, request) 
  >>> cssTable.update()
  >>> print cssTable.render()
  <table class="table">
    <thead class="thead">
      <tr class="tr">
        <th class="thCol th">Title</th>
        <th class="th">The second column</th>
      </tr>
    </thead>
    <tbody class="tbody">
      <tr class="tr">
        <td class="tdCol td">Title: First</td>
        <td class="td">First</td>
      </tr>
      <tr class="tr">
        <td class="tdCol td">Title: Second</td>
        <td class="td">Second</td>
      </tr>
      <tr class="tr">
        <td class="tdCol td">Title: Third</td>
        <td class="td">Third</td>
      </tr>
    </tbody>
  </table>


Alternating table
-----------------

We offer built in support for alternating table rows based on even and odd CSS
classes. Let's define a table including other CSS classes. For even/odd support,
we only need to define the ``cssClassEven`` and ``cssClassOdd`` CSS classes:

  >>> class AlternatingTable(table.Table):
  ... 
  ...     cssClasses = {'table': 'table',
  ...                   'thead': 'thead',
  ...                   'tbody': 'tbody',
  ...                   'th': 'th',
  ...                   'tr': 'tr',
  ...                   'td': 'td'}
  ... 
  ...     cssClassEven = u'even'
  ...     cssClassOdd = u'odd'
  ... 
  ...     def setUpColumns(self):
  ...         firstColumn = TitleColumn(self.context, self.request, self)
  ...         firstColumn.__name__ = u'title'
  ...         firstColumn.__parent__ = self
  ...         firstColumn.weight = 1
  ...         firstColumn.cssClasses = {'th':'thCol', 'td':'tdCol'}
  ...         secondColumn = SimpleColumn(self.context, self.request, self)
  ...         secondColumn.__name__ = u'simple'
  ...         secondColumn.__parent__ = self
  ...         secondColumn.weight = 2
  ...         secondColumn.header = u'The second column'
  ...         return [secondColumn, firstColumn]

Now update and render the new table. As you can see the given ``tr`` class get 
used additional to the even and odd classes:

  >>> alternatingTable = AlternatingTable(container, request) 
  >>> alternatingTable.update()
  >>> print alternatingTable.render()
  <table class="table">
    <thead class="thead">
      <tr class="tr">
        <th class="thCol th">Title</th>
        <th class="th">The second column</th>
      </tr>
    </thead>
    <tbody class="tbody">
      <tr class="even tr">
        <td class="tdCol td">Title: First</td>
        <td class="td">First</td>
      </tr>
      <tr class="odd tr">
        <td class="tdCol td">Title: Second</td>
        <td class="td">Second</td>
      </tr>
      <tr class="even tr">
        <td class="tdCol td">Title: Third</td>
        <td class="td">Third</td>
      </tr>
    </tbody>
  </table>


Sorting Table
-------------

Another table feature is the support for sorting data given from columns. Since
sorting table data is an important feature, we offer this by default. But it
only gets used if there is a sortOn value set. You can set this value at class
level by adding a defaultSortOn value or set it as a request value. We show you
how to do this later. We also need a columns which allows us to do a better 
sort sample. Our new sorting column will use the content items number value
for sorting:

  >>> class NumberColumn(column.Column):
  ... 
  ...     header = u'Number'
  ...     weight = 20
  ... 
  ...     def getSortKey(self, item):
  ...         return item.number
  ... 
  ...     def renderCell(self, item):
  ...         return 'number: %s' % item.number


Now let's setup a table:

  >>> class SortingTable(table.Table):
  ... 
  ...     def setUpColumns(self):
  ...         firstColumn = TitleColumn(self.context, self.request, self)
  ...         firstColumn.__name__ = u'title'
  ...         firstColumn.__parent__ = self
  ...         secondColumn = NumberColumn(self.context, self.request, self)
  ...         secondColumn.__name__ = u'number'
  ...         secondColumn.__parent__ = self
  ...         return [firstColumn, secondColumn]

We also need some more container items which we can use for sorting:

  >>> container[u'fourth'] = Content('Fourth', 4)
  >>> container[u'zero'] = Content('Zero', 0)

And render them without set a sortOn value:

  >>> sortingTable = SortingTable(container, request) 
  >>> sortingTable.update()
  >>> print sortingTable.render()
  <table>
    <thead>
      <tr>
        <th>Title</th>
        <th>Number</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Title: First</td>
        <td>number: 1</td>
      </tr>
      <tr>
        <td>Title: Fourth</td>
        <td>number: 4</td>
      </tr>
      <tr>
        <td>Title: Second</td>
        <td>number: 2</td>
      </tr>
      <tr>
        <td>Title: Third</td>
        <td>number: 3</td>
      </tr>
      <tr>
        <td>Title: Zero</td>
        <td>number: 0</td>
      </tr>
    </tbody>
  </table>

As you can see this table doesn't provide any explicit order. Let's find out
the index of our column which we like to sort on:

  >>> sortOnId = sortingTable.rows[0][1][1].id
  >>> sortOnId
  u'table-number-1'

And let's ues this id as ``sortOn`` value:

  >>> sortingTable.sortOn = sortOnId

An important thing is to update the table after set an sort on value:

  >>> sortingTable.update()
  >>> print sortingTable.render()
  <table>
    <thead>
      <tr>
        <th>Title</th>
        <th>Number</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Title: Zero</td>
        <td>number: 0</td>
      </tr>
      <tr>
        <td>Title: First</td>
        <td>number: 1</td>
      </tr>
      <tr>
        <td>Title: Second</td>
        <td>number: 2</td>
      </tr>
      <tr>
        <td>Title: Third</td>
        <td>number: 3</td>
      </tr>
      <tr>
        <td>Title: Fourth</td>
        <td>number: 4</td>
      </tr>
    </tbody>
  </table>

We can also reverse the sort order:

  >>> sortingTable.sortOrder = 'reverse'
  >>> sortingTable.update()
  >>> print sortingTable.render()
  <table>
    <thead>
      <tr>
        <th>Title</th>
        <th>Number</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Title: Fourth</td>
        <td>number: 4</td>
      </tr>
      <tr>
        <td>Title: Third</td>
        <td>number: 3</td>
      </tr>
      <tr>
        <td>Title: Second</td>
        <td>number: 2</td>
      </tr>
      <tr>
        <td>Title: First</td>
        <td>number: 1</td>
      </tr>
      <tr>
        <td>Title: Zero</td>
        <td>number: 0</td>
      </tr>
    </tbody>
  </table>

The table implementation is also able to get the sort criteria given from a 
request. Let's setup such a request:

  >>> sorterRequest = TestRequest(form={'table-sortOn': 'table-number-1',
  ...                                   'table-sortOrder':'descending'})

and another time, update and render. As you can see the new table get sorted
by the second column and ordered in reverse order:

  >>> requestSortedTable = SortingTable(container, sorterRequest)
  >>> requestSortedTable.update()
  >>> print requestSortedTable.render()
  <table>
    <thead>
      <tr>
        <th>Title</th>
        <th>Number</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Title: Fourth</td>
        <td>number: 4</td>
      </tr>
      <tr>
        <td>Title: Third</td>
        <td>number: 3</td>
      </tr>
      <tr>
        <td>Title: Second</td>
        <td>number: 2</td>
      </tr>
      <tr>
        <td>Title: First</td>
        <td>number: 1</td>
      </tr>
      <tr>
        <td>Title: Zero</td>
        <td>number: 0</td>
      </tr>
    </tbody>
  </table>


Class based Table setup
-----------------------

There is a more elegant way to define table rows at class level. We offer 
a method which you can use if you need to define some columns called 
``addTable``. Before we define the table. let's define some cell renderer:

  >>> def headCellRenderer():
  ...     return u'My items'

  >>> def cellRenderer(item):
  ...     return u'%s item' % item.title

Now we can define our table and use the custom cell renderer:

  >>> class AddColumnTable(table.Table):
  ... 
  ...     cssClasses = {'table': 'table',
  ...                   'thead': 'thead',
  ...                   'tbody': 'tbody',
  ...                   'th': 'th',
  ...                   'tr': 'tr',
  ...                   'td': 'td'}
  ... 
  ...     cssClassEven = u'even'
  ...     cssClassOdd = u'odd'
  ... 
  ...     def setUpColumns(self):
  ...         return [
  ...             column.addColumn(self, TitleColumn, u'title',
  ...                              cellRenderer=cellRenderer,
  ...                              headCellRenderer=headCellRenderer,
  ...                              weight=1),
  ...             column.addColumn(self, SimpleColumn, name=u'simple',
  ...                              weight=2, header=u'The second column',
  ...                              cssClasses = {'th':'thCol', 'td':'tdCol'})
  ...             ]

  >>> addColumnTable = AddColumnTable(container, request)
  >>> addColumnTable.update()
  >>> print addColumnTable.render()
  <table class="table">
    <thead class="thead">
      <tr class="tr">
        <th class="th">My items</th>
        <th class="thCol th">The second column</th>
      </tr>
    </thead>
    <tbody class="tbody">
      <tr class="even tr">
        <td class="td">First item</td>
        <td class="tdCol td">First</td>
      </tr>
      <tr class="odd tr">
        <td class="td">Fourth item</td>
        <td class="tdCol td">Fourth</td>
      </tr>
      <tr class="even tr">
        <td class="td">Second item</td>
        <td class="tdCol td">Second</td>
      </tr>
      <tr class="odd tr">
        <td class="td">Third item</td>
        <td class="tdCol td">Third</td>
      </tr>
      <tr class="even tr">
        <td class="td">Zero item</td>
        <td class="tdCol td">Zero</td>
      </tr>
    </tbody>
  </table>

As you can see the table columns provide all attributes we set in the addColumn
method:

  >>> titleColumn = addColumnTable.rows[0][0][1]
  >>> titleColumn
  <TitleColumn u'title'>

  >>> titleColumn.__name__
  u'title'

  >>> titleColumn.__parent__
  <AddColumnTable None>

  >>> titleColumn.colspan
  0

  >>> titleColumn.weight
  1

  >>> titleColumn.header
  u''

  >>> titleColumn.cssClasses
  {}

and the second column

  >>> simpleColumn = addColumnTable.rows[0][1][1]
  >>> simpleColumn
  <SimpleColumn u'simple'>

  >>> simpleColumn.__name__
  u'simple'

  >>> simpleColumn.__parent__
  <AddColumnTable None>

  >>> simpleColumn.colspan
  0

  >>> simpleColumn.weight
  2

  >>> simpleColumn.header
  u'The second column'

  >>> simpleColumn.cssClasses
  {'td': 'tdCol', 'th': 'thCol'}


Batching
--------

Or table implements a concept for batching by default. If you set the attribute
``startBatchingAt`` to a size smaller then the rows generated based on the given
items, our table starts to generate a batch. Let's define a new Table:

  >>> class BatchingTable(table.Table):
  ... 
  ...     def setUpColumns(self):
  ...         return [
  ...             column.addColumn(self, TitleColumn, u'title',
  ...                              cellRenderer=cellRenderer,
  ...                              headCellRenderer=headCellRenderer,
  ...                              weight=1),
  ...             column.addColumn(self, NumberColumn, name=u'number',
  ...                              weight=2, header=u'Number')
  ...             ]

Now we can create our table:

  >>> batchingTable = BatchingTable(container, request)

And add some more items to our container:

  >>> container[u'sixt'] = Content('Sixt', 6)
  >>> container[u'seventh'] = Content('Seventh', 7)
  >>> container[u'eighth'] = Content('Eighth', 8)
  >>> container[u'ninth'] = Content('Ninth', 9)
  >>> container[u'tenth'] = Content('Tenth', 10)
  >>> container[u'eleventh'] = Content('Eleventh', 11)
  >>> container[u'twelfth '] = Content('Twelfth', 12)
  >>> container[u'thirteenth'] = Content('Thirteenth', 13)
  >>> container[u'fourteenth'] = Content('Fourteenth', 14)
  >>> container[u'fifteenth '] = Content('Fifteenth', 15)
  >>> container[u'sixteenth'] = Content('Sixteenth', 16)
  >>> container[u'seventeenth'] = Content('Seventeenth', 17)
  >>> container[u'eighteenth'] = Content('Eighteenth', 18)
  >>> container[u'nineteenth'] = Content('Nineteenth', 19)
  >>> container[u'twentieth'] = Content('Twentieth', 20)

Now let's show the full table without batching:

  >>> batchingTable.update()
  >>> print batchingTable.render()
  <table>
    <thead>
      <tr>
        <th>My items</th>
        <th>Number</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Eighteenth item</td>
        <td>number: 18</td>
      </tr>
      <tr>
        <td>Eighth item</td>
        <td>number: 8</td>
      </tr>
      <tr>
        <td>Eleventh item</td>
        <td>number: 11</td>
      </tr>
      <tr>
        <td>Fifteenth item</td>
        <td>number: 15</td>
      </tr>
      <tr>
        <td>First item</td>
        <td>number: 1</td>
      </tr>
      <tr>
        <td>Fourteenth item</td>
        <td>number: 14</td>
      </tr>
      <tr>
        <td>Fourth item</td>
        <td>number: 4</td>
      </tr>
      <tr>
        <td>Nineteenth item</td>
        <td>number: 19</td>
      </tr>
      <tr>
        <td>Ninth item</td>
        <td>number: 9</td>
      </tr>
      <tr>
        <td>Second item</td>
        <td>number: 2</td>
      </tr>
      <tr>
        <td>Seventeenth item</td>
        <td>number: 17</td>
      </tr>
      <tr>
        <td>Seventh item</td>
        <td>number: 7</td>
      </tr>
      <tr>
        <td>Sixt item</td>
        <td>number: 6</td>
      </tr>
      <tr>
        <td>Sixteenth item</td>
        <td>number: 16</td>
      </tr>
      <tr>
        <td>Tenth item</td>
        <td>number: 10</td>
      </tr>
      <tr>
        <td>Third item</td>
        <td>number: 3</td>
      </tr>
      <tr>
        <td>Thirteenth item</td>
        <td>number: 13</td>
      </tr>
      <tr>
        <td>Twelfth item</td>
        <td>number: 12</td>
      </tr>
      <tr>
        <td>Twentieth item</td>
        <td>number: 20</td>
      </tr>
      <tr>
        <td>Zero item</td>
        <td>number: 0</td>
      </tr>
    </tbody>
  </table>

As you can see, the table is not nice ordered and it uses all items. If we like
to use tha batch, we need to set the startBatchingAt size to a lower value then
it is set by default. The default value which a batch is used is set to ``50```:

  >>> batchingTable.startBatchingAt
  50

We will set the size to ``10`` for now:

  >>> batchingTable.startBatchingAt = 5
  >>> batchingTable.startBatchingAt
  5

There is also a ``batchSize`` value which we need to set to ``5``. By deault
the value get initialized by the ``batchSize`` value:

  >>> batchingTable.batchSize
  50

  >>> batchingTable.batchSize = 5
  >>> batchingTable.batchSize
  5

Now we can update and render the table again. But you will see that we only get
a table size of 5 rows whihc is correct. But the order doesn't depend on the 
numbers we see in cells:

  >>> batchingTable.update()
  >>> print batchingTable.render()
  <table>
    <thead>
      <tr>
        <th>My items</th>
        <th>Number</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Eighteenth item</td>
        <td>number: 18</td>
      </tr>
      <tr>
        <td>Eighth item</td>
        <td>number: 8</td>
      </tr>
      <tr>
        <td>Eleventh item</td>
        <td>number: 11</td>
      </tr>
      <tr>
        <td>Fifteenth item</td>
        <td>number: 15</td>
      </tr>
      <tr>
        <td>First item</td>
        <td>number: 1</td>
      </tr>
    </tbody>
  </table>

I think we should order the table by the second column before we show the next
batch values. We do this by simply set the ``defaultSortOn``:

  >>> batchingTable.sortOn = u'table-number-1'

Now we shuld see a nice ordered and batched table:

  >>> batchingTable.update()
  >>> print batchingTable.render()
  <table>
    <thead>
      <tr>
        <th>My items</th>
        <th>Number</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Zero item</td>
        <td>number: 0</td>
      </tr>
      <tr>
        <td>First item</td>
        <td>number: 1</td>
      </tr>
      <tr>
        <td>Second item</td>
        <td>number: 2</td>
      </tr>
      <tr>
        <td>Third item</td>
        <td>number: 3</td>
      </tr>
      <tr>
        <td>Fourth item</td>
        <td>number: 4</td>
      </tr>
    </tbody>
  </table>

The batch concept allows us to choose from all batches and render the rows
for this batched items. We can do this by set any batch as rows. as you can see
we have ``4`` batched row data available:

  >>> len(batchingTable.rows.batches)
  4

We can set such a batch as row values, then this batch data are used for 
rendering. But take care, if we update the table, our rows get overriden 
and reset to the previous values. this means you can set any bath as rows
data and only render them. This is possbile since the update method sorted all
items and all batch contain ready to use data. This concept could be important
if you need to cache batches etc. 

  >>> batchingTable.rows = batchingTable.rows.batches[1]
  >>> print batchingTable.render()
  <table>
    <thead>
      <tr>
        <th>My items</th>
        <th>Number</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Sixt item</td>
        <td>number: 6</td>
      </tr>
      <tr>
        <td>Seventh item</td>
        <td>number: 7</td>
      </tr>
      <tr>
        <td>Eighth item</td>
        <td>number: 8</td>
      </tr>
      <tr>
        <td>Ninth item</td>
        <td>number: 9</td>
      </tr>
      <tr>
        <td>Tenth item</td>
        <td>number: 10</td>
      </tr>
    </tbody>
  </table>

And like described above, if you call ``update`` our batch to rows setup get
reset:

  >>> batchingTable.update()
  >>> print batchingTable.render()
  <table>
    <thead>
      <tr>
        <th>My items</th>
        <th>Number</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Zero item</td>
        <td>number: 0</td>
      </tr>
      <tr>
        <td>First item</td>
        <td>number: 1</td>
      </tr>
      <tr>
        <td>Second item</td>
        <td>number: 2</td>
      </tr>
      <tr>
        <td>Third item</td>
        <td>number: 3</td>
      </tr>
      <tr>
        <td>Fourth item</td>
        <td>number: 4</td>
      </tr>
    </tbody>
  </table>

This means you can probably update all batches, cache them and use them alter.
but this is not usfull for normal usage in a page without an enhanced concept
which is not a part of this implementation. This also means, there must be 
another way to set the batch index. Yes there is, there are two other ways how
we can set the batch position. We can set a batch position by set the 
``batchStart`` value in our table or we can use a request variable. Let's show 
the first one first:

  >>> batchingTable.batchStart = 6
  >>> batchingTable.update()
  >>> print batchingTable.render()
  <table>
    <thead>
      <tr>
        <th>My items</th>
        <th>Number</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Seventh item</td>
        <td>number: 7</td>
      </tr>
      <tr>
        <td>Eighth item</td>
        <td>number: 8</td>
      </tr>
      <tr>
        <td>Ninth item</td>
        <td>number: 9</td>
      </tr>
      <tr>
        <td>Tenth item</td>
        <td>number: 10</td>
      </tr>
      <tr>
        <td>Eleventh item</td>
        <td>number: 11</td>
      </tr>
    </tbody>
  </table>

We can also set the batch position by using the batchStart value in a request.
Note that we need the table ``prefix`` and column ``__name__`` like we use in 
the sorting concept:

  >>> batchingRequest = TestRequest(form={'table-batchStart': '11',
  ...                                     'table-batchSize': '5',
  ...                                     'table-sortOn': 'table-number-1'})
  >>> requestBatchingTable = BatchingTable(container, batchingRequest)

Note; our table needs to start batching at smaller amount of items then we 
have by default otherwise we don't get a batch:

  >>> requestBatchingTable.startBatchingAt = 5
  >>> requestBatchingTable.update()
  >>> print requestBatchingTable.render()
  <table>
    <thead>
      <tr>
        <th>My items</th>
        <th>Number</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Twelfth item</td>
        <td>number: 12</td>
      </tr>
      <tr>
        <td>Thirteenth item</td>
        <td>number: 13</td>
      </tr>
      <tr>
        <td>Fourteenth item</td>
        <td>number: 14</td>
      </tr>
      <tr>
        <td>Fifteenth item</td>
        <td>number: 15</td>
      </tr>
      <tr>
        <td>Sixteenth item</td>
        <td>number: 16</td>
      </tr>
    </tbody>
  </table>
