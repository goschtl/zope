.. _commu-browser-resource:

Browser Resource
================

Package: `z3c.zrtresource <http://pypi.python.org/pypi/z3c.zrtresource>`_

Zope Resource Templates (ZRT) allows for locally working resources to
work with BlueBream as well.  It will rewrite text segments in a
resource.  It is a 3rd party package developed by Stephan Richter for
Lovely Systems.

ZRT Resource
------------

When working locally, you may be storing your image resources in a
directory.  If you have a subfolder called images with an image
logo.png.  And you have a template, so here is the HTML to insert the
logo::

     <img src="./images/logo.png" />

Now you can see that the template locally works.  If you view the
HTML via Zope, you can see that it is broken.  Now, let's try to
register the logo with the system like this::

     <resource
        name="logo.png"
        file="images/logo.png"
        />

Now try again, after restarting Zope 3, you can see that it is still
broken!.  So, relative path is not correct.

Add the following lines to the HTML resource::

     <!--
      /* zrt-replace: "./images/logo.png" \
                      tal"string:${context/++resource++logo.png}" */
     -->

Then convert HTML resource registration to::

     <zrt-resource
        name="helloworld.html"
        file="helloworld.html"
        />
