.. _tut4-tutorial:

Tutorial --- Part 4
===================

.. _tut4-introduction:

Introduction
------------

BlueBream comes with a flexible security mechanism.  The two fundamental
concepts are **permissions** and **principals**.  Permission is a kind of
access, i.e. *permission to READ* vs. *permission to WRITE*.  Fundamentally
the whole security framework is organized around checking permissions on
objects.  Permissions are like keys to doors that open to a particular
functionality.  For example, in the issue tracker application used in the
tutorial, we might need the permission ``zope.View`` to look at a tickets'
detail screen.  Principals, on the other hand, are agents of the system that
execute actions.  The most common example of a principal is a user of the
system.  Principal is a generalization of the user concept.  The goal is now
to grant permissions to principals, which is the duty of another sub-system
known as the **securitypolicy**.

BlueBream does not enforce any particular security policy.  In contrary, it
encourages developers to carefully choose the security policy and use one
that fits their needs best.  The default BlueBream distribution comes with a
default security policy (``src/tc/main/securitypolicy.zcml``) that supports
the concept of roles.  Roles are like hats people wear, as Jim Fulton would
say, and can be seen as a collection of permissions.  A single user can have
several hats, but only wear one at a time.  Prominent examples of roles
include *member*, *editor* and *administrator*.  Therefore, the default
security policy supports mappings from permissions to principals,
permissions to roles, and roles to principals.  This chapter will use the
default security policy to setup the security, but will clearly mark the
sections that are security policy specific.

The first task will be to define a sensible set of permissions and change
the existing directives to use these new permissions.  This is a bit
tedious, but it is important that you do this carefully, since the quality
of your security depends on this task.  While doing this, you usually
discover that you missed a permission and even a role, so do not hesitate to
add some.  That is everything the programmer should ever do.  The site
administrator, who uses the default security policy, will then define roles
and grant permissions to them.  Finally the roles are granted to some users
for testing.

Securing an object does not require any modification to the existing Python
code as you will see going through the chapter, since everything is
configured via ZCML.  Therefore security can be completely configured using
ZCML, leaving the Python code untouched, which is another advantage of using
BlueBream.

.. _tut4-delcare-permissions:

Delcarations of Permissions
---------------------------

Permissions have to be explicitly defined.  For our ticket collector it will
suffice to define the following four basic permissions:

**View** - Allow users to access the data for tickets and comments.  Every
regular ticket collector user is going to have this permission.

**Add** - Allows someone to add a ticket or comment on tickets.  Note that
every regular user is allowed to do this, since adding tickets and
commenting must be possible.

**Edit** - Editing ticket details (after it is created) is only a permission
given to the admin user (for moderation), since we would not want a regular
user to be able to manipulate tickets after creation.

**Delete** - The admin must be able to get rid of comments, of course.
Therefore the delete permission is assigned to her.  Note that this
permission does not allow the admin to delete ticket collector objects.

Let's define the permissions now.  Note that they must appear at the very
beginning of the configuration file, so that they will be defined by the
time the other directives (that will use the permissions) are executed.
Here are the four directives you should add to your main ``configure.zcml``
file.  Open ``src/tc/main/configure.zcml`` and this at the beginning of
file, just before including ``securitypolicy.zcml``::

  <permission
     id="tc.View"
     title="View tickets and comments"
     description="View the tickets and all its comments."
     />

  <permission
     id="tc.Add"
     title="Add tickets and comments"
     description="Add tickets and comment on them."
     />

  <permission
     id="tc.Edit"
     title="Edit tickets and comments"
     description="Edit tickets and comment on them."
     />

  <permission
     id="tc.Delete"
     title="Delete tickets and comments"
     description="Delete tickets and comment on them."
     />

The ``zope:permission`` directive defines and creates a new permission in
the global permission registry.  The *id* should be a unique name for the
permission, so it is a good idea to give the name a dotted prefix, like
``tc.`` in this case.  Note that the *id* must be a valid URI or a dotted
name - if there is no dot in the dotted version, a `ValidationError` will be
raised.  The *id* is used as identifier in the following configuration
steps.  The *title* of the permissions is a short description that will be
used in web interfaces to identify the permission, while the description is
a longer explanation that serves more or less as documentation.  Both the
*id* and *title* are required attributes.

.. _tut4-use-permissions:

Using the Permissions
---------------------

