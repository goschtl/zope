from Products.CMFCore.utils import getToolByName
from zope.component import getUtility, getUtilitiesFor
from lovely.remotetask.interfaces import ITaskService
from remotetaskexample.service import ExampleService
import transaction

class Example(object):
    """ Some docis """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        portal_url = getToolByName(self.context, 'portal_url')
        site = portal_url.getPortalObject()

        service = getUtility(ITaskService, name='ExampleService',
                             context=site)
        service.startProcessing()
        return "successfully started service"

class RunTask(object):
    """ Some docis """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        service = getUtility(ITaskService, name='ExampleService')
        service.add(u'exampletask', 'china')
        return "exampletask added"

class AddExampleService(object):
    """ Adds a service to the site. """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        portal_url = getToolByName(self.context, 'portal_url')
        site = portal_url.getPortalObject()

        service = ExampleService()

        sm = site.getSiteManager()
        sm.registerUtility(ITaskService, service, 'ExampleService')
        service = sm.queryUtility(ITaskService, 'ExampleService')
        service.__parent__ = sm
        service.id = 'ITaskService-ExampleService'
        service.__name__ = service.getId()

        # startProcessing needs the utility to have a _p_jar so we need
        # to use a savepoint here
        transaction.savepoint()
        service.startProcessing()

        return "service successfully added and started"
