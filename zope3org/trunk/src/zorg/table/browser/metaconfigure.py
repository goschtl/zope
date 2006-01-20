import os
import zope


from zope.configuration import config, xmlconfig, fields
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.interface import implements, Interface
from zope.app.component.metaconfigure import utility
from zope.app.component import metaconfigure
from zope.app.publisher.browser import viewmeta
from zope.app.publisher.interfaces.browser import IBrowserView
from zope.app.pagetemplate.engine import TrustedEngine
from zope.configuration.exceptions import ConfigurationError
from zope.security import checker
from zope.security.checker import CheckerPublic

from zorg.table.interfaces import ICell, IRow, ITableAction, ITableFilter

from interfaces import ITableView, ICellView, IRowView, IActionView, IFilterView

from views import TableView, CellView, RowView, ActionView, FilterView
from views import SimpleTableViewClass

from metadirectives import ITableViewDirective
from metadirectives import ICellViewDirective, IRowViewDirective
from metadirectives import IActionViewDirective, IFilterViewDirective


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
                 useForm=False,widget=None):
        super(CellViewDirective,self).__init__(context,
                                               name=name or u'',
                                               for_=for_,
                                               class_=class_,
                                               template=template,
                                               layer=layer,
                                               permission=permission,
                                               useForm=useForm,
                                               field=field,
                                               schema=schema,
                                               widget=widget)
        self._normalize()           

    def after(self):

        attributes = {
            'useForm':self.useForm,
            'field':self.field,
            'schema':self.schema,
            'widget':self.widget
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

                                              
class ActionViewDirective(CommonInformation):
    
    implements(IActionViewDirective)

    view = ActionView
    default_template='action.pt'
    
    def __init__(self,context,name,for_,class_=None,template=None,
                 permission=None,layer=None,useForm=True,display=u"Bottom"):

        super(ActionViewDirective,self).__init__(context,
                                                 name=name or u'',
                                                 for_=for_,
                                                 class_=class_,
                                                 template=template,
                                                 layer=layer,
                                                 permission=permission,
                                                 useForm=useForm,
                                                 display=display)
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
                                              [self.for_,ITableAction],
                                              layer=self.layer,
                                              permission = self.permission,
                                              provides=IActionView
                                              )

                                             
class FilterViewDirective(CommonInformation):
    
    implements(IFilterViewDirective)

    view = FilterView
    default_template='filter.pt'
    
    def __init__(self,context,name,for_,class_=None,template=None,
                 permission=None,layer=None):

        super(FilterViewDirective,self).__init__(context,
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
                                              [self.for_,ITableFilter],
                                              layer=self.layer,
                                              permission = self.permission,
                                              provides=IFilterView
                                              )