Now that we have defined these permissions, we also have to use them; let's
start with the ticket collector configuration file
(``src/tc/collector/configure.zcml``).  In the following walk-through we are
only going to use the last part of the permission name to refer to the
permission, leaving off ``tc.``.  However, the full *id* has to be specified
for the configuration to execute.

Change the first `require` statement of the ticket content directive to use
the `View` permission.  This makes the description and the items accessible
to all users.  Similarly, change permission for the comment.

First, in the ``src/tc/collector/configure.zcml`` file update the
declaration like::

  <class class="tc.collector.ticket.Ticket">
    <implements
       interface="zope.annotation.interfaces.IAttributeAnnotatable"
       />
    <implements
       interface="zope.container.interfaces.IContentContainer"
       />
    <require
       permission="tc.View"
       interface="tc.collector.interfaces.ITicket"
       />
    <require
       permission="tc.View"
       set_schema="tc.collector.interfaces.ITicket"
       />
  </class>

  ...

  <class class="tc.collector.comment.Comment">
    <implements
       interface="zope.annotation.interfaces.IAttributeAnnotatable"
       />
    <require
       permission="tc.View"
       interface="tc.collector.interfaces.IComment"
       />
    <require
       permission="tc.View"
       set_schema="tc.collector.interfaces.IComment"
       />
  </class>


All the container functionality will only require the view permission, so
change the permissions to `View`.  This is unsecure, since this includes
read and write methods, but it will suffice for this demonstration.

Now let's go to the browser view configurations and fix the permissions
there::

  <browser:page
     for="tc.collector.interfaces.ICollector"
     name="index"
     permission="tc.View"
     class="tc.collector.views.TicketCollectorMainView"
     layer="tc.skin.interfaces.ITCSkin"
     />

  <browser:page
     for="tc.collector.interfaces.ICollector"
     name="add_ticket"
     permission="tc.Add"
     class="tc.collector.views.AddTicket"
     layer="tc.skin.interfaces.ITCSkin"
     />

  <browser:page
     for="tc.collector.interfaces.ITicket"
     name="index"
     permission="tc.View"
     class="tc.collector.views.TicketMainView"
     layer="tc.skin.interfaces.ITCSkin"
     />

  <browser:page
     for="tc.collector.interfaces.ITicket"
     name="add_comment"
     permission="tc.Add"
     class="tc.collector.views.AddComment"
     layer="tc.skin.interfaces.ITCSkin"
     />


That's it.  If you would restart BlueBream at this point, you could not even
access the TicketCollector and/or Ticket instances.  Therefore we need to
create some roles next and assign permissions to them.

.. _tut4-delcare-roles:

Declaration of Roles
--------------------

The declaration of roles is specific to BlueBream's default security policy.
Another security policy might not even have the concept of roles at all.
Therefore, the role declaration and grants to the permissions should not
even be part of your package.  For simplicity and keeping it all at one
place, we are going to store the policy-specific security configuration in
``src/tc/main/securitypolicy.zcml``.  For our ticket collector package we
really only need two roles, *Member* and *Admin*, which are declared as
follows::

  <role
      id="tc.Member"
      title="Ticket collector member"
      description="Users that actually use the ticket collector."/>

  <role
      id="tc.Admin"
      title="Ticket collector administrator"
      description="The administrator can edit and delete tickets."/>

Equivalently to the ``zope:permission`` directive, the ``zope:role``
directive creates and registers a new role with the global role registry.
Again, the id must be a unique identifier that is used throughout the
configuration process to identify the role.  Both, the id and the title are
required.

Next we grant the new permissions to the new roles, i.e. create a
permission-role map.  The user should be only to add and view tickets, while
the editor is allowed to execute all permission.

::

  <grant
      permission="tc.View"
      role="tc.Member"
      />

  <grant
      permission="tc.Add"
      role="tc.Member"
      />

  <grant
       permission="tc.Edit"
       role="tc.Admin"
       />

  <grant
      permission="tc.Delete"
      role="tc.Admin"
      />

The ``zope:grant`` directive is fairly complex, since it permits all three
different types of security mappings.  It allows you to assign a permission
to a principal, a role to a principal, and a permission to a role.
Therefore the directive has three optional arguments: *permission*, *role*,
and *principal*.  Exactly two of the three arguments have to be specified to
make it a valid directive.  All three security objects are specified by
their id.

.. _tut4-roles-principals:

Assigning Roles to Principals
-----------------------------

