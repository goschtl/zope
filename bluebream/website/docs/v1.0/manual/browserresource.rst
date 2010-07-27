.. _man-browser-resource:

Browser Resource
================

File Resource
-------------

Certain presentation, like images and style sheets are not associated
with any other component, so that one cannot create a view.  To solve
this problem, resources were developed, which are presentation
components that do not require any context.  This chapter will
demonstrate how resources are created and registered with BlueBream.

The first goal is to register a simple plain-text file called
``resource.txt`` as a browser resource.  The first step is to create
this file anywhere you wish on the filesystem, and adding the
following content.  If you are working on the official tutorial, you
can create the file at: ``src/tc/main/resource.txt``::

  Hello, I am a BlueBream Resource Component!

Now just register the resource in a ZCML configuration file using the
browser resource directive.  If you are working on the official
tutorial, you can add these lines to ``src/tc/main/configure.zcml``::

  <browser:resource
      name="resource.txt"
      file="resource.txt"
      layer="default" />

- Line 2: This is the name under which the resource will be known in
  Zope.

- Line 3: The file attribute specifies the path to the resource on
  the filessytem.  The current working directory (``.``) is always
  the directory the configuration file is located.  So in the example
  above, the file ``resource.txt`` is located in the same folder as
  the configuration file is.

- Line 4: The optional layer attribute specifies the layer the
  resource is added to.  By default, the default layer is selected.

Once you hook up the configuration file to the main configuration
path and restart BlueBream, you should be able to access the resource
now via a Browser at: http://localhost:8080/@@/resource.txt.  The
``@@/`` in the URL tells the traversal mechanism that the following
object is a resource.

Image Resource
--------------

If you have an image resource, you might want to use different
configuration.  Create a simple image called ``img.png`` and register
it as follows::

  <browser:resource
      name="img.png"
      image="img.png"
      permission="zope.ManageContent" />

- Line 3: As you can see, instead of the file attribute we use the
  image one.  Internally this will create an Image object, which is
  able to detect the content type and returns it correctly.  There is
  a third possible attribute named template.  If specified, a Page
  Template that is executed when the resource is called.  Note that
  only one of file, image, or template attributes can be specified
  inside a resource directive.

- Line 4: A final optional attribute is the ``permission`` one must
  have to view the resource.  To demonstrate the security, I set the
  permission required for viewing the image to
  ``zope.ManageContent``, so that you must log in as an
  administrator/manager to be able to view it.  The default of the
  attribute is ``zope.Public`` so that everyone can see the resource.


Directory Resource
------------------

If you have many resource files to register, it can be very tedious
to write a single directive for every resource.  For this purpose the
``browser:resourceDirectory`` directive is provided, with which you
can simply declare an entire directory, including its content as
resources.  Thereby the filenames of the files are reused as the
names for the resource available.  Assuming you put your two previous
resources in a directory called ``resource``, then you can use the
following::

  <browser:resourceDirectory
    name="resource"
    directory="resource"
    />

The image will then be publically available from the following URL:
http://localhost:8080/@@/resources/img.png

The directory resource object uses a simple resource type
recognition.  It looks at the filename extensions to discover the
type.  For page templates, currently the extensions ``pt``, ``zpt``
and ``html`` are registered and for an image ``gif``, ``png`` and
``jpg``.  All other extensions are converted to file resources.  Note
that it is not necessary to have a list of all image types, since
only Browser-displayable images must be recognized.

In BlueBream, there is a resource directory registered named
``static``.  If you are working the tutorial, you can see it at:
``src/tc/main/configure.zcml``.  At the beginning of the file, you
can see the registration like this::

  <browser:resourceDirectory
     name="static"
     directory="static"
     />

Two resource files (``style.css`` and ``logo.png``) will be already
available inside ``src/tc/main/static`` directory.

There is a community supported package named `z3c.zrtresource
<http://pypi.python.org/pypi/z3c.zrtresource>`_ which provides a
better way to register & use resources.  For more information, look
at the documentation: :ref:`commu-browser-resource`.


.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
