===================
Templated Resources
===================

One of the design goals of Zope is to allow designers to check in HTML
template, CSS and Javascript files, which just work (with some additional
information). For HTML code we use Zope's Page Templates to accomplish this
objective. For CSS and Javascript we did not need such a feature until now,
since those files were largely static or variables could be inserted using
other ways at runtime.

However, in CSS URLs -- for example for background images -- are now
frequently inserted into CSS directives. However, the path layout for the
designer might not equal the resource file structure. This package provides a
simple mechanism to replace strings by another.

To accomplish this, a templated resource is provided. The template syntax is
provided in a way that it does not interfere with the syntax of the
resource. For both, Javascript and CSS, this is a comment of the form ``/*
... */``.

Here is the general syntax::

  <COMMAND-BEGIN> <ZRT-COMMAND>: <COMMAND-ARGUMENTS> <COMMAND-END>

Here is an example for CSS::

    /* zrt-replace: ".." "@@" */

To demonstrate this feature, we first have to create a CSS file.

  >>> import tempfile
  >>> fn = tempfile.mktemp('.css')
  >>> open(fn, 'w').write('''\
  ... /* zrt-replace: "../img1" "++resource++/img" */
  ... /* zrt-replace: "fontName" "Arial, Tahoma" */
  ... h1 {
  ...   color: red;
  ...   font: fontName;
  ...   background: url('../img1/mybackground.gif');
  ... }
  ...
  ... h2 {
  ...   color: red;
  ...   background: url('../img2/mybackground.gif');
  ... }
  ... /* zrt-replace: "../img2" "++resource++/img" */
  ... ''')

The global replace command replaces a string with another. It is only active
in the lines *after* it was declared. Thus, in this case, the second command
is meaningless.

Now we create a ZRT resource from the resource factory ...

  >>> from z3c.zrtresource import ZRTFileResourceFactory
  >>> cssFactory = ZRTFileResourceFactory(fn, None, 'site.css')

  >>> from zope.publisher.browser import TestRequest
  >>> css = cssFactory(TestRequest())

and render the resource:

  >>> print css.GET()
  h1 {
    color: red;
    font: Arial, Tahoma;
    background: url('++resource++/img/mybackground.gif');
  }
  <BLANKLINE>
  h2 {
    color: red;
    background: url('../img2/mybackground.gif');
  }

As you can see only the first URL was replaced, because of the incorrect
position of the second statement.

And that's all! In your ZCML you can use this factory as follows::

  <zrt-resource
      name="site.css"
      path="css/site.css"
      />


Replacing Strings
-----------------

The ``zrt-replace`` command replaces any matches with the output string as
many times as specified. Here is the syntax:

  zrt-replace: <EXPR-TYPE>"<INPUT-EXPR>" <EXPR-TYPE>"<OUTPUT-EXPR>" <NUM>

As seen in the example above, ``zrt-replace`` calls can be placed
anywhere in the file. Let's make sure that some special cases work as well:

  >>> from z3c.zrtresource import processor, replace
  >>> def process(text):
  ...     p = processor.ZRTProcessor(
  ...         text, commands={'replace': replace.Replace})
  ...     return p.process(None, None)

  >>> print process('''\
  ...        /* zrt-replace: "foo" "bar" */
  ... foo''')
  bar

  >>> print process('''\
  ... /*      zrt-replace: "foo" "bar"      */
  ... foo''')
  bar

  >>> print process('''\
  ... /* zrt-replace:   "foo"         "bar" */
  ... foo''')
  bar

But the following does not work:

  >>> print process('''\
  ... /* zrt-replace : "foo" "bar" */
  ... foo''')
  /* zrt-replace : "foo" "bar" */
  foo

  >>> print process('''\
  ... /* zrt -replace : "foo" "bar" */
  ... foo''')
  /* zrt -replace : "foo" "bar" */
  foo

Until now we have only considered multiple replacements. Let's now restrict
the number of replacements with the final argument. Initially all occurences
of a matching string are replaced:

  >>> print process('''\
  ... /* zrt-replace: "foo" "bar" */
  ... foo foo foo foo foo''')
  bar bar bar bar bar

When we specify a number of replacements, then only that amount is replaced:

  >>> print process('''\
  ... /* zrt-replace: "foo" "bar" 1 */
  ... foo foo foo foo foo''')
  bar foo foo foo foo

  >>> print process('''\
  ... /* zrt-replace: "foo" "bar" 3 */
  ... foo foo foo foo foo''')
  bar bar bar foo foo

  >>> print process('''\
  ... /* zrt-replace: "foo" "bar" 6 */
  ... foo foo foo foo foo''')
  bar bar bar bar bar


The String Expression
~~~~~~~~~~~~~~~~~~~~~

