import zope

import interfaces

class TableFormatter:
    def __init__(self, config, request, batch_start=0):
        self.config = config
        self.request = request
        self.batch_start = batch_start
        self.columns_by_title = dict([(col.title,col) for col in config.columns])

    def getVisibleColumns(self):
        return [self.columns_by_title[title] 
                for title in self.config.visible_columns]

    def renderTable(self, items):
        return ('<table>\n' + 
                self.renderHeaderRow() + '\n' + 
                self.renderRows(items) + '\n' +
                '</table>')

    def renderHeaderRow(self):
        return '<tr>' + self.renderHeaders() + '</tr>' 

    def renderHeaders(self):
        return ''.join(['<th>'+cell+'</th>' for cell in self.getHeaders()])

    def renderRows(self, items):
        rows = self.getRows(items)
        return '\n'.join(['<tr><td>' + '</td><td>'.join(cells) + '</td></tr>'
                          for cells in rows])

    def getHeaders(self):
        columns = self.getVisibleColumns()
        headers = []
        for column in columns:
            contents = column.renderHeader(self)
            if contents == None:
                contents = ''
            headers.append(str(contents))

        return headers
    
    def getRows(self, items):
        columns = self.getVisibleColumns()
        if self.config.sort_on:
            key_func = self.columns_by_title[self.config.sort_on].getSortKey
        else:
            key_func = lambda *args, **kws: None

        if self.config.batch_size == 0:
            batch_end = None
        else:
            batch_end = self.batch_start + self.config.batch_size

        rows = []
        for item in items:
            cells = []
            sort_key = key_func(item, self)
            for column in columns:
                contents = column.renderCell(item, self)
                if contents == None:
                    contents = ''
                cells.append(str(contents))
            rows.append((sort_key, cells))

        rows.sort()
        rows = [row[1] for row in rows]

        if self.config.sort_reverse:
            rows.reverse()
        
        rows = rows[self.batch_start:batch_end]
        return rows

class TableConfiguration:
    zope.interface.implements(interfaces.ITableConfiguration)
    sort_on = None
    sort_reverse = False
    batch_size = 0
    def __init__(self, columns):
        self.columns = columns
        self._visible_columns = None

    def visible_columns():
        def fget(self):
            if self._visible_columns == None:
                return tuple([col.title for col in self.columns])
            else:
                return self._visible_columns

        def fset(self, value):
            self._visible_columns = visible_columns

        return locals()

    visible_columns = property(**visible_columns())
