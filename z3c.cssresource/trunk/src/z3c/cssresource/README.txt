==================
CSS File Resources
==================

One of the design goals of Zope is to allow designers to check in HTML
template, CSS and Javascript files, which just work (with some additional
information). For templates we use Zope's Page Templates to accomplish this
objective. For CSS and Javascript we did not need such a feature, since
nothing should be dynamic, due to chaching.

However, now URLs -- for example for background images -- are frequently
inserted into CSS files. However, the path layout for the designer might not
equal that to the resource file structure. This package provides a simple
mechanism to replace strings by another.

To accomplish this task, a custom CSS file resource is provided. The replace
syntax is provided inside CSS comments. The commands are as follows:

- ``/* zope-global-replace: "ORIGINAL" "FINAL" */``

(Yes, for now it is only one.)

To demonstrate this feature, we first have to create a CSS file.

  >>> import tempfile
  >>> fn = tempfile.mktemp('.css')
  >>> open(fn, 'w').write('''\
  ... /* zope-global-replace: "../img1" "++resource++/img" */
  ... h1 {
  ...   color: red;
  ...   background: url('../img1/mybackground.gif');
  ... }
  ...
  ... h2 {
  ...   color: red;
  ...   background: url('../img2/mybackground.gif');
  ... }
  ... /* zope-global-replace: "../img2" "++resource++/img" */
  ... ''')

As you can see, the command can be placed anywhere.

Now we create a CSS resource from the resource factory:

  >>> from z3c.cssresource import CSSFileResourceFactory
  >>> cssFactory = CSSFileResourceFactory(fn, None, 'site.css')

  >>> from zope.publisher.browser import TestRequest
  >>> css = cssFactory(TestRequest())

  >>> print css.GET()
  h1 {
    color: red;
    background: url('++resource++/img/mybackground.gif');
  }
  <BLANKLINE>
  h2 {
    color: red;
    background: url('++resource++/img/mybackground.gif');
  }
  <BLANKLINE>

And that's all! In your ZCML you can use this factory as follows::

  <resource
      name="site.css"
      path="css/site.css"
      factory="z3c.cssresource.CSSFileResourceFactory"
      />


Global Replace
--------------

As seen in the example above, ``zope-global-replace`` calls can be placed
anywhere in the file. Let's make sure that some special cases work as well:

  >>> from z3c.cssresource import CSSFileResource
  >>> resource = CSSFileResource(None, None)

  >>> print resource.process('''\
  ...        /* zope-global-replace: "foo" "bar" */
  ... foo''')
  bar

  >>> print resource.process('''\
  ... /*      zope-global-replace: "foo" "bar"      */
  ... foo''')
  bar

  >>> print resource.process('''\
  ... /* zope-global-replace:   "foo"         "bar" */
  ... foo''')
  bar

But the following does not work:

  >>> print resource.process('''\
  ... /* zope-global-replace : "foo" "bar" */
  ... foo''')
  /* zope-global-replace : "foo" "bar" */
  foo

  >>> print resource.process('''\
  ... /* zope -global-replace : "foo" "bar" */
  ... foo''')
  /* zope -global-replace : "foo" "bar" */
  foo


