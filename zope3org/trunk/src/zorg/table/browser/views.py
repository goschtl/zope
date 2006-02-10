
import sys

from zope.interface import Interface, implements
from zope.interface.interfaces import IMethod
from zope.schema.interfaces import IField
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.security.checker import defineChecker, NamesChecker

from zope.app import zapi
from zope.app.publisher.browser import BrowserView
from zope.app.pagetemplate.simpleviewclass import SimpleViewClass
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.form.interfaces import IDisplayWidget, IInputWidget
from zope.app.form.utility import setUpWidget

from zorg.table.interfaces import ITable,ITableConfig
from interfaces import ITableView,IRowView,ICellView,IActionView,IFilterView
from interfaces import ITableForm


class TableView(BrowserView):

    implements(ITableView)

    template = ViewPageTemplateFile('table.pt')
    configId=u''
    formClass = None
    
    def __init__(self, context, request):
        super(TableView, self).__init__(context, request)
        self.table = ITable(self.context)
        self.table.name = self.__name__ or u''
        config = zapi.getUtility(ITableConfig,self.configId)
        self.table.applyConfig(config)
        requestConfig = zapi.getMultiAdapter((self.table,request),
                                             ITableConfig)
        self.table.applyConfig(requestConfig)
        if self.formClass:
            self.table.form = self.formClass(self)
#            self.table.form.update()
        else:
            self.table.form = None

    def update(self):
        if self.formClass:
            self.table.form.update()

    def hasTableResult(self):
        return self.formClass and (self.table.form.form_result is not None)
    
    def render(self,*args,**kw):
        if self.formClass:
            if self.table.form.form_result is None:
                return self.template(*args,**kw)
            else:
                # hand over form_result (data and manipulation of response)
                return self.table.form.form_result
        else:
            return self.template(*args,**kw)
        
    def __call__(self,*args,**kw):
        self.update()
        self.render(*args,**kw)

    def getActionsBase(self, formActions=None):
        """get (specific) available actions of table."""
        if self.table.form is None:
            return []
        
        result = []
        actions = self.table.getActions(
                        self.table.config.availableActions(self.context)
                        )
        formActions = self.table.form.availableActions(formActions)            
        for formAction in formActions:
            if not formAction.label in actions:
                continue
            action = actions[formAction.label]
            adapt = zapi.queryMultiAdapter(
                      (self.context,action,self.request),
                      IActionView,name=action.name
                      )
            if adapt == None:
                adapt = zapi.getMultiAdapter(
                          (self.context,action,self.request),
                           IActionView,name=u""
                          )
            adapt.setPrefix(formAction.__name__)
            result.append(adapt)
        return result

    def getActions(self):
        """get all available actions of table."""
        return self.getActionsBase()

    def getFilters(self):
        """get all available filters of table."""
        result = []
        filters = self.table.getFilters(
                        self.table.config.availableFilters(self.context)
                        )
        for name, filter in filters.items():
            adapt = zapi.queryMultiAdapter(
                      (self.context,filter,self.request),
                      IFilterView,name=name
                      )
            if adapt == None:
                adapt = zapi.getMultiAdapter(
                          (self.context,filter,self.request),
                           IFilterView,name=u""
                          )
            result.append(adapt)
        return result        

    def getRows(self):
        """get objects of table."""
        for row in self.table.getRows():
            yield zapi.getMultiAdapter((row.context, row,
                                        self.request),IRowView)

    def getStatus(self):
        if self.table.form is None:
            return []
        else:
            return self.table.form.status
            
    def getErrors(self):
        if self.table.form is None:
            return []
        else:
            return self.table.form.error_views()

    def getPages(self):
        pages = self.table.config.pages
        if pages == 1:
            return []
        page = self.table.config.page
        batchSize = self.table.config.batchSize
        info = []
        if pages > 4:
            minPage = max(1,page-2)
            maxPage = min(pages,page+2)
        else:
            minPage = 1
            maxPage = pages
        if page > 1:
            info.append({'page':'<',
                         'batchStart':batchSize*(page-2)})
        if minPage > 1:
            info.append({'page':'1',
                         'batchStart':0})
        if minPage > 2:
            info.append({'page':'...',
                         'batchStart':batchSize})             
        for p in range(minPage,maxPage+1):
            info.append({'page':p,
                         'batchStart':batchSize*(p-1)})
        if maxPage < pages - 1:
            info.append({'page':'...',
                         'batchStart':batchSize*maxPage})
        if maxPage < pages:
            info.append({'page':pages,
                         'batchStart':batchSize*(pages-1)})
        if page < pages:
            info.append({'page':'>',
                         'batchStart':batchSize*page})
        return info

        
