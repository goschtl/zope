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

Now let's go to the browser configuration file
(``src/tc/main/configure.zcml``) and fix the permissions there.

That's it.  If you would restart BlueBream at this point, you could not even
access the TicketCollector and/or Ticket instances. Therefore we need to
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

Note that you might want to grant the tc.Member role to the ``zope.anybody``
principal, so that everyone can view and add tickets.

The ``zope.anybody`` principal is an unauthenticated principal, which is
defined using the ``zope:unauthenticatedPrincipal`` directive, which has the
same three basic attributes the ``zope:principal`` directive had, but does
not accept the login and password attribute.

You also need to register a default view for ``IUnauthorized`` exception as
given below.  Here the and implementation available in ``zope.app.http``
package is included: ``zope.app.http.exception.unauthorized.Unauthorized``::

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
