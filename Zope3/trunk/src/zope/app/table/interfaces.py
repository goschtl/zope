import zope.interface
import zope.schema

class ITableConfiguration(zope.interface.Interface):
    """Table column configuration schema."""

    columns = zope.schema.Tuple(
        title=u'All the columns that make up this table.',
        description=u'The names of columns to display in the table',
        required=True,
        unique=True,
        )

    visible_columns = zope.schema.List(
        title=u'Columns to display',
        description=u'The names of columns to display in the table',
        value_type=zope.schema.Choice(vocabulary='table_preference_columns'),
        required=True,
        unique=True,
        )

    sort_on = zope.schema.Choice(
        title=u'Sort on column',
        description=u'The name of the column to sort by',
        vocabulary='table_preference_columns',
        required=True,
        )

    sort_reverse = zope.schema.Bool(
        title=u'Reverse sort',
        description=u'Set to sort in reverse',
        required=True,
        default=False,
        )

    batch_size = zope.schema.Int(
        title=u'Number of rows per page',
        description=u'The number of rows to show at a time.  '
                    u'Set to 0 for no batching.',
        required=False,
        default=20,
        min=0,
        )


class IColumn(zope.interface.Interface):

    title = zope.schema.TextLine(
        title=u'Title',
        description=u'The title of the column, usually displayed in the table',
        required=True,
        )

    sortable = zope.schema.Bool(
        title=u'Sortable',
        description=u'Is this column sortable.',
        required=True,
        default=True,
        )

    def renderHeader(formatter):
        """Renders a table header.

        'formatter' - The ITableFormatter that is using the IColumn.

        Returns html_fragment.
        """

    def renderCell(item, formatter):
        """Renders a table cell.

        'item' - the object on this row. 
        'formatter' - The ITableFormatter that is using the IColumn.

        Returns html_fragment.
        """

    def getSortKey(item, formatter):
        """Identify the value used to sort an item.
        
        'item' - the object on this row. 
        'formatter' - The ITableFormatter that is using the IColumn.

        Returns sort_key
        """
