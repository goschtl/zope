================
z3c.securitytool
================


z3c.securitytool is a Zope3 package aimed at providing component level security
information to assist in analyzing security problems and to potentially expose
weaknesses. The goal of the security tool is to provide a matrix of users and 
their effective permissions for all available views for any given component 
and context. We also provide two further levels of detail. You can view the 
details of how a user came to have the permission on a given view, by clicking 
on the permission in the matrix.  


FOR THE IMPATIENT TO VIEW YOUR SECURITY MATRIX: 
  Remember this is a work in progress.

  1. Add the <include package="z3c.securitytool"/> to your site.zcml
  2. Append the @@vum.html view to any context to view the permission
     matrix for that context.
     
  
  Desired Behavior
  ---------------
  On the page you will be able to select the desired skin from all the 
  available skin on the system. You can also trunkate the results by 
  selecting the permission from the filter select box.

  When you click on the "Allow" or "Deny" security tool will explain
  where these permissions were specified wheather by role, group, or
  in local context. 
  
  When you click on a username all the permissions inherited from
  roles, groups or specifically assigned will be displayed


  >>> from pprint import pprint
  >>> import zope
  >>> from zope.interface import implements
  >>> from zope.annotation.interfaces import IAttributeAnnotatable
  >>> from zope.app.container import contained
  >>> from zope.app.folder import Folder, rootFolder
  >>> import persistent


  >>> from zope.app.authentication.principalfolder import Principal
  >>> from zope.securitypolicy.role import Role
  >>> from zope.security.permission import Permission

  >>> from zope.publisher.interfaces import IRequest

  >>> from zope.component import provideAdapter  
  >>> from zope.app.testing import ztapi
  >>> from zope.app.folder.interfaces import IFolder
  >>> import transaction

The news agency, the Concord Times, is implementing a new article management
system in Zope 3. In order to better understand their security situation, they
have installed z3c.security tool. 

  >>> concordTimes = getRootFolder()
  
The Concord Times site is a folder which contains a Folder per issue and each
issue contains articles.

  >>> class Issue(Folder):
  ...     implements(IFolder)
  ...     def __repr__(self):
  ...         return '<%s %r>' %(self.__class__.__name__, self.title)

  >>> ztapi.provideAdapter(
  ...     IRequest, IFolder,
  ...     Issue)

  >>> class Article(contained.Contained, persistent.Persistent):
  ...     implements(IAttributeAnnotatable)
  ...
  ...     def __init__(self, title, text):
  ...         self.title = title
  ...         self.text = text
  ...
  ...     def __repr__(self):
  ...         return '<%s %r>' %(self.__class__.__name__, self.title)
  
At the Concord Times, they have only three levels of users: Editors, Writers,
and Janitors.

  >>> editor = Role('concord.Editor', 'The editors')
  >>> writer = Role('concord.Writer', 'The writers')
  >>> janitor = Role('concord.Janitor', 'The janitors')

In order to control who has access to the system, they define the following
necessary permissions:
    
  >>> createIssue = Permission('concord.CreateIssue','Create Issue')
  >>> publishIssue = Permission('concord.PublishIssue', 'Publish Issue')
  >>> readIssue    = Permission('concord.ReadIssue', 'Read Issue')
  >>> createArticle = Permission('concord.CreateArticle', 'Create Article')
  >>> deleteArticle = Permission('concord.DeleteArticle', 'Delete Article')

Now we need to setup the security system on the level of the news agency.
In order to assign the permissions to the roles, we must setup a role-
permission Manager, which is used to map permissions to roles.

  >>> from zope.securitypolicy.interfaces import IRolePermissionManager
  >>> rolePermManager = IRolePermissionManager(concordTimes)
  
Now we can use our ``rolePermManager`` to assign the roles. 
Editors are the only users that are allowed to create and publish issues.
Writers and Editors may create articles, but only editors can delete them.
Everyone can read the issues.
  
  >>> rolePermManager.grantPermissionToRole(createIssue.id, editor.id)
  >>> rolePermManager.grantPermissionToRole(publishIssue.id, editor.id)
  >>> rolePermManager.grantPermissionToRole(readIssue.id, editor.id)
  >>> rolePermManager.grantPermissionToRole(createArticle.id, editor.id)
  >>> rolePermManager.grantPermissionToRole(deleteArticle.id, editor.id)
  
  >>> rolePermManager.grantPermissionToRole(readIssue.id, writer.id)
  >>> rolePermManager.grantPermissionToRole(createArticle.id, writer.id)
  
  >>> rolePermManager.grantPermissionToRole(readIssue.id, janitor.id)

