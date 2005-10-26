from zope.app import zapi
from zope.app.publisher.browser import BrowserView
from zorg.table.browser.interfaces import ITableView
from zorg.table.browser.views import CellView
from zope.app.copypastemove.interfaces import IContainerItemRenamer
from zope.app.form.interfaces import IInputWidget,IDisplayWidget
from form import TableForm


class ContainerView(BrowserView):

    def __init__(self, context, request):
        super(ContainerView, self).__init__(context, request)
        self.table = zapi.getMultiAdapter((context,request),
                                          ITableView,u'zorg.table.container.table')


class ContainerTableView(BrowserView):

    formClass=TableForm

    
class NameView(CellView):

    def __init__(self,context,cell,request):
        super(NameView, self).__init__(context,cell,request)

    def _action_save(self):
        
        """updates the data if we are in editMode and the request
        data does not match the context data"""
        self.viewType = IInputWidget
        self.setUpWidget()
        widget=getattr(self,self.widget_name)
        changed=False
        if widget.hasInput():
            newId=widget.getInputValue()
            oldId=self._value()
            renamer = IContainerItemRenamer(self.cell.table.context)
            if newId != oldId:
                renamer.renameItem(oldId, newId)
                changed=True
        return changed


        
