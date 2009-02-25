Browser Resources
=================

.. index:: browser resource

Introduction
------------

Certain presentation, like images and style sheets are not associated
with any other component, so that one cannot create a view.  To solve
this problem, resources were developed, which are presentation
components that do not require any context.  This mini-chapter will
demonstrate how resources are created and registered with Zope 3.


File resource
-------------

.. index::
   single: file resource; browser resource

The first goal is to register a simple plain-text file called
`resource.txt` as a browser resource.  The first step is to create
this file anywhere you wish on the filesystem, and adding the
following content::

  Hello, I am a Zope 3 Resource Component!

Then, register the resource in a ZCML configuration file using the
`browser` resource directive::

  <browser:resource
    name="resource.txt"
    file="resource.txt"
    layer="default"
    />

Line 2: This is the name under which the resource will be known in
Zope.

Line 3: The file attribute specifies the path to the resource on the
filessytem.  The current working directory ('.') is always the
directory the configuration file is located.  So in the example
above, the file `resource.txt` is located in the same folder as the
configuration file is.

Line 4: The optional layer attribute specifies the layer the resource
is added to.  By default, the default layer is selected.

Once you hook up the configuration file to the main configuration
path and restart Zope 3, you should be able to access the resource
now via a Browser using `http://localhost:8080/@@/resource.txt`.  The
`@@/` in the URL tells the traversal mechanism that the following
object is a resource.


Image resource
--------------

.. index::
   single: image resource; browser resource

If you have an image resource, you might want to use different
configuration.  Create a simple image called `img.png` and register
it as follows::

  <browser:resource
    name="img.png"
    image="img.png"
    permission="zope.ManageContent"
    />

Line 3: As you can see, instead of the `file` attribute we use the
`image` one.  Internally this will create an `Image` object, which is
able to detect the content type and returns it correctly.  There is a
third possible attribute named `template`.  If specified, a Page
Template that is executed when the resource is called.  Note that
only one of `file`, `image`, or `template` attributes can be
specified inside a resource directive.

Line 4: A final optional attribute is the ''permission'' one must
have to view the resource.  To demonstrate the security, I set the
permission required for viewing the image to `zope.ManageContent`, so
that you must log in as a manager to be able to view it.  The default
of the attribute is `zope.Public` so that everyone can see the
resource.


Directory resource
------------------

.. index::
   single: directory resource; browser resource

If you have many resource files to register, it can be very tedious
to write a single directive for every resource.  For this purpose the
`resourceDirectory` is provided, with which you can simply declare an
entire directory, including its content as resources.  Thereby the
filenames of the files are reused as the names for the resource
available.  Assuming you put your two previous resources in a
directory called resource, then you can use the following::

  <browser:resourceDirectory
    name="resources"
    directory="../resource"
    />

The image will then be publically available under the URL:
`http://localhost:8080/@@/resources/img.png`

The `DirectoryResource` object uses a simple resource type
recognition.  It looks at the filename extensions to discover the
type.  For page templates, currently the extensions ''pt'', ''zpt''
and ''html'' are registered and for an image ''gif'', ''png'' and
''jpg''.  All other extensions are converted to file resources.  Note
that it is not necessary to have a list of all image types, since
only Browser-displayable images must be recognized.


ZRT resource
------------

.. index::
   single: zrt resource; browser resource

While working with CSS and JavaScript resource files, it would be
useful if it works locally as well as with Zope 3.  This will help us
to test those files without running application server.  Zope
Resource Templates (ZRT) allows for locally working resources to work
with Zope 3 as well.  It will rewrite text segments in a resource.
It is a Zope 3 community package originally developed by Stephan
Richter for Lovely Systems.  The package is available from PyPI_.

.. _PyPI: http://pypi.python.org/pypi/z3c.zrtresource


Installation
~~~~~~~~~~~~

- Go to setup.py

- Add `z3c.zrtresource` to the `install_requires` list making it a
  new dependency.

- In application.zcml, add::

    <include package="z3c.zrtresource" file="meta.zcml" />


Usage
~~~~~

Explaining the idea of ZRT with CSS or JavaScript will be bit
lengthy.  So, here we are going for unrealistic example with an HTML
file as the resource file.

When working locally, you may be storing your image resources in a
directory.  If you have a subfolder called `images` with an image
`logo.png`.  And you have a resource html file with the following
content to display the logo::

  <html>
  <img src="./images/logo.png" />
  </html>

Here is the html resource file registration::

  <browser:resource
    name="helloworld.html"
    file="helloworld.html"
    />

Now you can see that the template locally works.  You can access this
resource at via Zope at `http://localhost:8080/@@/helloworld.html`
(Replace the `8080` port with the actual one).  Then, if you view the
HTML via Zope, you can see that it is broken.  This is because the
logo image resource is not available.  Now, let's try to register the
logo with the system like this::

  <browser:resource
    name="logo.png"
    file="images/logo.png"
    />

Now try again, after restarting Zope 3, you can see that it is still
broken!.  This reason is the relative path to image is not correct.
The location of logo resource will be at
http://localhost:8080/@@/logo.png .

This problem can be solved using ZRT resource.  To use the
`zrt-resource` add the following lines to the resource html file::

  <!--
  /*
    zrt-replace: "./images/logo.png" tal"string:${context/++resource++logo.png}"
  */
  -->

Then change resource registration like this::

  <browser:zrt-resource
    name="helloworld.html"
    file="helloworld.html"
    />

Now, if you try to access the `helloworld.html`, you can see that the
image is rendering properly.  For XML-based files we could have also
have used TAL, thus ZRT resources are most interesting for CSS and
JavaScript files.  To use TAL for resources, simply have the template
end in .pt instead of .html.


Summary
-------

This chapter introduced browser resources and narrated its usage.
Finally we have covered ZRT resource also.