To make our package work again, we now have to connect the roles to some
principals.  We are going to create two new principals called boarduser and
boardeditor.  To do that, go to the BlueBream root directory and add the
following lines to ``src/tc/main/principals.zcml``::

  <principal
      id="tc.jack"
      title="Ticket collector member"
      login="jack"
      password="jack"
      />

  <grant
      role="tc.Member"
      principal="tc.jack"
      />

  <principal
      id="tc.jill"
      title="Ticket collector admin"
      login="jill"
      password="jill"
      />

  <grant
      role="tc.Member"
      principal="tc.jill"
      />

  <grant
      role="tc.Admin"
      principal="tc.jill"
      />

The ``zope:principal`` directive creates and registers a new principal/user
in the system.  Like for all security object directives, the *id* and
*title* attributes are required.  We could also specify a description as
well.  In addition to these three attributes, the developer must specify a
login and password (plain text) for the user, which is used for
authentication of course.

Note that you might want to grant the ``tc.Member`` role to the
``zope.anybody`` principal, so that everyone can view and add tickets.

The ``zope.anybody`` principal is an unauthenticated principal, which is
defined using the ``zope:unauthenticatedPrincipal`` directive, which has the
same three basic attributes the ``zope:principal`` directive had, but does
not accept the login and password attribute.

You also need to register a default view for ``IUnauthorized`` exception as
given below.  Here the and implementation available in ``zope.app.http``
package is included: ``zope.app.http.exception.unauthorized.Unauthorized``.
Add these registrations to ``src/tc/main/configure.zcml``::

  <view
      for="zope.security.interfaces.IUnauthorized"
      type="zope.publisher.interfaces.http.IHTTPRequest"
      name="index"
      permission="zope.Public"
      factory="zope.app.http.exception.unauthorized.Unauthorized"
      />

  <browser:defaultView
      for="zope.security.interfaces.IUnauthorized"
      layer="zope.publisher.interfaces.http.IHTTPRequest"
      name="index"
      />

Now your system should be secure and usable.  If you restart BlueBream now,
you will see that only the ticket collector's Admin can freely manipulate
objects.  (Of course you have to log in as one.)

Important Note: While testing security related things use ``deploy.ini``.
Otherwise you can remove ``z3c.evalexception`` middleware from ``debug.ini``.

Persistent principals
---------------------

In the example given above, principals are stored in ZCML.  You can store
principals in ZODB using some plugins mechanism provided by the pluggable
authentication utility using `zope.pluggableauth` package.

While adding ticket collector, it is registered as a site.  A site provides
a persistent component registry.  To add site to the collector object, you
are doing like this in ``src/tc/collector/views.py`` file (class:
``AddTicketCollector``)::

         collector.setSiteManager(LocalSiteManager(collector))

Repplace this line with this function call::

         setup_site_manager(context)

Here is the definition of this function, you can write this function in the
same file, ``src/tc/collector/views.py``::

  from zope.site import LocalSiteManager
  from zope.pluggableauth.authentication import PluggableAuthentication
  from zope.authentication.interfaces import IAuthentication
  from zope.app.authentication.principalfolder import PrincipalFolder
  from zope.pluggableauth.interfaces import IAuthenticatorPlugin

  from zope.securitypolicy.interfaces import (IPrincipalRoleManager,
                                              IPrincipalPermissionManager)
  from zope.principalannotation.interfaces import IPrincipalAnnotationUtility
  from zope.principalannotation.utility import PrincipalAnnotationUtility
  from zope.session.interfaces import ISessionDataContainer
  from zope.session.session import PersistentSessionDataContainer

  from zope.event import notify
  from zope.lifecycleevent import ObjectCreatedEvent, ObjectModifiedEvent
  from zope.session.http import CookieClientIdManager
  from zope.session.http import ICookieClientIdManager
  from zope.app.authentication.principalfolder import InternalPrincipal

  def setup_site_manager(context):
      context.setSiteManager(LocalSiteManager(context))
      sm = context.getSiteManager()
      pau = PluggableAuthentication(prefix='hello.pau.')
      notify(ObjectCreatedEvent(pau))
      sm[u'authentication'] = pau
      sm.registerUtility(pau, IAuthentication)

      annotation_utility = PrincipalAnnotationUtility()
      sm.registerUtility(annotation_utility, IPrincipalAnnotationUtility)
      session_data = PersistentSessionDataContainer()
      sm.registerUtility(session_data, ISessionDataContainer)

      client_id_manager = CookieClientIdManager()
      notify(ObjectCreatedEvent(client_id_manager))
      sm[u'CookieClientIdManager'] = client_id_manager
      sm.registerUtility(client_id_manager, ICookieClientIdManager)

      principals = PrincipalFolder(prefix='pf.')
      notify(ObjectCreatedEvent(principals))
      pau[u'pf'] = principals
      pau.authenticatorPlugins += (u"pf", )
      notify(ObjectModifiedEvent(pau))

      pau.credentialsPlugins += (u'Session Credentials',)

      p1 = InternalPrincipal('admin1', 'admin1', "Admin 1",
                             passwordManagerName="Plain Text")
      principals['p1'] = p1

      role_manager = IPrincipalRoleManager(context)
      login_name = principals.getIdByLogin(p1.login)
      pid = unicode('hello.pau.' + login_name)
      role_manager.assignRoleToPrincipal('tc.Admin', pid)

