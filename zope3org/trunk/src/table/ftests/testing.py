from zope.app.publisher.browser import BrowserView
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from zope.interface import Interface, implements
from zope.app import zapi
from zope.app.location.interfaces import ILocation
from table.table import Table,Column

class TestView(BrowserView):

    def __init__(self, context, request):
        super(TestView, self).__init__(context, request)

        # config is a one timer?
        # table is ?
        requestConfig = ITableConfig(self.request)
        #preferencesConfig = ITableConfig(some preference object?)
        table = zapi.getUtility(ITable,
                                name='readcontainer.contents')
        config = zapi.getUtility(ITableConfig,
                                 name='readcontainer,contents')
        table = zapi.getAdapter(
            self.context,ITable,'readcontainer.contents')

        table.applyConfig(config)
        table = table.bind(self.context)

