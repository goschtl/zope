.. _tut3-tutorial:

Tutorial --- Part 3
===================

.. _tut3-introduction:

Introduction
------------

Security
========

Introduction
------------

BlueBream comes with a flexible security mechanism.  The two fundamental
concepts are **permissions** and **principals**.  Permission is a kind of
access, i.e. *permission to READ* vs. *permission to WRITE*.  Fundamentally
the whole security framework is organized around checking permissions on
objects.  Permissions are like keys to doors that open to a particular
functionality.  For example, in the issue tracker application used in the
tutorial, we might need the permission `zope.View` to look at a tickets's
detail screen.  Principals, on the other hand, are agents of the system that
execute actions.  The most common example of a principal is a user of the
system.  Principal is a generalization of the user concept.  The goal is now
to grant permissions to principals, which is the duty of another sub-system
known as the **securitypolicy*.

BlueBream does not enforce any particular security policy.  In contrary, it
encourages developers to carefully choose the security policy and use one
that fits their needs best.  The default BlueBream distribution comes with a
default security policy (``securitypolicy.zcml``) that supports the concept
of roles.  Roles are like hats people wear, as Jim Fulton would say, and can
be seen as a collection of permissions.  A single user can have several
hats, but only wear one at a time.  Prominent examples of roles include
*editor* and *administrator*.  Therefore, the default security policy
supports mappings from permissions to principals, permissions to roles, and
roles to principals.  This chapter will use the default security policy to
setup the security, but will clearly mark the sections that are security
policy specific.

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

Delcarations of Permissions
---------------------------

Permissions have to be explicitly defined.  For our ticket collector it will
suffice to define the following four basic permissions:

*View* - Allow users to access the data for tickets and comments.  Every
regular ticket collector user is going to have this permission.

*Add* - Allows someone to add a ticket or comment on tickets.  Note that
every regular user is allowed to do this, since adding tickets and
commenting must be possible.

*Edit* - Editing ticket details (after it is created) is only a permission
given to the Admin possesses (for moderation), since we would not want a
regular user to be able to manipulate tickets after creation.

*Delete* - The Admin must be able to get rid of messages, of course.
Therefore the Delete permission is assigned to her.  Note that this
permission does not allow the Admin to delete ticket collector objects.

Let's define the permissions now.  Note that they must appear at the very
beginning of the configuration file, so that they will be defined by the
time the other directives (that will use the permissions) are executed.
Here are the four directives you should add to your main ``configure.zcml``
file:

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
      title="Edit tickets"
      description="Edit tickets."
      />
  <permission
      id="tc.Delete"
      title="Delete ticket"
      description="Delete ticket."
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

Using the Permissions
---------------------

Now that we have defined these permissions, we also have to use them; let's
start with the main ticket collector configuration file
(``src/tc/main/configure.zcml``).  In the following walk-through we are only
going to use the last part of the permission name to refer to the
permission, leaving off ``tc.``.  However, the full *id* has to be specified
for the configuration to execute.

Change the first `require` statement of in the ticket collector content
directive to use the `View` permission (line 42).  This makes the
description and the items accessible to all users.  Similarly, change line
64 for the ticket.

Change the permission of line 46 to `Edit`, since only the message board
administrator should be able to change any of the properties of the
MessageBoard object.

All the container functionality will only require the view permission, so
change the permission on line 68 to `View`.  This is unsecure, since this
includes read and write methods, but it will suffice for this demonstration.

For the Message we need to be able to set the attributes with the `Add`
permission, so change line 72 to specify this permission.

Now let's go to the browser configuration file
(``src/tc/main/configure.zcml``) and fix the permissions there.

The permissions for the message board's add form (line 11), add menu item
(line 18), and its edit form (line 27) stay unchanged, since only an
administrator should be able manage the board.

Since we want every user to see the messages in a messageboard, the
permission on line 33 should become `View`.  Since the contents view is
meant for management, only principals with the `Edit` permission should be
able to see it (line 34).  Finally, you need the Add permission to actually
add new messages to the message board (line 35).  The same is true for the
message's container views permissions (line 84-86).

