
============================
Trails: URL Recipes for Grok
============================

Cave men often hunted by following animal trails through the woods.
They could also follow trails to important natural resources; the very
first human migrations may have been along the trails that migratory
animal herds created when visiting natural salt deposits.

In the same tradition, the Trails product, which lives in the
``megrok.trails`` package, allows Grok web site developers to define the
URLs that web users can travel in order to visit the objects that roam
your site.  It creates both the traversers which make the URLs work in
the forward direction (so that users can visit them and see the right
objects), and also registers the adapters necessary for URLs to work in
reverse (meaning that Grok can ask "where does this object live?" and
receive back an answer).

Trails look something like this when in use::

    class MyTrails(megrok.trails.TrailHead):
        grok.context(MyApp)
        trails = [
            Trail('/person/:id', Person),
            Trail('/account/:username', Account),
            ]

The above example makes a URL like::

    http://example.com/app/person/3096

traverse to the object created by calling ``Person(id=3096)``, while a
user visiting the URL::

    http://example.com/app/account/dcr

will find the object created by calling ``Account(username=dcr)``.  In
each case, the colon-prefixed URL elements in the Trail become keyword
arguments passed to the class (or other object constructor) given as the
second argument to ``Trail()``.  Each URL element that is not prefixed
with a colon must be matched literally by the corresponding element in
the submitted URL.

A ``TrailHead`` takes over traversal for the object which you name as
its ``grok.context()``, so you do not have to define a ``traverse()``
method or create a ``grok.Traverser`` for that context yourself.  When
the URL components that follow fail to match any of the ``Trail``
patterns that start from that ``TrailHead``, an error is raised that
should return a ``404 Not Found`` to the user.  If, instead, one of the
URL patterns is matched, then the object named in the second argument of
the ``Trail`` is instantiated with the colon-prefixed wildcard URL
components provided as keyword parameters, as outlined above.

Once the trail has been matched and resolved to an object, Trails is
done processing, and normal Grok traversal then takes over again to
process any remaining URL components, or to look for a default view for
the object if the end of the URL has been reached.  So, in the above
example, the developer would need to have provided normal ``grok.View``
classes for the ``Person`` and ``Account`` objects in order for the user
to see them rendered in a browser.  This means that Trails is not
comparable to something like `Rails Routes`_ or `Python Routes`_,
because those products impose their own methods for choosing the view
that gets placed atop an object.  Trails, by contrast, leaves the normal
Grok rules in place for how a view is selected and placed atop your
object; it merely attempts to make object traversal itself cleaner and
easier to maintain in an application where objects and containers do not
literally exist in an object database like the ZODB.

.. _Rails Routes: http://manuals.rubyonrails.com/read/book/9
.. _Python Routes: http://routes.groovie.org/

Note that Trails stops, satisfied, once any ``Trail`` has been
completed, and returns control to Grok.  You cannot, therefore, have two
working trails where one is a prefix of the other; the second ``Trail``
shown here will never be used::

    trails = [
        Trail('/person/:id', Person),
        Trail('/person/:id/:acct', BankAccount), # will never be used!
        ]

Remember that Trails also registers adapters that tell Grok where each
kind of object lives, so that if you, for example, are rendering a page
full of ``Person`` objects as part of a search result, then you can call
``view.url(person)`` on each of them and Trails will construct URLs for
them that are built like::

    application_url + '/person/%s' % person.id

If your trail had said something more ambitious, like::

    Trail('/town/:name/:state', Town)

then the URL of any particular town would be formed by computing::

    application_url + '/town/%s/%s' % (town.name, town.state)

and might look like ``/town/Springfield/MA``.  Note that this means that
Trails makes two assumptions about every class that you name as the
second argument to a ``Trail``: first, that it can safely be called with
keyword arguments that look like the colon-prefixed wildcards that form
the URL pattern; and, second, that any live object of that type will
have attributes with those same two names which it can look up to form a
URL for the object.

If you have suggestions, bug reports, or questions about Trails, please
visit our project page at Launchpad::

    https://launchpad.net/megrok.trails
