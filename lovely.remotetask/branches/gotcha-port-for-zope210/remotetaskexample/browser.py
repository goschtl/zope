from Products.CMFCore.utils import getToolByName
from zope.component import getUtility, getUtilitiesFor
from AccessControl import getSecurityManager
from lovely.remotetask.interfaces import ITaskService
from remotetaskexample.service import ExampleService
import transaction

# see configure.zcml for the description 

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

class JobStatus(object):
    """ Some docis """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        jobid = self.request.get('job', -1)
        if jobid == -1:
            return
        else:
            service = getUtility(ITaskService, name='ExampleService')
            return "%s - %s" % (service.getStatus(jobid) , service.getResult(jobid))
            

class RunTask(object):
    """ Some docis """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        service = getUtility(ITaskService, name='ExampleService')
        # we want to pass current context path, current member ID and user storage
        # anyway, the parameters are not required
        path = '/'.join(self.context.getPhysicalPath())
        # if Anonymous, user_id will be None
        user = getSecurityManager().getUser()
        user_id = user.getId()
        user_container = '/'.join(user.aq_parent.getPhysicalPath())
        # look to task.py how parameters are processed
        jobid = service.add(u'exampletask', dict(path=path, user_id=user_id, user_container=user_container))
        return "exampletask added. Job ID: %d." % jobid

class AddExampleService(object):
    """ Adds a service to the site. """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        portal_url = getToolByName(self.context, 'portal_url')
        site = portal_url.getPortalObject()
        # service will be persistently stored
        sm = site.getSiteManager()
        service = sm.queryUtility(ITaskService, 'ExampleService')
        if service is None:
            service = ExampleService()
            service.__parent__ = site
            service.id = 'ITaskService-ExampleService'
            service.__name__ = service.getId()
            site._setOb(service.id, service)
            sm.registerUtility(service, ITaskService, 'ExampleService')
            msg = "service successfully added and started"
        else:
            msg = "service successfully started"
            
        # startProcessing needs the utility to have a _p_jar so we need
        # to use a savepoint here
        transaction.savepoint()
        service.startProcessing()

        return msg
