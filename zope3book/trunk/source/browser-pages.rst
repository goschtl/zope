Browser Pages
=============

.. index:: browser page
.. index:: browser view
.. index:: view component; component

Introduction
------------

In the last chapter we have seen how to use HTML as a resources file.
The resource HTML will be only available on site-level with the `@@`
prefix.

Browser page (or more generically views) are representations for
particular objects/components.

If you have a template like this (helloworld.pt)::

  Hello, World !

.. index:: registration; browser page

Here is how to register a page for `IFolder` interface::

  <browser:page
    name="helloworld.html"
    for="zope.app.folder.interfaces.IFolder"
    template="helloworld.pt"
    permission="zope.Public"
    /> 


View components
---------------

While templates display data view components are preparing data.
View components convert data to output formats also prepare related
data (meta-data).  Then, create TAL-friendly object structures (dicts
and lists).  View components know about: component for which the
representation is created (context) and request object holding all
`output media` information (request)


Implementation
~~~~~~~~~~~~~~

Normally view components are added inside `browser` package inside
your main package.  The organization of the browser code is really up
to you and the examples are just the most basic rules of thumb.

Here is a simple view defined::

  from zope.publisher.browser import BrowserPage
  from zope.app.folder import interfaces

  class HelloWorld(BrowserPage):

      def subFolderIds(self):
          for name, subobj in self.context.items():
              if interfaces.IFolder.providedBy(subobj):
                  yield name 

Since methods and attributes of the view component are directly used
by the template, they should return simple iterable objects
(e.g. lists, tuples, generators) or mappings (e.g. dicts).


View components - integration
-----------------------------

First you need to register the view component for a particular
integration.  You can use the `class` attribute of `browser:page`
directive for registration.  The above example registration can be
changed like this::

  <browser:page
    name="helloworld.html"
    for="zope.app.folder.interfaces.IFolder"
    template="helloworld.pt"
    class=".browser.HelloWorld"
    permission="zope.Public"
    /> 

Now you can use the view in the template (helloworld.pt).  For
example, if you want to list all folders add like this to template::

    <ul>
      <li tal:repeat="id view/subFolderIds"
          tal:content="id" />
    </ul>

All methods and attributes defined in the view component are
available via the view top-level namespace.  In fact, the view
namespace is the instance of the view component.  Now restart Zope 3
for new configuration to take effect.  You can see the subfolders
listing at http://localhost:8080/@@helloworld.html (Replace the
`8080` port with the actual one)


Template attribute language
---------------------------

.. index:: TAL ; page template

.. index::
   single: template attribute language ; page template

* Attribute-based templating language
* Allows designer to modify templates without having to worry about TAL
* Works only well for XML
* See TAL Specification 1.4


tal:content
~~~~~~~~~~~

Insert content into the element and remove all of the element's
children.

Examples::

  <p tal:content="request/principal/title">Gandalf</p>


tal:replace
~~~~~~~~~~~

Replace the current element and all its content by the evaluated
expression.

Examples::

  <span tal:replace="view/title">Title</span>
  <span tal:replace="text view/title">Title</span>
  <span tal:replace="structure view/subTemplate" />
  <span tal:replace="nothing">This element is a comment.</span>


tal:attributes
~~~~~~~~~~~~~~

* Replaces the value of an XML attribute

* Can replace multiple attributes separated by ;

  Examples::

      <a href="/sample/link.html"
         tal:attributes="href here/sub/absolute_url">
      <textarea rows="80" cols="20"
                tal:attributes="rows request/rows; cols request/cols" />


tal:repeat (1)
~~~~~~~~~~~~~~

* Replicate a subtree once for each item in a sequence

* The current item is stored in a given variable

  Examples::

    <ul>
      <li tal:repeat="name context/keys">
        <span tal:replace="repeat/name/number" />.
        <span tal:replace="name" />
      </li>
    </ul>


tal:repeat (2)
~~~~~~~~~~~~~~

Global repeat namespace provides many organizational features

- index - repetition number, starting from zero.
- number - repetition number, starting from one.
- even - true for even-indexed repetitions (0, 2, 4, ...).
- odd - true for odd-indexed repetitions (1, 3, 5, ...).
- start - true for the starting repetition (index 0).
- end - true for the ending, or final, repetition.
- length - length of the sequence, which will be the total number
  of repetitions.
- letter - count reps with lower-case letters: "a" - "z", "aa" -
  "az", "ba" - "bz", ..., "za" - "zz", "aaa" - "aaz", and so forth.
- Letter - upper-case version of letter.


tal:condition
~~~~~~~~~~~~~

Include a section of the XML document, only under a certain condition

Examples::

  <p tal:condition="view/showCopyright"
     tal:content="view/copyright">(c) Stephan Richter 2006</p>


tal:define
~~~~~~~~~~

Allows you to declare new local and global variables

Examples::

  tal:define="title view/title; extra_title string:$title - Extra"
  tal:define="global company_name string:Web2k"


tal:on-error
~~~~~~~~~~~~

* After an error occurred in any TAL statement, it is caught and the
  error expression is evaluated and inserted.

* The engine looks up the entire element path to find an on-error
  statement

  Examples::

      <p tal:on-error="string: Error! This paragraph is buggy!">
        My name is <span tal:replace="view/unknown" />.
      </p>


tal:omit-tag
~~~~~~~~~~~~

* Omit a tag, if the provided expression evaluates to true

* Sub-elements are not omitted

  Examples::

    <div tal:omit-tag="" comment="This tag will be removed">
    <i>...but this text will remain.</i>
    </div>
    <b tal:omit-tag="not:bold">I may not be bold.</b>


Common TAL top-level namespaces
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are a few common top-level namespaces available in a Zope Page
Template (ZPT)

*view*
  The view component attached to the template. If none was provided
  during registration, the namespace is effectively empty.

*context*
  The component the view is for. This is the same context as the
  context of the view component.

*request*
  The request object representing the access medium. It contains
  server data, input data and principal information.


TALES namespaces
~~~~~~~~~~~~~~~~

.. index:: TALES ; page template

TALES namespaces effectively specify the expression type. The default
is the path TALES namespace. See TALES Specification 1.3

*path*
  interpret the expression string as the path to some object.

*string*
  interpret the expression string as text.

*python*
  interpret the expression string as restricted Python code.

*not*
  evaluate the expression string (recursively) as a full expression,
  and returns the boolean negation of its value.


Summary
-------

This chapter introduced browser pages or views.  Also covered the
basic of TAL.
