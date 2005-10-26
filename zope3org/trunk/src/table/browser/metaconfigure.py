import os
import zope

from zope.configuration import config, xmlconfig, fields
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.interface import implements
from zope.app.component.metaconfigure import utility
from zope.app.pagetemplate.engine import TrustedEngine
from zope.configuration.exceptions import ConfigurationError

from table.interfaces import ICell,IRow

from interfaces import ITableView,ICellView,IRowView
from views import SimpleTableViewClass
from views import TableView,CellView,RowView
from metadirectives import ITableViewDirective
from metadirectives import ICellViewDirective,IRowViewDirective

class CommonInformation(config.GroupingContextDecorator):

    implements(config.IConfigurationContext)
    engine = TrustedEngine
    view = None
    default_template=None
    class_ = None
    template = None
    layer = IDefaultBrowserLayer

    def _normalize(self):
        if self.class_ is None:
            self.bases = (self.view,)
        else:
            self.bases = (self.class_, self.view)

        if self.template is not None:
            self.template = os.path.abspath(str(self.template))
            if not os.path.isfile(self.template):
                raise ConfigurationError("No such file", self.template)
        else:
            self.template = self.default_template


class TableViewDirective(CommonInformation):
    
    implements(ITableViewDirective)
    view = TableView
    default_template='table.pt'

    
    def __init__(self,context,name,config,for_,class_=None,template=None,
                 permission=None,layer=None):
        super(TableViewDirective,self).__init__(context,
                                                name=name or u'',
                                                config=config,
                                                for_=for_,
                                                class_=class_,
                                                template=template,
                                                layer=layer,
                                                permission=permission)

        self._normalize()

    def after(self):

        attributes = {'configId':self.config}
        factory = SimpleTableViewClass(self.template,
                                       bases=self.bases,
                                       name=self.name,
                                       attributes=attributes
                                       )
        zope.app.component.metaconfigure.view(self.context,
                                              [factory],
                                              IBrowserRequest,
                                              self.name or u'',
                                              [self.for_],
                                              layer=self.layer,
                                              permission = self.permission,
                                              provides=ITableView
                                              )


class CellViewDirective(CommonInformation):
    
    implements(ICellViewDirective)

    view = CellView
    default_template='cell.pt'
    
    def __init__(self,context,name,for_,class_=None,template=None,
                 permission=None,layer=None,field=None,schema=None,
                 useForm=False):
        super(CellViewDirective,self).__init__(context,
                                               name=name or u'',
                                               for_=for_,
                                               class_=class_,
                                               template=template,
                                               layer=layer,
                                               permission=permission,
                                               useForm=useForm,
                                               field=field,
                                               schema=schema)
        self._normalize()            

    def after(self):

        attributes = {
            'useForm':self.useForm,
            'field':self.field,
            'schema':self.schema
            }
        factory = SimpleTableViewClass(self.template,
                                       bases=self.bases,
                                       name=self.name,
                                       attributes=attributes
                                       )
        zope.app.component.metaconfigure.view(self.context,
                                              [factory],
                                              IBrowserRequest,
                                              self.name,
                                              [self.for_,ICell],
                                              layer=self.layer,
                                              permission = self.permission,
                                              provides=ICellView
                                              )

class RowViewDirective(CommonInformation):
    
    implements(IRowViewDirective)

    view = RowView
    default_template='row.pt'
    
    def __init__(self,context,name,for_,class_=None,template=None,
                 permission=None,layer=None):

        super(RowViewDirective,self).__init__(context,
                                               name=name or u'',
                                               for_=for_,
                                               class_=class_,
                                               template=template,
                                               layer=layer,
                                               permission=permission)
        self._normalize()            

    def after(self):

        factory = SimpleTableViewClass(self.template,
                                       bases=self.bases,
                                       name=self.name
                                       )
        zope.app.component.metaconfigure.view(self.context,
                                              [factory],
                                              IBrowserRequest,
                                              self.name,
                                              [self.for_,IRow],
                                              layer=self.layer,
                                              permission = self.permission,
                                              provides=IRowView
                                              )
