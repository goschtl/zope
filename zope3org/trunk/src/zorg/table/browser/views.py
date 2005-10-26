
from zope.interface import Interface, implements
from zope.interface.interfaces import IMethod
from zope.schema.interfaces import IField

from zope.app import zapi
from zope.app.publisher.browser import BrowserView
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.form.interfaces import IInputWidget,IDisplayWidget
from zope.app.form.utility import setUpWidget

from zorg.table.interfaces import ITable,ITableConfig
from interfaces import ITableView,IRowView,ICellView,ITableForm

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
            self.table.form.update()
        else:
            self.table.form = None

    def __call__(self,*args,**kw):
        return self.template(*args,**kw)

    def getActions(self):
        """get global actions of table.form."""
        return self.table.form.actions

    def getRows(self):
        """get objects of table.form."""
        for row in self.table.getRows():
            yield zapi.getMultiAdapter((row.context, row,
                                        self.request),IRowView)


class RowView(BrowserView):

    implements(IRowView)

    template = ViewPageTemplateFile('row.pt')

    def __init__(self, context, row, request):
        super(RowView, self).__init__(context, request)
        self.row = row
        self.prefix = self.row.table.config.prefix + \
                      u'row.%s' % self.row.key
    
    def __call__(self,*args,**kw):
        return self.template(*args,**kw)

    def getCells(self):
        for cell in self.row.getCells():
            yield zapi.getMultiAdapter(
                (self.context,cell,self.request),
                ICellView,name=cell.column.name)

class CellView(BrowserView):

    implements(ICellView)
    template = ViewPageTemplateFile('cell.pt')
    useForm=False
    useWidget=True
    schema=None
    field=None
    
    def __init__(self,context,cell,request):
        super(CellView, self).__init__(context, request)
        self.cell = cell
        self.schema = self.schema or self.cell.column.schema
        if self.field is None:
            self.field = self.cell.column.field
        else:
            self.field = self.schema[self.field]
        self.prefix = self.cell.table.config.prefix + 'cell.' + \
                      u'.'.join(self.cell.key)
        
        self._action = self._action_default
        if self.cell.table.config.action:
            name = '_action_' + self.cell.table.config.action.name
            action =  getattr(self,name,None)
            if callable(action):
                self._action = action
        self.adapted = self.schema(self.context)
        self.viewType = IDisplayWidget
        if IMethod.providedBy(self.field):
            # no widget available
            self.useWidget = False

    def _action_default(self):
        self.viewType=IDisplayWidget
        self.setUpWidget()

    def setUpWidget(self):
        setUpWidget(self, self.cell.column.name, self.field, self.viewType,
                    value=self._value(),
                    prefix=self.prefix,
                    context=self.adapted)
        self.widget_name = '%s_widget'%self.cell.column.name

    def _action_save(self):

        """updates the data if we are in editMode and the request
        data does not match the context data"""
        self.viewType = IInputWidget
        self.setUpWidget()
        widget=getattr(self,self.widget_name)
        changed = False
        if IInputWidget.providedBy(widget) and widget.hasInput():
            changed = widget.applyChanges(self.adapted)
        return changed

    def _value(self):
        field=self.field.bind(self.adapted)
        v = field.get(self.adapted)
        return v

    def _action_edit(self):
        self.viewType = IInputWidget
        self.setUpWidget()

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
#        if not self.useForm:
#            return self._value()
#        self._action()
#        return getattr(self,self.widget_name)()

    def __call__(self,*args,**kw):
        return self.template(*args,**kw)

        
def SimpleTableViewClass(template, offering=None, bases=(), attributes=None,
                    name=u''):
    import sys
    # Get the current frame
    if offering is None:
        offering = sys._getframe(1).f_globals

    # Create the base class hierarchy
    #bases += (SimpleViewlet, simple)

    attrs = {'template' : ViewPageTemplateFile(template, offering),
             '__name__' : name}
    if attributes:
        attrs.update(attributes)

    # Generate a derived view class.
    class_ = type("SimpleTableViewClass from %s" % template, bases, attrs)

    return class_

