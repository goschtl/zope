.. _howto-default-view:

Default view for objects
========================

In BlueBream, a browser view can be accessed using ``@@`` symbols
before the view name.  For example, if you have registered a view
named ``testview`` for a container object named ``myobject``, that
view can be accessed like this: ``myobject/@@testview``.

.. note::

  Container object -- Any object implementing
  ``zope.content.interfaces.IContainer`` interface is called a
  contenter object.

The view could be accessed without using the ``@@`` symbols also,
provided there is no content object with the same same exist inside
the container.  In the above example, If there is no content object
named ``testview`` inside ``myobject`` container, then, the view can
be accessed like ``myobject/testview``.  However, BlueBream
recommend, always to use ``@@`` symbols to access view to avoid
ambiguity.

.. note::

   Content Object -- If an **interface** provides
   ``zope.app.content.interfaces.IContentType`` interface type, then
   all objects providing the **interface** are considered content
   objects.

In BlueBream, ``index`` is registered as the view name for
``zope.container.interfaces.IContainer`` interface.  So, if you try
to access any container object without specifying any view name,
BlueBream will try to display the view registered with name as
``index``.

You can configure the name of default view for a particular type of
object with ``browser:defaultView`` directive available in
``zope.publisher`` package.  If the name of default view is not
configured, and when you try to access an object without specifying
the view name, you will get a ``ComponentLookupError`` with a message
like this: ``Couldn't find default view name``.  For example, if you
try to access the root folder like: http://localhost:8080/ and name of
default view is not configured, you will get an error like this::

  ComponentLookupError: ("Couldn't find default view name",
  <zope.site.folder.Folder object at 0xa3a09ac>,
  <zope.publisher.browser.BrowserRequest instance
  URL=http://localhost:8080>)

.. note::

   In order to use any ZCML except few built-ins like ``configure``
   and ``include``, you include the ZCML where it is defined the
   directive, conventionally in BlueBream it will be inside
   ``meta.zcml`` for any package.  For example, to use
   ``defaultView`` directive, you need to include ``meta.zcml`` file
   inside ``zope.publisher``::

     <include package="zope.publisher" file="meta.zcml" />


If you have created the application using the ``bluebream`` project
template, you won't get this error.  Because there is already a a
default view name (``index``) is configured in ``application.zcml``
configuration file inside the main package.

If there is a default view name configured, but there is no view
registered with that name, you will get ``NotFound`` error when you
try to access object directly without specifying the name of view.
For example, if the default view name is ``index`` and there is no
such view registered for root folder, you will get an error like
this::

  NotFound: Object: <zope.site.folder.Folder object at 0xac9b9ec>,
  name: u'@@index'

As mentioned earlier, the ``browser:defaultView`` directive is
defined in ``zope.publisher``.  To use this directive, you need to
include ``meta.zcml`` using ``include`` directive::

  <include package="zope.publisher" file="meta.zcml" />

For example, you can specify the default view for ``IContainer`` like
this::

  <browser:defaultView
     name="index"
     for="zope.container.interfaces.IContainer"
     />

If ``index`` is registered as the name for default view and the view
is not explicitly mentioned in the URL, BlueBream will try to get
``@@index`` view for containers.  However, you need to have a browser
view registered to access the view, otherwise a ``NotFound`` error
will be raised as mentioned above.

More details about registering a browser view using ``browser:page``
directive is explained in :ref:`man-browser-page` manual.

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
