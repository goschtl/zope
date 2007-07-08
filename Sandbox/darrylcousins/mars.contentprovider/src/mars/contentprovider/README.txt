====================
Mars ContentProvider
====================

Martian is a library that allows the embedding of configuration
information in Python code. Martian can then grok the system and
do the appropriate configuration registrations.

This package uses martian to configure contentproviders.

Example Code
------------

::
 import mars.view
 import mars.template
 import mars.contentprovider

 class Index(mars.view.LayoutView):
     pass

 class IndexLayout(mars.template.LayoutFactory):
     grok.template('index.pt')
     grok.context(Index)

 class Title(mars.contentprovider.ContentProvider):

     def render(self):
         return self.context.title

Template for index may be::

 <tal:block tal:content="structure provider:title" />

Directives
----------

Please see ``directive.txt``.

Tests
-----

See test directory.