class RowView(BrowserView):

    implements(IRowView)

    template = ViewPageTemplateFile('row.pt')

    def __init__(self, context, row, request):
        super(RowView, self).__init__(context, request)
        self.row = row
        self.prefix = self.row.table.config.prefix + \
                      u'row.%s' % self.row.key
    
    def getCells(self):
        for cell in self.row.getCells():
            yield zapi.getMultiAdapter(
                (self.context,cell,self.request),
                ICellView,name=cell.column.name)

    def getActionsBase(self, formActions=None):
        """get (specific) available actions of row."""
        if self.row.table.form is None:
            return []
        
        result = []
        actions = self.row.getActions()
        form = self.row.table.form.forms[self.row.key]
        formActions = form.availableActions(formActions)            
        for formAction in formActions:
            if not formAction.label in actions:
                continue
            action = actions[formAction.label]
            adapt = zapi.queryMultiAdapter(
                      (self.row.container,action,self.request),
                      IActionView,name=action.name
                      )
            if adapt == None:
                adapt = zapi.getMultiAdapter(
                          (self.row.container,action,self.request),
                           IActionView,name=u""
                          )
            adapt.setPrefix(formAction.__name__)
            result.append(adapt)
        return result

    def getActions(self):
        """get all available actions of row."""
        return self.getActionsBase()

#    def getActions(self):
#        """get local actions of table.forms.form."""
#        if self.row.table.form is None:
#            return []
#        else:
#            form = self.row.table.form.forms[self.row.key]
#            return form.actions

    def __call__(self,*args,**kw):
        return self.template(*args,**kw)


class CellView(BrowserView):

    implements(ICellView)
    
    template = ViewPageTemplateFile('cell.pt')

    # cell attributes
    schema=None
    field=None
    
    # view attributes
    useWidget=True
    viewType = IDisplayWidget
    
    def __init__(self,context,cell,request):
        super(CellView, self).__init__(context, request)
        self.cell = cell
        
        # get cell attributes
        self.schema = self.schema or self.cell.column.schema
        if self.field is None:
            self.field = self.cell.column.field
        else:
            self.field = self.schema[self.field]
        self.adapted = self.schema(self.context)

        self.prefix = self.cell.table.config.prefix + 'cell.' + \
                      u'.'.join(self.cell.key)

        if IMethod.providedBy(self.field):
            # no widget available
            self.useWidget = False

    def setUpWidget(self):
        setUpWidget(self, self.cell.column.name, self.field, self.viewType,
                    value=self._value(),
                    prefix=self.prefix,
                    context=self.adapted)
        self.widget_name = '%s_widget'%self.cell.column.name

    def _value(self):
        field=self.field.bind(self.adapted)
        v = field.get(self.adapted)
        return v

    def hasInputWidget(self):
        if self.useForm:
            # use cell widget of form
            form = self.cell.table.form.forms[self.cell.row.key]
            widget = form.widgets[self.cell.column.name]
            return IInputWidget.providedBy(widget)
        else:
            return False
        
    def content(self):
        if self.useForm:
            # use cell widget of form
            form = self.cell.table.form.forms[self.cell.row.key]
            return form.widgets[self.cell.column.name]
        else:
            if self.useWidget:
                # use widget of cell
                self.setUpWidget()
                return getattr(self,self.widget_name)()
            else:
                # no widget available
                return getattr(self.adapted,self.field.__name__)()

    def __call__(self,*args,**kw):
        return self.template(*args,**kw)


class ActionView(BrowserView):

    implements(IActionView)

    template = ViewPageTemplateFile('action.pt')

    def __init__(self, context, action, request):
        super(ActionView, self).__init__(context, request)
        self.action = action
        self.prefix = self.action.table.config.prefix + \
                      u'.actions.%s' % self.action.name.lower()

    def setPrefix(self, prefix):
        self.prefix = prefix

    def __call__(self,*args,**kw):
        return self.template(*args,**kw)


class FilterView(BrowserView):

    implements(IFilterView)

    template = ViewPageTemplateFile('filter.pt')
    formClass = None

    def __init__(self, context, filter, request):
        super(FilterView, self).__init__(context, request)
        self.filter = filter
        self.prefix = self.filter.table.config.prefix + \
                      u'.filters.%s' % self.filter.name.lower()

    def filter(self, context):
        return True

    def setPrefix(self, prefix):
        self.prefix = prefix

    def __call__(self,*args,**kw):
        if self.formClass is None:
            return self.template(*args,**kw)
        else:
            return self.formClass(self.context, self.request, *args,**kw)()

        

def SimpleTableViewClass(template, offering=None, bases=(), attributes=None,
                       name=u''):
    """A function that can be used to generate a tableview from a set of
    information.
    """

    # Get the current frame
    if offering is None:
        offering = sys._getframe(1).f_globals

    # Create the base class hierarchy
    #bases += (TableView,)

    attrs = {'template' : ViewPageTemplateFile(template, offering),
             '__name__' : name}
    if attributes:
        attrs.update(attributes)

    # Generate a derived view class.
    class_ = type("SimpleTableViewClass from %s" % template, bases, attrs)

    return class_
