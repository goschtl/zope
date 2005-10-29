======
Tables
======

The table package provides tabular data handling by using schema information.

    >>> from zope.interface import Interface
    >>> from zope.interface.common.mapping import IReadMapping
    >>> from zope.app.testing import ztapi
    >>> from zope.app import zapi

    First we import some Test classes

    >>> from zorg.table.testing import ISimple,Simple,Container
    >>> container = Container()
    >>> for i in range(5):
    ...     container[unicode(i)] = Simple(u'name %s ' % i,4-i)

    The container objects implements IReadMapping

    >>> IReadMapping.providedBy(container)
    True

    >>> sorted(container.keys())
    [u'0', u'1', u'2', u'3', u'4']

    >>> print container.values()
    [<zorg.table.testing.Simple object at ...>]

    XXX The ITableConfig utility registration should be done in zcml.

    >>> from zorg.table.table import Column,TableConfig
    >>> from zorg.table.interfaces import ITable,ITableConfig
    >>> colName = Column(ISimple,u'name')
    >>> colPriority = Column(ISimple,u'priority')
    >>> config = TableConfig(columns=[colName,colPriority])
    >>> ztapi.provideUtility(ITableConfig,config,u'simple.config')

    We get our config as a named utility

    >>> config = zapi.getUtility(ITableConfig,u'simple.config')
    >>> print config
    <zorg.table.table.TableConfig object at ...>

    Now let's instantiate a table with the given config. There is
    already a registered table for IReadMapping, so we can adapt a
    table.

    >>> table = ITable(container)
    >>> print table
    <zorg.table.table.ReadMappingTable object at ...>

    Now we have an unconfigured table which has no columns etc.

    >>> print list(table.getColumns())
    []

    We have to apply the config to it ...

    >>> table.applyConfig(config)
    >>> print list(table.getColumns())
    [<zorg.table.table.Column object at ...>, <zorg.table.tab...>]

    Sorting by the 'name' attribute

    >>> table.config.sortBy = u'name'
    >>> print list(row.context.name for row in table.getRows())
    [u'name 0 ', u'name 1 ', u'name 2 ', u'name 3 ', u'name 4 ']

    Reverse sorting

    >>> table.config.sortReverse = True
    >>> print list(row.context.name for row in table.getRows())
    [u'name 4 ', u'name 3 ', u'name 2 ', u'name 1 ', u'name 0 ']

    Sort by 'priority' attribute

    >>> table.config.sortBy = u'priority'
    >>> print list(row.context.priority for row in table.getRows())
    [4, 3, 2, 1, 0]

    Note that the above result is still reverse, because of the config
    'sortReverse' attribute

    >>> table.config.sortReverse is  True
    True

    >>> rows = list(table.getRows())
    >>> len(rows)
    5

    By default cell instances are callable and return the actual value
    of the cell when called

    >>> for row in table.getRows():
    ...     print list(cell() for cell in row.getCells())
    [4, u'name 0 ']
    [3, u'name 1 ']
    [2, u'name 2 ']
    [1, u'name 3 ']
    [0, u'name 4 ']

    With the 'colNames' attribute we can change the visibility of
    columns.

    >>> table.config.colNames = [u'priority']
    >>> for row in table.getRows():
    ...     print list(cell() for cell in row.getCells())
    [4]
    [3]
    [2]
    [1]
    [0]

    Each row in a table has a unique key in the container.

    >>> print list(row.key for row in table.getRows())
    [u'0', u'1', u'2', u'3', u'4']

    Note that in the above result, the keys are provided by the
    container, not the row itself.

Selectons on Tables

    Table configurations can also hold information about which cells
    are selected. This can then be used to apply a specific action to
    cells which are selected.

    Selections can be provided as a dictionary in the format
    columnName:[rowKeys]. So if we want to select the 'name' column of
    the rows with the keys 1,2 it has to be defined like this: 

    >>> selection = ({u'name':[u'1',u'2']})
    >>> 
    >>> config = TableConfig(columns=[colName,colPriority],
    ...                      selection=selection)
    >>> config.selection
    {u'name': [u'1', u'2']}

    When we now apply the config we have those 2 cells selected

    >>> table.applyConfig(config)
    >>> for row in table.getRows():
    ...     print row.key,
    ...     print list(cell.selected for cell in row.getCells())
    1 [False, True]
    0 [False, False]
    3 [False, False]
    2 [False, True]
    4 [False, False]

    We can also select whole rows by providing the special all
    attribute of the config as key:
    >>> table.config.selection={table.config.all:[u'3',u'4']}
    >>> for row in table.getRows():
    ...     print row.key,
    ...     print list(cell.selected for cell in row.getCells())
    1 [False, False]
    0 [False, False]
    3 [True, True]
    2 [False, False]
    4 [True, True]

    Rows also have a selected attribute which is true if all cells in
    it are selected.
    >>> list((row.key,row.selected) for row in table.getRows())
    [(u'1', False), (u'0', False), (u'3', True), (u'2', False), (u'4', True)]

    The same applies to cols:

    >>> table.config.selection={u'priority':table.config.all}
    >>> for row in table.getRows():
    ...     print row.key,
    ...     print list(cell.selected for cell in row.getCells())
    1 [True, False]
    0 [True, False]
    3 [True, False]
    2 [True, False]
    4 [True, False]
    
Batching

    Batching rows is also defined in the table config by the use of
    batchStart and batchSize. batchStart is an index starting by
    0 defining the first shown row. and batchSize defines how much
    rows are returned. After each change to the batching attributes we
    have to reapply the config to the table. In order for batchEnd
    etc. to get computed.

    >>> table.config.batchStart = 3
    >>> table.applyConfig(table.config)
    >>> list(row.key for row in table.getRows())
    [u'1', u'0', u'3', u'2', u'4']

Batching is only done if the batchSize is greater than 0. The default
is 0. So let's change this to 2.


    >>> table.config.batchSize=2
    >>> table.applyConfig(table.config)
    >>> list(row.key for row in table.getRows())
    [u'2', u'4']


    >>> table.config.batchStart=2
    >>> table.applyConfig(table.config)
    >>> list(row.key for row in table.getRows())
    [u'3', u'2']

    >>> table.config.batchEnd
    4
    >>> table.config.page
    2
    >>> table.config.pages
    3
    >>> table.config.batchSize=4
    >>> table.applyConfig(table.config)
    >>> table.config.pages
    2

    batchEnd is at most the count of rows

    >>> table.config.batchEnd
    5
    
