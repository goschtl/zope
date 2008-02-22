==============
z3c.securitytool
================


z3c.securitytool is a Zope3 package aimed at providing component level
security information to assist in analyzing security problems and to
potentially expose weaknesses. The goal of the security tool is to
provide a matrix of users and their effective permissions for all available
views for any given component and context. We also provide two further
levels of detail. You can view the details of how a user came to have
the permission on a given view, by clicking on the permission in the matrix.


FOR THE IMPATIENT TO VIEW YOUR SECURITY MATRIX:
  Remember this is a work in progress.

  1. Add the z3c.securitytool to your install_requires in your
     setup.py. 
  2. Add the <include package="z3c.securitytool"/> to your site.zcml
  3. Append the @@securityMatrix.html view to any context to view the permission
     matrix for that context.


  Desired Behavior
  ---------------
  On the page you will be able to select the desired skin from all the
  available skins on the system.  On initial load of the securitytool
  you will only see permissions for IBrowserRequest and your current 
  context. The interesting information is when you select the skins.
  A future release of this tool will offer a selection to view  all
  information for all skins as well as each skin individually.

  You can also truncate the results by selecting the permission from
  the filter select box.

  When you click on the "Allow" or "Deny" security tool will explain
  where these permissions were specified whether by role, group, or
  in local context.

  When you click on a user-name all the permissions inherited from
  roles, groups or specifically assigned will be displayed.


Lets make sure all the views work properly. Just a simple smoke test

    >>> from zope.testbrowser.testing import Browser
    >>> manager = Browser()
    >>> authHeader = 'Basic mgr:mgrpw'
    >>> manager.addHeader('Authorization', authHeader)
    >>> manager.handleErrors = False


First we will check if the main page is available
    >>> manager.open('http://localhost:8080/@@securityMatrix.html')


Now lets send the filter variable so our test is complete
    >>> manager.open('http://localhost:8080/@@securityMatrix.html?'
    ...              'FILTER=None&selectedSkin=ConcordTimes')


And with the selected permission
    >>> manager.open('http://localhost:8080/@@securityMatrix.html?'
    ...              'FILTER=None&selectedSkin=ConcordTimes&'
    ...              'selectedPermission=zope.Public')


Here we send an invalid selectedPermisson ( just for coverage ) ;)
    >>> manager.open('http://localhost:8080/@@securityMatrix.html?'
    ...              'FILTER=None&selectedSkin=ConcordTimes&'
    ...              'selectedPermission=zope.dummy')


This is the principal detail page, you can get to by clicking on the
principals name at the top of the form.

    >>> manager.open('http://localhost:8080/@@principalDetails.html?principal=zope.daniel')
    >>> 'Permission settings' in manager.contents
    True


And lets call the view without a principal
    >>> manager.open('http://localhost:8080/@@principalDetails.html')
    Traceback (most recent call last):
    ...
    PrincipalLookupError: no principal specified

Here is the view you will see if you click on the actual permission
value in the matrix intersecting the view to the user on a public view.
    >>> manager.open('http://localhost:8080/@@permissionDetails.html?'
    ...              'principal=zope.daniel&view=PUT')

    'zope.Public' in manager.contents
    True

Ok lets send the command without the principal:
    >>> manager.open('http://localhost:8080/@@permissionDetails.html?view=PUT')
    Traceback (most recent call last):
    ...
    PrincipalLookupError: no user specified

And now we will test it without the view name
  >>> manager.open('http://localhost:8080/@@permissionDetails.html?principal=zope.daniel')