Now you need to create a new factory class for
``zope.security.interfaces.IUnauthorized`` exception.  Create a file
``src/tc/main/unauthorized.py`` with this content::

  from zope.authentication.interfaces import IAuthentication
  from zope.publisher.browser import BrowserPage
  from zope.component import getUtility
  from zope.browserpage import ViewPageTemplateFile

  class Unauthorized(BrowserPage):

      template = ViewPageTemplateFile('unauthorized.pt')

      def __call__(self):
          # Set the error status to 403 (Forbidden) in the case when we don't
          # challenge the user
          self.request.response.setStatus(403)

          # make sure that squid does not keep the response in the cache
          self.request.response.setHeader('Expires', 'Mon, 26 Jul 1997 05:00:00 GMT')
          self.request.response.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate')
          self.request.response.setHeader('Pragma', 'no-cache')

          principal = self.request.principal
          auth = getUtility(IAuthentication)
          auth.unauthorized(principal.id, self.request)
          if self.request.response.getStatus() not in (302, 303):
              return self.template()

Create the ``src/tc/main/unauthorized.pt`` with this content::

  <html>
  <body>

  <h1>Unauthorized</h1>

  <p>You are not authorized</p>

  </body>
  </html>

You can change the ``zope.security.interfaces.IUnauthorized`` exception view
registration like this in the file: ``src/tc/main/configure.zcml``::

  <view
     for="zope.security.interfaces.IUnauthorized"
     type="zope.publisher.interfaces.http.IHTTPRequest"
     name="index"
     permission="zope.Public"
     factory=".unauthorized.Unauthorized"
     />

Finally you need a login form, create a template file in
``src/tc/main/loginform.html``::

  <html>
    <head><title>Sign in</title></head>
  <body>
  
    <div tal:define="principal python:request.principal.id">
      <p tal:condition="python: principal == 'zope.anybody'">
        Please provide Login Information</p>
      <p tal:condition="python: principal != 'zope.anybody'">
        You are not authorized to perform this action. However, you may login
        as a different user who is authorized.</p>
      <form action="" method="post">
        <div tal:omit-tag=""
             tal:condition="python:principal != 'zope.anybody' and 'SUBMIT' in request">
          <span
             tal:define="dummy python:request.response.redirect(request.get('camefrom', ''))" />
        </div>
  
        <div class="row">
          <div class="label">
            <label for="login" i18n:translate="">User Name</label></div>
          <div class="field">
            <input type="text" name="login" id="login" />
          </div>
        </div>
  
        <div class="row">
          <div class="label">
            <label for="password" i18n:translate="">Password</label></div>
          <div class="field">
            <input type="password" name="password" id="password" />
          </div>
        </div>
      
        <div class="row">
          <input class="form-element" type="submit" 
                 name="SUBMIT" value="Log in" i18n:attributes="value login-button" />
        </div>
        <input type="hidden" name="camefrom" tal:attributes="value request/camefrom | nothing" />
      </form>
    </div>
  </body>
  </html>

And register a browser page with the above template::

  <browser:page
     name="loginForm.html"
     for="*"
     template="loginform.pt"
     permission="zope.Public"
     layer="tc.skin.interfaces.ITCSkin"
     />

Now you should be able access the site with new authentication details.  The
``admin1`` user has the Admin role.

Conclusion
----------

This chapter introduced BlueBream security concepts and explained how to use
it.

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
