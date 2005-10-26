from zope.interface import Interface,implements
from zope.schema import TextLine,List,Bool,Object
from zope.schema.interfaces import IField
from zope.component import getMultiAdapter,queryUtility
from zope.interface.interfaces import IMethod

from interfaces import ITable,IColumn,ICell,IRow,ISorter
from interfaces import ITableAction,ITableConfig

class TableAction(object):

    implements(ITableAction)

    def __init__(self,name,title=None):
        self.name=name
        self.title = title or name

    def __call__(self,context):
        if ITable.providedBy(context):
            return self.applyToTable(context)
        if ITableConfig.providedBy(context):
            return self.applyToConfig(context)

    def applyToTable(self,table):
        pass

    def applyToConfig(self,config):
        pass
    

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
        self.sorter = getMultiAdapter((self.schema,self.field),ISorter)

class TableConfig(object):
    implements(ITableConfig)

    keep = object()
    all = object()
    colNames=[]
    columns={}
    selection = {}
    prefix = u'table.'
    action=None

    def __init__(self,colNames=None,sortBy=None,sortReverse=False,
                 columns=[],selection={},actions=[],action=None,
                 batchStart=0,batchSize=0):
        self.actions = {}
        self.batchStart=batchStart
        self.batchSize=batchSize
        self.sortBy = sortBy
        self.sortReverse = sortReverse
        self.selection = selection
        self.columns = {}
        if columns == self.keep:
            self.columns = columns
        else:
            for column in columns:
                self.columns[column.name]=column
        if colNames==None:
            self.colNames = self.columns.keys()
        else:
            self.colNames = colNames
        if actions == self.keep:
            self.actions = actions
        else:
            for act in actions:
                self.actions[act.name]=act
        if action:
            self.action=self.actions.get(action,None)
            self.action(self)


    def update(self,config):
        for attr in ['sortBy','sortReverse','columns',
                     'colNames','selection','actions','action',
                     'batchStart','batchSize']:
            v = getattr(config,attr)
            if not v is self.keep:
                setattr(self,attr,v)
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

        # actions
        self.actions=self.keep
        #actionName = request.form.get(self.prefix + u'action',None)
        #if actionName:
        #    # set it to none, so we call an action only once
        #    self.action = table.config.actions.get(actionName,None)
        #    self.action(self)


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
        if config.action:
            config.action(self)
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
            keys = (key for key,value in items)
        else:
            keys = self.context.keys()
        if self.config.batchSize>0:
            keys = keys[self.config.batchStart:self.config.batchEnd]
        for key in keys:
            yield self.getRow(key)

    def getPage(self):

        """returns the current page"""
        if self.config.batchSize<1:
            return 1
        
        
        

    def getColumns(self):

        return (self.config.columns[colName] for colName in self.config.colNames)



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
        
        
    
    
