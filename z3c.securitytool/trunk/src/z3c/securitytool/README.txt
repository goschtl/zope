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


  >>> from pprint import pprint
  >>> from zope.interface import implements
  >>> from zope.annotation.interfaces import IAttributeAnnotatable
  >>> from zope.app.container import contained
  >>> from zope.app.folder import Folder, rootFolder

  >>> from zope.app.authentication.principalfolder import Principal
  >>> from zope.securitypolicy.role import Role
  >>> from zope.security.permission import Permission

  

The news agency, the Concord Times, is implementing a new article management
system in Zope 3. In order to better understand their security situation, they
have installed z3c.security tool. 

  >>> concordTimes = rootFolder()
  
The Concord Times site is a folder which contains a Folder per issue and each
issue contains articles.

  >>> class Issue(Folder):
  ...     def __init__(self, title):
  ...         self.title = title
  ...
  ...     def __repr__(self):
  ...         return '<%s %r>' %(self.__class__.__name__, self.title)

  >>> class Article(contained.Contained):
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
  
To allow editors to create articles Martin has to create a new Issue:
    
  >>> firstIssue = concordTimes['issue.1'] = \
  ...     Issue('The very first issue of `The Concord Times`')

Randy starts to write his first article:
    
  >>> firstArticle = Article('A new star is born',
  ...                        'A new star is born, the `The Concord Times` ...')
  
  
   >>> from zope.security import testing
   >>> from zope.securitypolicy import zopepolicy

  >>> policy = zopepolicy.ZopeSecurityPolicy()
  >>> participation = testing.Participation(markus)
  >>> policy.add(participation)
  >>> policy.checkPermission(createIssue.id, concordTimes)
  False
  
  >>> policy2 = zopepolicy.ZopeSecurityPolicy()
  >>> participation2 = testing.Participation(martin)
  >>> policy2.add(participation2)
  >>> policy2.checkPermission(createIssue.id, concordTimes)
  True
  

  
  