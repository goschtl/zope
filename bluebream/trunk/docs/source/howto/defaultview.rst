Default view for objects
========================

Normally in BlueBream, a browser view can be accessed using ``@@``
symbols before the view name.  For example, if you have registered a
view named ``testview`` for an object, that view can be accessed like
this: ``myobject/@@testview``.

The view could be accessed without using the ``@@`` symbols also,
provided there is no object with same same exist inside the
container.  In the above example, If there is no object named
``testview`` inside ``myobject`` container, then, the view can be
accessed like ``myobject/testview``.  However, BlueBream reccommends
to use ``@@`` symbols always to access view to avoid ambiguity.

If you try to access an object without specifying any view name,
BlueBream will try to display the default view registered.  You can
configure the name os default view for a particular type object using
``browser:defaultView`` directive available in ``zope.publisher``
package.  If the name of default view is not configured, and you try
to access an object without specifying the view name, you will get a
``ComponentLookupError`` with a message like this: ``Couldn't find
default view name``.  For example, if you try to access the root
folder like: htt://localhost:8080/ and name of default view is not
configured, you will get an error like this::

  ComponentLookupError: ("Couldn't find default view name",
  <zope.site.folder.Folder object at 0xa3a09ac>,
  <zope.publisher.browser.BrowserRequest instance
  URL=http://localhost:8080>)

If you have created the application using ``bluebream`` project
template, you won't get this error.  Beacause there is already a a
default view name (``index``) is configured in ``application.zcml``
configuration file inside the main package.

If there is a default view name configured, but that there is no view
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

If ``index`` is registered as the name for default view, BlueBream
will try to get ``@@index`` view for any containers, if the view is
not explicitly mentioned in the URL.  However, you need to have a
browser view registered to acces the view, otherwise a ``NotFound``
error will be raised as mentioned above.

More details about registering a browser view using ``browser:page``
directive is explained in `browser page HOWTO <browserpage.html>`_.

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
