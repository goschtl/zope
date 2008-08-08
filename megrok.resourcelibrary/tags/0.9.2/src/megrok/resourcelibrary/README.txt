megrok.resourcelibrary: Resources in Grok
=========================================

Introduction
------------

Grok already comes equipped with a simple way to expose static file
resources, the ``static`` directory.

``megrok.resourcelibrary`` allows the more flexible inclusion of
static file resources in Grok. It uses the ``zc.resourcelibrary``
package to do this.

A resource library is essentially like a directory like the ``static``
directory of a package, full of static resources, such as CSS files,
javascript files and images. Resources are intended to be used from
HTML pages, as additional resources to help display a particular
layout or user interface.

How is ``megrok.resourcelibrary`` more flexible than Grok's default
``static`` directory?

* A resource library can be in a layer.

* A resource library can have a non-public permission.

* A resource library can more easily be packaged for reuse by other
  libraries. Resource libraries have unique names under the control of
  the developer.

* A resource library can automatically include some resources (such as
  javascript or css) in the ``head`` section of a web page whenever a
  particular widget needs it.

* A resource library can also depend on other libraries.

Basic example
-------------

Let's see how this all works. First we need to grok this package
itself (this is normally done from ZCML)::

  >>> from grok.testing import grok
  >>> grok('megrok.resourcelibrary.meta')

Now we can set up a simple resource library::
  
  >>> import grok
  >>> import megrok.resourcelibrary
  >>> class SomeLibrary(megrok.resourcelibrary.ResourceLibrary):
  ...     megrok.resourcelibrary.directory('tests/example')

We need to grok this to make it available (in normal use this is done
automatically for you)::

  >>> from grok.testing import grok_component
  >>> grok_component('SomeLibrary', SomeLibrary)
  True

The resources in this directory are now published, by default under
the class name of the library, lower cased (therefore
``somelibrary``)::

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.open('http://localhost/@@/somelibrary/my-lib/included.js')
  >>> print browser.contents
      function be_annoying() {
      alert('Hi there!');
  }

The default name can be overridden by using the ``grok.name``
directive::

  >>> class SomeLibrary2(megrok.resourcelibrary.ResourceLibrary):
  ...     grok.name('some-library')
  ...     megrok.resourcelibrary.directory('tests/example')
  >>> grok_component('SomeLibrary2', SomeLibrary2)
  True
  >>> browser.open('http://localhost/@@/some-library/my-lib/included.js')
  >>> print browser.contents
      function be_annoying() {
      alert('Hi there!');
  }

It's an error to point to a directory that doesn't exist::

  >>> class WrongDirectory(megrok.resourcelibrary.ResourceLibrary):
  ...     grok.name('wrong-directory')
  ...     megrok.resourcelibrary.directory('tests/doesnt_exist')
  >>> grok_component('WrongDirectory', WrongDirectory)
  Traceback (most recent call last):
    ...
  GrokError: Directory 'tests/doesnt_exist' is not a valid directory passed to the 'wrong-directory' directive.

Automactic inclusion of resources
---------------------------------

We now set up a resource library that automatically includes two
resources whenever it is used in a web page, namely ``included.js``
and ``included.css``::

  >>> class MyLib(megrok.resourcelibrary.ResourceLibrary):
  ...    grok.name('my-lib')
  ...    megrok.resourcelibrary.directory('tests/example/my-lib')
  ...    megrok.resourcelibrary.include('included.js')
  ...    megrok.resourcelibrary.include('included.css')
  >>> grok_component('MyLib', MyLib)
  True

This is how you require the library to be loaded in a particular page
template::

  <tal:block replace="resource_library:my-lib"/>

``test_template_2`` makes this requirement, so the included Javascript
should be included::

  >>> browser.open('http://localhost/zc.resourcelibrary.test_template_2')
  >>> '/@@/my-lib/included.js' in browser.contents
  True

And the resource is also published::

  >>> browser.open('/@@/my-lib/included.js')
  >>> print browser.contents
      function be_annoying() {
      alert('Hi there!');
  }

