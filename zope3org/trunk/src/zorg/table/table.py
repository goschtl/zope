
from zope.interface import Interface,implements
from zope.interface.interfaces import IMethod

from zope.component import getMultiAdapter,getAdapter,queryUtility

from zope.security import checkPermission
from zope.security.checker import CheckerPublic

from zope.schema import TextLine,List,Bool,Object
from zope.schema.interfaces import IField

from interfaces import ITable, IColumn, ICell, IRow, ISorter
from interfaces import IAction, IFilter, ITableConfig, ITableAction, ITableFilter


class Action(object):

    implements(IAction)

    def __init__(self,name,permission=None,label=None,forRow=False):
        self.name = name
        if permission == 'zope.Public':
            self.permission = CheckerPublic
        else:
            self.permission = permission
        self.label = label or name
        self.forRow = forRow


class Filter(object):

    implements(IFilter)

    def __init__(self,name,permission=None):
        self.name = name
        if permission == 'zope.Public':
            self.permission = CheckerPublic
        else:
            self.permission = permission
#        self.filter = getMultiAdapter((self.schema,self.field),IFilter)

class Column(object):

    implements(IColumn)

    def __init__(self,schema,name,field=None,title=None):
        self.schema = schema
        self.name = name
        if field is None:
            self.field = self.schema[self.name]
        else:
            self.field = self.schema[field]
        self.title = title or getattr(self.field,'title',None) or self.name
#        print "getMultiAdapter((%s,%s),ISorter)" % (self.schema,self.field)
        self.sorter = getMultiAdapter((self.schema,self.field),ISorter)


class TableConfig(object):

    implements(ITableConfig)

    keep = object()
    all = object()
    colNames = []
    columns = {}
    actions = {}
    filters = {}
    selection = {}
    prefix = u'table.'

    def __init__(self,colNames=None,sortBy=None,sortReverse=False,
                 batchSize=0,columns=[],selection={},actions={},filters={},
                 action=None,batchStart=0):
        self.batchStart = batchStart
        self.batchSize = batchSize
        self.sortBy = sortBy
        self.sortReverse = sortReverse
        self.selection = selection
        self.columns = {}
        if columns == self.keep:
            self.columns = columns
        else:
            for column in columns:
                self.columns[column.name]=column
        if colNames == None:
            self.colNames = self.columns.keys()
        else:
            self.colNames = colNames
        self.actions = {}
        if actions == self.keep:
            self.actions = actions
        else:
            for act in actions:
                self.actions[act.name]=act
        self.filters = {}
        if filters == self.keep:
            self.filters = filters
        else:
            for filter in filters:
                self.filters[filter.name]=filter

    def update(self,config):
        for attr in ['sortBy','sortReverse','columns',
                     'colNames','selection','actions',
                     'filters','batchStart','batchSize']:
            v = getattr(config,attr)
            if not v is self.keep:
                setattr(self,attr,v)
        self.batchStart = int(self.batchStart)
        self.batchSize = int(self.batchSize)
        if self.colNames == None:
            self.colNames = self.columns.keys()

    def isSelected(self,obj):
        if IRow.providedBy(obj):
            row = obj.key
            cols = [self.all]
        else:
            row,col = obj.key
            cols = [self.all,col]
        for key in cols:
            colSel = self.selection.get(key,None)
            if colSel==None: continue
            if colSel==self.all or row in colSel:
                return True
        return False

    def setBatchInfo(self,rc):
        """sets the page, pages, batchStart, batchEnd values by the
        use of the rowCount"""
        if self.batchSize>0:
            self.batchStart = min(rc,self.batchStart)
            self.batchEnd = min(rc,self.batchStart+self.batchSize)
            self.page = self.batchStart/self.batchSize +1
            self.pages = rc/self.batchSize
            if self.pages*self.batchSize<rc:
                self.pages = self.pages +1
        else:
            self.batchEnd = 0
            self.pages = 1
            self.page = 1

    def availableActions(self, context):
        result = {}
        for name, act in self.actions.items():
            permission = act.permission
            if permission is not None:
                if not checkPermission(permission, context):
                    continue
            result[name] = act
        return result

    def availableFilters(self, context):
        result = {}
        for name, filter in self.filters.items():
            permission = filter.permission
            if permission is not None:
                if not checkPermission(permission, context):
                    continue
            result[name] = filter
        return result

            
