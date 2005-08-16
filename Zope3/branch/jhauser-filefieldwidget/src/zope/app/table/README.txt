======
Tables
======

Tables are general purpose UI constructs designed to simplify presenting
tabular information.  A table has a column set which collects columns and
manages configuration data.


Columns
=======

``Columns`` have methods to render a header and the contents of a cell based on
the item that occupies that cell.  They also provide the ability to retrieve
the sort key for a particular item::

    >>> import zope.interface 
    >>> from zope.app.table.interfaces import IColumn
    >>> class GetItemColumn:
    ...     zope.interface.implements(IColumn)
    ...     def __init__(self, title, attr, sortable=True):
    ...         self.title = title
    ...         self.sortable = sortable
    ...         self.attr = attr # This isn't part of IColumn
    ...     def renderHeader(self, formatter):
    ...         return self.title
    ...     def renderCell(self, item, formatter):
    ...         return str(getattr(item, self.attr))
    ...     def getSortKey(self, item, formatter):
    ...         return str(getattr(item, self.attr))
    
Note that the methods are required to provide the <th> and <td> tags.  This
provides the flexability for columns to provide other wrapping tags when
neccesary.

Let's create some columns that we'll use later::

    >>> columns = (
    ...     GetItemColumn('First', 'a'),
    ...     GetItemColumn('Second', 'b'),
    ...     GetItemColumn('Third', 'c'),
    ...     )


Table Configuration
===================

When a table is rendered its display is modified with the use of a
configuration object.  Such objects must conform to ITableConfiguration::

    >>> from zope.app.table.interfaces import ITableConfiguration
    >>> class MyTableConfiguration:
    ...     zope.interface.implements(ITableConfiguration)
    ...     visible_columns = ('First', 'Third')
    ...     sort_on = None
    ...     sort_reverse = False
    ...     batch_size = 10
    ...     def __init__(self, columns):
    ...         self.columns = columns
    >>> config = MyTableConfiguration(columns)


Table Formatters
================

When a sequence of objects are to be turned into an HTML table, a ``Table
Formatter`` is used. 

    >>> from zope.app.table import TableFormatter
    >>> context = {}
    >>> formatter = TableFormatter(config, context)

We need some data to format::

    >>> class DataItem:
    ...     def __init__(self, a, b, c):
    ...         self.a = a
    ...         self.b = b
    ...         self.c = c

    >>> items = [DataItem('a0', 'b0', 'c0'), DataItem('a1', 'b1', 'c1')]

The simplest way to use one is to call the ``render`` method::

    >>> print formatter.renderTable(items)
    <table>
    <tr><th>First</th><th>Third</th></tr>
    <tr><td>a0</td><td>c0</td></tr>
    <tr><td>a1</td><td>c1</td></tr>
    </table>

If you want more control over the output there are other methods you can use::

    >>> html = '<table class="my_class">\n'
    >>> html += '<tr class="header">'+ formatter.renderHeaders() + '</tr>\n'
    >>> for index, row in enumerate(formatter.getRows(items)):
    ...     if index % 2:
    ...         html += '<tr class="even">'
    ...     else:
    ...         html += '<tr class="odd">'
    ...     for index, cell in enumerate(row):
    ...         if index == 0:
    ...             html += '<td class="first_column">'
    ...         else:
    ...             html += '<td>'
    ...         html += cell + '<td>'
    ...     html += '</tr>\n'
    >>> html += '</table>'
    >>> print html
    <table class="my_class">
    <tr class="header"><th>First</th><th>Third</th></tr>
    <tr class="odd"><td class="first_column">a0<td><td>c0<td></tr>
    <tr class="even"><td class="first_column">a1<td><td>c1<td></tr>
    </table>


Batching
========

``TableFormatter`` instances can also batch.

    >>> config.batch_size = 1
    >>> print formatter.renderTable(items)
    <table>
    <tr><th>First</th><th>Third</th></tr>
    <tr><td>a0</td><td>c0</td></tr>
    </table>

To specify a starting point, just pass it in when creating the formatter::

    >>> batchingFormatter = TableFormatter(config, formatter, batch_start=1)
    >>> print batchingFormatter.renderTable(items)
    <table>
    <tr><th>First</th><th>Third</th></tr>
    <tr><td>a1</td><td>c1</td></tr>
    </table>


Sorting
=======

``TableFormatter`` instances can be configured to sort their output. 

    >>> config = MyTableConfiguration(columns)
    >>> config.sort_on = 'Second'
    >>> config.sort_reverse = True
    >>> formatter = TableFormatter(config, context)
    >>> print formatter.renderTable(items)
    <table>
    <tr><th>First</th><th>Third</th></tr>
    <tr><td>a1</td><td>c1</td></tr>
    <tr><td>a0</td><td>c0</td></tr>
    </table>

When batching sorted tables, the sorting is applied first, then the batching::

    >>> config = MyTableConfiguration(columns)
    >>> config.sort_on = 'Second'
    >>> config.sort_reverse = True
    >>> formatter = TableFormatter(config, context, batch_start=1)
    >>> print formatter.renderTable(items*2)
    <table>
    <tr><th>First</th><th>Third</th></tr>
    <tr><td>a1</td><td>c1</td></tr>
    <tr><td>a0</td><td>c0</td></tr>
    <tr><td>a0</td><td>c0</td></tr>
    </table>


Fancy Columns
=============

It is easy to make columns be more sophisticated.  For example, if we wanted
a column that held content that was especially wide, we could do this::

    >>> class WideColumn(GetItemColumn):
    ...     def renderHeader(self, formatter):
    ...         return '<div style="width:200px">%s</div>' % self.title
    >>> columns = [
    ...     WideColumn('First', 'a'),
    ...     GetItemColumn('Second', 'b'),
    ...     GetItemColumn('Third', 'c'),
    ...     ]
    >>> config = MyTableConfiguration(columns)
    >>> formatter = TableFormatter(config, context)
    >>> print formatter.renderTable(items)
    <table>
    <tr><th><div style="width:200px">First</div></th><th>Third</th></tr>
    <tr><td>a0</td><td>c0</td></tr>
    <tr><td>a1</td><td>c1</td></tr>
    </table>

This level of control over the way columns are rendered allows for creating
advanced column types (e.g. sorted columns with clickable headers).

