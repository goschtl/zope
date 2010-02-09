from remotetaskexample.interfaces import IExampleTask
from zope.interface import implements
from zope.app.publication.zopepublication import ZopePublication
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl import getSecurityManager

FOLDER_ID = 'SomeFolder'

class ExampleTask(object):
    """ This example task shows how to create Folder from the service """
    implements(IExampleTask)

    def __call__(self, service, jobid, input):
        print "Creating folder in context of %s" % input
        
        # get application object
        app = service._p_jar.root()[ZopePublication.root_name]
        # get context object
        context = app.unrestrictedTraverse(input['path'])
            # get user
        acl_users = app.unrestrictedTraverse(input['user_container'])
        if acl_users is not None:
            user = acl_users.getUser(input['user_id'])
        else: 
            user = None
        sm = getSecurityManager()
        try:
            # force user    
            newSecurityManager(None, user)
            
            if getattr(context, FOLDER_ID, None) is None:
                id = context.invokeFactory('Folder', FOLDER_ID)
                folder = getattr(context, id)
                print  "Folder %s created" % folder
                return "Folder %s created" % folder
            else:
                print  "Folder %s already exists" % FOLDER_ID
                return "Folder %s already exists" % FOLDER_ID
        finally:
            setSecurityManager(sm)
