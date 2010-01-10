Default view for objects
========================

Normally in BlueBream, a browser view can be accessed using ``@@``
symbol before the view name.  For example, if you have registered a
view named ``testview`` for an object, it can be accessed like this:
``myobject/@@testview``.

The view could be accessed without using the ``@@`` symbol also,
provided there is no object with same same exists inside the
container.  In the above example, If there is no object named
``testview`` inside ``myobject`` container, then, the view can be
accessed like this: ``myobject/testview``.  BlueBream reccommends to
use ``@@`` symbol always to access view.

If you access an object without specifying any view, BlueBream will
try to display the default view registered.  You can specify what
should be the default view for a particular type object using
``browser:defaultView`` directive .  If there is no default view
registered, and then you try to access an object without specifying
the view, you will get a ``ComponentLookupError`` with a message
like: ``Couldn't find default view name``.  For example, if you
access the root folder and there is no default view registered, you
will get an error like this::

  ComponentLookupError: ("Couldn't find default view name",
  <zope.site.folder.Folder object at 0xa3a09ac>,
  <zope.publisher.browser.BrowserRequest instance
  URL=http://localhost:8080>)

If you created the application using ``bluebream`` project template,
you won't get this error.  Beacause there is already a
``defaultView`` configured in ``application.zcml`` configure file
inside the main package.  Now if there is a default view name
configured, but that there is no view registed in that name, you will
get ``NotFound`` error.  For example, if the defaultView is ``index``
and there is no such view registered for root folder, you will get an
error like this::

  NotFound: Object: <zope.site.folder.Folder object at 0xac9b9ec>,
  name: u'@@index'

The ``browser:defaultView`` directive is defined in
``zope.publisher``.  To use this directive, you need to include
``meta.zcml`` using ``include`` directive::

  <include package="zope.publisher" file="meta.zcml" />

You can specify the default view for ``IContainer`` like this ::

  <browser:defaultView
     name="index"
     for="zope.container.interfaces.IContainer"
     />

Now, BlueBream will try to get ``@@index`` view for any containers,
if the view is not explicitly mentioned in the URL.

More details about registering a browser page using ``browser:page``
directive is explained in `browser page HOWTO <browserpage.html>`_.

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
