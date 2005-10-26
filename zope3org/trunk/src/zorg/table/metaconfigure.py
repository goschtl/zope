from zope.configuration import config, xmlconfig, fields
from sets import Set,ImmutableSet
from zope.interface import implements
from zope.app.component.metaconfigure import utility
from zope.app.pagetemplate.engine import TrustedEngine
from logging import warn

from metadirectives import ITableConfigDirective,IColumnDirective
from table import TableConfig,Column,TableAction
from interfaces import ITableConfig,IColumn,ITableAction
from zope.component import provideUtility

def handler(colNames,sortBy,sortReverse,columns,name,actions):
    cols = []
    acts=[]
    for col in columns:
        cols.append(Column(*col))
    for act in actions:
        acts.append(act[2](*act[:2]))

    config = TableConfig(colNames=colNames,
                         sortBy=sortBy,
                         sortReverse=sortReverse,
                         columns=cols,
                         actions=acts)
    provideUtility(config,ITableConfig,name=name)
    

class TableConfigDirective(config.GroupingContextDecorator):
    
    implements(config.IConfigurationContext, ITableConfigDirective)

    engine = TrustedEngine
    
    def __init__(self,context,id,colNames=None,sortBy=None,sortReverse=None):
        super(TableConfigDirective,self).__init__(context,
                                                  id=id,
                                                  colNames=colNames,
                                                  sortBy=sortBy,
                                                  sortReverse=sortReverse)
        self.acts = []
        self.columns = []

    def after(self):
        self.action(discriminator=("tableconfig",self.id),
                    callable=handler,
                    args = (self.colNames,self.sortBy,
                            self.sortReverse,self.columns,
                            self.id,self.acts))

def columnHandler(context,schema,name,field=None,title=None):
    col = (schema,name,field,title)
    context.columns.append(col)

def actionHandler(context,name,title=None,class_=TableAction):
    act = (name,title,class_)
    context.acts.append(act)