Since all user should be able to see the message thread and the message
details, the permissions on line 43, 94, and 106 should become `View`.

On line 61 you should change the permission to `Add`, because you only allow
messages to be added to the message board, if the user has this
permission. The same is true for the message's add menu item on line 68.

On line 78 make sure that a user can only access the edit screen if he has
the `Edit` permission.

That's it.  If you would restart Zope 3 at this point, you could not even
access the MessageBoard and/or Message instances. Therefore we need to
create some roles next and assign permissions to them.

Declaration of Roles
--------------------

The declaration of roles is specific to Zope 3's default security policy.
Another security policy might not even have the concept of roles at all.
Therefore, the role declaration and grants to the permissions should not
even be part of your package.  For simplicity and keeping it all at one
place, we are going to store the policy-specific security configuration in
security.zcml.  For our message board package we really only need two roles,
*User* and *Editor*, which are declared as follows::

  <role
      id="tc.User"
      title="Ticket collector User"
      description="Users that actually use the Message Board."/>
  
  <role
      id="tc.Editor"
      title="Message Board Editor"
      description="The Editor can edit and delete Messages."/>

Equivalently to the zope:permission directive, the zope:role directive
creates and registers a new role with the global role registry.  Again, the
id must be a unique identifier that is used throughout the configuration
process to identify the role.  Both, the id and the title are required.

Next we grant the new permissions to the new roles, i.e. create a
permission-role map.  The user should be only to add and view messages,
while the editor is allowed to execute all permission.

::

  <grant
      permission="book.messageboard.View"
      role="book.messageboard.User"
      />
  <grant
      permission="book.messageboard.Add"
      role="book.messageboard.User"
      />
  <grant
       permission="book.messageboard.Edit"
       role="book.messageboard.Editor"
       />
   <grant
       permission="book.messageboard.Delete"
       role="book.messageboard.Editor"
       />

The zope:grant directive is fairly complex, since it permits all
three different types of security mappings. It allows you to assign a
permission to a principal, a role to a principal, and a permission to
a role. Therefore the directive has three optional arguments:
permission, role, and principal. Exactly two of the three arguments
have to be specified to make it a valid directive. All three security
objects are specified by their id.

Finally, you have to include the security.zcml file into your other
configuration. This is simply done by adding the following inclusion
directive in the ZOPE3/principals.zcml file::

  <include package="book.messageboard" file="security.zcml" />

The reason we put it here is to make it obvious that this file
depends on the security policy. Also, when assigning permissions to
roles we want all possible permissions the system can have to be
defined. Since the principals.zcml file is the last ZCML to be
evaluated, this is the best place to put the declarations.

Assigning Roles to Principals
-----------------------------

To make our package work again, we now have to connect the roles to
some principals. We are going to create two new principals called
boarduser and boardeditor. To do that, go to the Zope 3 root
directory and add the following lines to principals.zcml:


  <principal
      id="book.messageboard.boarduser"
      title="Message Board User"
      login="boarduser" password="book"
      />
  <grant
      role="book.messageboard.User"
      principal="book.messageboard.boarduser"
      />
   
   <principal
       id="book.messageboard.boardeditor"
       title="Message Board Editor"
       login="boardeditor" password="book"
       />
   <grant
       role="book.messageboard.User"
       principal="book.messageboard.boardeditor"
       />
   <grant
       role="book.messageboard.Editor"
       principal="book.messageboard.boardeditor"
       />

The zope:principal directive creates and registers a new
principal/user in the system.  Like for all security object
directives, the id and title attributes are required.  We could also
specify a description as well.  In addition to these three
attributes, the developer must specify a login and password (plain
text) for the user, which is used for authentication of course.

Note that you might want to grant the book.messageboard.User role to
the zope.anybody principal, so that everyone can view and add
messages.

The zope.anybody principal is an unauthenticated principal, which is
defined using the zope:unauthenticatedPrincipal directive, which has
the same three basic attributes the zope:principal directive had, but
does not accept the login and password attribute.

Now your system should be secure and usable.  If you restart Zope 3
now, you will see that only the message board's Editor can freely
manipulate objects.  (Of course you have to log in as one.)


Conclusion
----------

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