The news agency now hires the initial set of staff members. So let's create
a principal for each hired person:

  >>> martin = Principal('martin', 'Martin')
  >>> randy = Principal('randy', 'Randy')
  >>> markus = Principal('markus', 'Markus')
  >>> daniel = Principal('daniel', 'Daniel')
  >>> stephan = Principal('stephan', 'Stephan')

Based on their positions we assign proper roles to the staff.
In order to assign roles to our staff members, we must first create a
principal-role manager.

  >>> from zope.securitypolicy.interfaces import IPrincipalRoleManager
  >>> prinRoleManager = IPrincipalRoleManager(concordTimes)
  
And now we can assign the roles. At the Concord Times, Martin is an editor,
Randy and Markus are writers, and Daniel and Stephan are janitors.

  >>> prinRoleManager.assignRoleToPrincipal(editor.id, martin.id)
  >>> prinRoleManager.assignRoleToPrincipal(writer.id, randy.id)
  >>> prinRoleManager.assignRoleToPrincipal(writer.id, markus.id)
  >>> prinRoleManager.assignRoleToPrincipal(janitor.id, daniel.id)
  >>> prinRoleManager.assignRoleToPrincipal(janitor.id, stephan.id)

Lets set up the securityPolicy objects and the corresponding
participation for our actors.

  >>> from zope.security import testing
  >>> from zope.securitypolicy import zopepolicy

  >>> markus_policy = zopepolicy.ZopeSecurityPolicy()
  >>> markus_part = testing.Participation(markus)
  >>> markus_policy.add(markus_part)

  >>> martin_policy = zopepolicy.ZopeSecurityPolicy()
  >>> martin_part = testing.Participation(martin)
  >>> martin_policy.add(martin_part)

  >>> randy_policy = zopepolicy.ZopeSecurityPolicy()
  >>> randy_part = testing.Participation(randy)
  >>> randy_policy.add(randy_part)

  >>> stephan_policy = zopepolicy.ZopeSecurityPolicy()
  >>> stephan_part = testing.Participation(stephan)
  >>> stephan_policy.add(stephan_part)

  >>> daniel_policy = zopepolicy.ZopeSecurityPolicy()
  >>> daniel_part = testing.Participation(daniel)
  >>> daniel_policy.add(daniel_part)
  

  >>> firstIssue = \
  ...    Folder()
  >>> concordTimes['firstIssue'] = firstIssue
  >>> concordTimes._p_changed = 1
  >>> transaction.commit()



Randy starts to write his first article:
    
  >>> firstArticle = Article('A new star is born',
  ...                        'A new star is born, the `The Concord Times` ...')
  
   TODO: add permisson settings for this context then test with
   functional tests.


  
Markus tries to give his fellow writer some help by attempting to
create an Issue and of course cannot.

  >>> markus_policy.checkPermission(createIssue.id, concordTimes)
  False


Only Martin as the editor has createIssue priveleges.

  >>> martin_policy.checkPermission(createIssue.id, concordTimes)
  True
  

This is not yet complete. But this is the proper way to connect.
Now lets see if the app displays the appropriate permissions.

    >>> from zope.testbrowser.testing import Browser # use for external
    >>> import base64
    >>> manager = Browser()
    >>> login,password = 'admin','admin'
    >>> authHeader = "Basic %s" % base64.encodestring(
    ...                            "%s:%s" % (login,password))

    >>> manager.addHeader('Authorization', authHeader)
    >>> manager.handleErrors = False

    >>> list(concordTimes.keys())
    [u'firstIssue']


Our issue was added to the root folder as we can see by printing @@contents.html
    >>> manager.open('http://localhost:8080/@@contents.html')
    >>> print manager.contents
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <BLANKLINE>
    ...
    <td>
      <input type="checkbox"
             class="noborder slaveBox"
             name="ids:list" id="firstIssue"
             value="firstIssue" />
    </td>
    ...
    </html>
    <BLANKLINE>
    <BLANKLINE>

TODO: Make this a real test.
    >>> manager.open('http://localhost:8080/@@vum.html')
    >>> print manager.contents
    <html>
    <head>
    <link type="text/css" rel="stylesheet" media="all"
    ...
    </body>
    </html>
    <BLANKLINE>

TODO: make this a valid test we are looking for permission
settings provided in the test appear on the html page.

    >>> manager.open('http://localhost:8080/firstIssue/pd.html?principal='
    ... + 'zope.sample_manager&view=addSiteManager.html"')

    >>> print manager.contents
    <html>
    <head>
    ...
    </html>
    <BLANKLINE>