class RequestTableConfig(TableConfig):

    def __init__(self,table,request):
        self.request = request
        self.prefix = table.config.prefix
        self.batchStart = request.form.get(self.prefix + u'batchStart',
                                         self.keep)
        self.batchSize = request.form.get(self.prefix + u'batchSize',
                                         self.keep)
        self.colNames = request.form.get(self.prefix + u'colNames',
                                         self.keep)
        self.sortBy = request.form.get(self.prefix + u'sortBy',
                                       self.keep)
        if self.request.form.has_key(self.prefix + u'sortReverse'):
            self.sortReverse = self.request.get(
                self.prefix + u'sortReverse') == u'True'
        else:
            self.sortReverse = self.keep
        self.columns = self.keep
        selectedRows = request.form.get(self.prefix + u'selection',[])
        if selectedRows:
            self.selection = {self.all:selectedRows}
        self.actions=self.keep
        self.filters=self.keep


class ReadMappingTable(object):
    
    implements(ITable)

    def __init__(self,context,name=None,config=None):
        self.context = self.__parent__ = context
        self.name = name
        if config:
            self.applyConfig(config)
        else:
            self.config = TableConfig()

    def applyConfig(self,config):
        self.config.update(config)
        if self.name:
            self.config.prefix = "table." + self.name + "."
        self.config.setBatchInfo(len(self.context))

    def getRow(self,key):
        value = self.context[key]
        row = getMultiAdapter((value,self.context,self),IRow)
        row.key = key
        row.selected = self.config.isSelected(row)
        return row

    def getRows(self):
        sorter = None
        if self.config.sortBy:
            sortCol = self.config.columns[self.config.sortBy]
            sorter = sortCol.sorter
        if sorter:
            items = sorter.sort(self.context.items())
            if self.config.sortReverse:
                items.reverse()
            keys = []
            for key,value in items:
                keys.append(key)
        else:
            keys = self.context.keys()
        if self.config.batchSize>0:
            keys = keys[self.config.batchStart:self.config.batchEnd]
        for key in keys:
            yield self.getRow(key)

    def getColumns(self):
        return (self.config.columns[colName] for colName in self.config.colNames)

    def getActions(self, actions=None):
        result = {}
        for act in actions.values():
            if act.forRow:
                continue
            result[act.label] = \
                getMultiAdapter((act,self.context,self),ITableAction)
        return result

    def getFilters(self, filters=None):
        result = {}
        for filter in filters.values():
            result[filter.name] = \
                getMultiAdapter((filter,self.context,self),ITableFilter)
        return result



class SimpleCell(object):

    implements(ICell)
    selected=False
    
    def __init__(self,context,column,row,table):
        self.column = column
        self.row = row
        self.table = table
        self.context = context
        self.key = None

    def __call__(self):
        raise NotImplementedError


class SchemaCell(SimpleCell):

    def __init__(self,context,column,row,table):
        super(SchemaCell,self).__init__(context,column,row,table)
        
    def __call__(self):
        o = self.column.schema(self.context)
        if IMethod.providedBy(self.column.field):
            return getattr(o,self.column.field.__name__)()
        field=self.column.field.bind(o)
        v = field.get(o)
        return v


class Row(object):
    
    implements(IRow)
    
    selected=False
    
    def __init__(self,context,container,table):
        self.container=container
        self.table = table
        self.context=context

    def getCells(self):
        for column in self.table.getColumns():
            cell =  getMultiAdapter((self.context,column,self,
                                     self.table),ICell)
            cell.key = (self.key,column.name)
            cell.selected = self.table.config.isSelected(cell)
            yield cell

    def getActions(self):
        result = {}
        for act in self.table.config.actions.values():
            if act.forRow:
                result[act.label] = \
                    getMultiAdapter((act,self.container,self.table),ITableAction)
        return result


class TableAction(object):
    
    implements(ITableAction)
    
    def __init__(self,action,container,table):
        self.container = container
        self.table = table
        self.action = action
        self.name = action.name
        self.label = action.label
    

class TableFilter(object):
    
    implements(ITableFilter)
    
    def __init__(self,filter,container,table):
        self.container = container
        self.table = table
        self.filter = filter
        self.name = filter.name
