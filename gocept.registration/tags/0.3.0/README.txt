======================
User self-registration
======================

This package provides functionality to implement user self-registration for
applications.

The general workflow requires that every user provides at least his email
address but additional data may be provided, too.  After a user registered, an
email is send out asking him to confirm his identity by clicking a link that
is embedded in the email.  Once a registration is confirmed, the temporarily
stored registration data is deleted.

Applications can customize the registration behaviour by subscribing to events
for registration and confirmation and providing application-specific views and
adapters for registration and email creation.

There is a demo application included in this package/buildout that shows how
to use the basic views available to quickly create registration and
confirmation views and customized emails for your application. Both the views
and the email generation provide a good degree of flexibility so they can be
re-used directly, but you can also provide your own.