A reference to the CSS is also inserted into the HTML::

  >>> browser.open('http://localhost/zc.resourcelibrary.test_template_2')
  >>> '/@@/my-lib/included.css' in browser.contents
  True
 
And the CSS is available from the URL referenced::

    >>> browser.open('/@@/my-lib/included.css')
    >>> print browser.contents
    div .border {
        border: 1px silid black;
    }

Programmatically signalling resource requirements
-------------------------------------------------

Above we've demonstrated the use of the ``resource_library`` namespace
in ZPT. Library usage can also be signalled programmatically, for
instance in a view::

  >>> import grok
  >>> from zope.interface import Interface
  >>> class View(grok.View):
  ...   grok.context(Interface)
  ...   def render(self):
  ...      MyLib.need()
  ...      return '<html><head></head><body>Example</body></html>'
  >>> grok_component('View', View)
  True

  >>> browser.open('http://localhost/view')
  >>> '/@@/my-lib/included.js' in browser.contents
  True

This also works for libraries which don't have an explicit ``grok.name``::

  >>> class MyLib2(megrok.resourcelibrary.ResourceLibrary):
  ...    megrok.resourcelibrary.directory('tests/example/my-lib')
  ...    megrok.resourcelibrary.include('included.js')
  ...    megrok.resourcelibrary.include('included.css')
  >>> grok_component('MyLib2', MyLib2)
  True

  >>> class View2(grok.View):
  ...   grok.context(Interface)
  ...   def render(self):
  ...      MyLib2.need()
  ...      return '<html><head></head><body>Example</body></html>'
  >>> grok_component('View2', View2)
  True

  >>> browser.open('http://localhost/view2')
  >>> '/@@/mylib2/included.js' in browser.contents
  True

You can also signal inclusion by library name instead (like is done in page templates)::

  >>> class View3(grok.View):
  ...   grok.context(Interface)
  ...   def render(self):
  ...      megrok.resourcelibrary.need('my-lib')
  ...      return '<html><head></head><body>Example</body></html>'

  >>> grok_component('View3', View3)
  True

  >>> browser.open('http://localhost/view3')
  >>> '/@@/my-lib/included.js' in browser.contents
  True

Making resource libraries depend on other ones
----------------------------------------------

We can make a resource library depend on another one::

  >>> class Dependency(megrok.resourcelibrary.ResourceLibrary):
  ...    megrok.resourcelibrary.directory('tests/example')
  ...    megrok.resourcelibrary.include('1.js')
  >>> grok_component('Dependency', Dependency)
  True
   
  >>> class Dependent(megrok.resourcelibrary.ResourceLibrary):
  ...    megrok.resourcelibrary.directory('tests/example')
  ...    megrok.resourcelibrary.include('2.css')
  ...    megrok.resourcelibrary.depend(Dependency)
  >>> grok_component('Dependent', Dependent)
  True

Let's make a view that needs ``Dependent``::

  >>> class DependentView(grok.View):
  ...   grok.context(Interface)
  ...   def render(self):
  ...      Dependent.need()
  ...      return '<html><head></head><body>Example</body></html>'
  >>> grok_component('DependentView', DependentView)
  True

The included code of both the original and the dependency will now
show up::

  >>> browser.open('http://localhost/dependentview')
  >>> '/@@/dependency/1.js' in browser.contents
  True
  >>> '/@@/dependent/2.css' in browser.contents
  True

Protecting resources
--------------------

It's possible to give a resource a permission::

  >>> class MyPermission(grok.Permission):
  ...    grok.name("my.permission")
  >>> grok_component('MyPermission', MyPermission)
  True

  >>> class MyLib3(megrok.resourcelibrary.ResourceLibrary):
  ...    megrok.resourcelibrary.directory('tests/example/my-lib')
  ...    grok.require(MyPermission)
  >>> grok_component('MyLib3', MyLib3)
  True

XXX This doesn't work yet, as resources don't do their own security
checks but rely on proxies, which Grok has removed... Need to introduce
new resources/factories to do checks by hand.