Until now we have only dealt with simple string replacement, since it is the
default expression type. Another way of spelling the expression type is:

  >>> print process('''\
  ... /* zrt-replace: str"foo" "bar" */
  ... foo''')
  bar

  >>> print process('''\
  ... /* zrt-replace: "foo" str"bar" */
  ... foo''')
  bar

  >>> print process('''\
  ... /* zrt-replace: str"foo" str"bar" */
  ... foo''')
  bar


The Regex Expression
~~~~~~~~~~~~~~~~~~~~

Regular expressions make only sense as input expressions, so they are only
supported there:

  >>> print process('''\
  ... /* zrt-replace: re"foo" "bar" */
  ... foo''')
  bar

  >>> print process('''\
  ... /* zrt-replace: re"[a-z]*foo" "bar" */
  ... myfoo''')
  bar

We also support groups:

  >>> print process('''\
  ... /* zrt-replace: re"([a-z]*)foo" "bar" */
  ... myfoo''')
  bar

  >>> print process('''\
  ... /* zrt-replace: re"([a-z]*)foo" "bar" */
  ... myfoo''')
  bar

  >>> print process('''\
  ... /* zrt-replace: re"([a-z]*)foo" "bar" */
  ... myfoo mybar''')
  bar mybar

Yes, even group replacement works:

  >>> print process('''\
  ... /* zrt-replace: re"([a-z]*)foo" "bar\\1" */
  ... myfoo a9foo''')
  barmy a9bar

  >>> print process('''\
  ... /* zrt-replace: re"(?P<prefix>[a-z]*)foo" "bar\\g<prefix>" */
  ... myfoo a9foo''')
  barmy a9bar


The TALES Expression
~~~~~~~~~~~~~~~~~~~~

What would be a Zope-based templating language without TALES expressions? This
is particularly useful, if you want to create absolute URLs and other dynamic
bits based on the request and the context:

  >>> import zope.interface
  >>> from zope.traversing.interfaces import IContainmentRoot
  >>> class Root(object):
  ...     zope.interface.implements(IContainmentRoot)

  >>> from zope.publisher.browser import TestRequest
  >>> def process(text):
  ...     p = processor.ZRTProcessor(
  ...         text, commands={'replace': replace.Replace})
  ...     return p.process(Root(), TestRequest())

  >>> print process('''\
  ... /* zrt-replace: "foo" tal"string:${context/@@absolute_url}/@@/foo" */
  ... foo''')
  http://127.0.0.1/@@/foo


Custom ZRT Command
~~~~~~~~~~~~~~~~~~

We can create custom ZRT commands.  For this we should register
a named IZRTCommandFactory utility

  >>> import re
  >>> from zope import interface
  >>> from zope.component import provideUtility

  >>> from z3c.zrtresource import interfaces

  >>> class MyCustomCommand(object):
  ...   interface.implements(interfaces.IZRTCommand)
  ...
  ...   data = {'color1': 'red', 'color2': 'green'}
  ...
  ...   isAvailable = True
  ...
  ...   def __init__(self, args, start, end):
  ...      self.args = args
  ...      self.start = start
  ...      self.end = end
  ...
  ...   def process(self, text, context, request):
  ...      for key, value in self.data.items():
  ...         regex = re.compile(re.escape(key))
  ...         text = regex.subn(value, text)[0]
  ...
  ...      return text

  >>> from zope.component.factory import Factory
  >>> my_command = Factory(MyCustomCommand, 'mycommand')
  >>> interface.directlyProvides(my_command, interfaces.IZRTCommandFactory)

  >>> provideUtility(my_command, interfaces.IZRTCommandFactory, name='mycommand')

  >>> open(fn, 'w').write('''\
  ... /* zrt-replace: "../img1" "++resource++/img" */
  ... /* zrt-replace: "fontFamily" "Arial, Tahoma" */
  ... /* zrt-mycommand: */
  ... /* oh, and we're testing that when the file changes, it is reloaded */
  ... h1 {
  ...   color: color1;
  ...   font: fontFamily;
  ...   background: url('../img1/mybackground.gif');
  ... }
  ...
  ... h2 {
  ...   color: color2;
  ...   background: url('../img2/mybackground.gif');
  ... }
  ... /* zrt-replace: "../img2" "++resource++/img" */
  ... ''')

We have to recreate the ZRTFileResourceFactory to reload the changed file
contents (don't worry -- in real life Zope creates these anew for every
request, since resources are actually registered as IResourceFactoryFactory
utilities).

  >>> cssFactory = ZRTFileResourceFactory(fn, None, 'site.css')
  >>> css = cssFactory(TestRequest())

  >>> print css.GET()
  /* oh, and we're testing that when the file changes, it is reloaded */
  h1 {
    color: red;
    font: Arial, Tahoma;
    background: url('++resource++/img/mybackground.gif');
  }
  <BLANKLINE>
  h2 {
    color: green;
    background: url('../img2/mybackground.gif');
  }
  <BLANKLINE>
