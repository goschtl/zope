
from zope.interface import implements

from zope.component import provideUtility
from zope.configuration import config, xmlconfig, fields
from zope.security.checker import InterfaceChecker

from zope.app.component.metaconfigure import handler, utility, proxify
from zope.app.pagetemplate.engine import TrustedEngine

from metadirectives import ITableConfigDirective,IColumnDirective
from table import TableConfig, Column, Action, Filter
from interfaces import ITableConfig, IAction, IFilter


def handler(colNames,sortBy,sortReverse,batchSize,columns,name,actions,filters):

    cols = []
    acts = []
    filts = []

    for col in columns:
        cols.append(Column(*col))

    for act in actions:
        action = Action(*act)
        if action.permission is not None:
            checker = InterfaceChecker(IAction, action.permission)
            action = proxify(action, checker)
        acts.append(action)

    for filt in filters:
        filter = Filter(*filt)
        if filter.permission is not None:
            checker = InterfaceChecker(IFilter, filter.permission)
            filter = proxify(filter, checker)
        filts.append(filter)

    config = TableConfig(colNames=colNames,
                         sortBy=sortBy,
                         sortReverse=sortReverse,
                         batchSize=batchSize,
                         columns=cols,
                         actions=acts,
                         filters=filts)

    provideUtility(config,ITableConfig,name=name)
    

class TableConfigDirective(config.GroupingContextDecorator):
    
    implements(config.IConfigurationContext, ITableConfigDirective)

    engine = TrustedEngine
    
    def __init__(self,context,id,colNames=None,sortBy=None,
                 sortReverse=None,batchSize=0):

        super(TableConfigDirective,self).__init__(context,
                                                  id=id,
                                                  colNames=colNames,
                                                  sortBy=sortBy,
                                                  sortReverse=sortReverse,
                                                  batchSize=batchSize)
        
        self.acts = []
        self.columns = []
        self.filters = []
                   
    def after(self):
        self.action(discriminator=("tableconfig",self.id),
                    callable=handler,
                    args = (self.colNames,self.sortBy,
                            self.sortReverse,self.batchSize,self.columns,
                            self.id,self.acts,self.filters))


def columnHandler(context,schema,name,field=None,title=None):
    col = (schema, name, field, title)
    context.columns.append(col)


def actionHandler(context,name,permission=None,label=None,forRow=False):
    act = (name, permission, label, forRow)
    context.acts.append(act)


def filterHandler(context,name,permission=None):
    filter = (name, permission)
    context.filters.append(filter)
