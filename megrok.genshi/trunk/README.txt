megrok.genshi
=============

megrok.genshi makes it possible to use Genshi templates in Grok. 

For more information on Grok and Genshi see:

- http://grok.zope.org/
- http://genshi.edgewall.org/

Requirements
------------

- Genshi.  Tested with v 0.4.4.
- Grok v0.11 or later.  Tested with 0.11.

Installation
------------

To use Genshi under Grok all you need is to add megrok.genshi as an egg in 
your buildout.cfg.  Assuming you used grokproject to create your buildout,
you should add it to the eggs list under the headings [app] and [test].

You also need to add <include package="megrok.genshi" /> to your site.zcml,
also under the [app] heading in your buildout.cfg.

Then run bin/buildout again, and it should now fetch and install the eggs
for both Genshi and megrok.genshi.

Usage
-----

megrok.genshi supports the Grok standard of placing templates in a templates
directory, for example app_templates, so you can use Genshi by simply placing
the Genshi templates in the templates directory, just as you would with ZPT
templates.  Although Genshi itself doesn't have a standard for the file
extensions for Genshi templates, Grok needs to have an association between an
extension and a type so it knows which type of template each template is.
megrok.genshi defines the extension .g for Genshi HTML templates and .gt for
Genshi Text templates.  Genshi can also include templates, and although you can
use any extension for this we recommend you use .gi for any include templates,
to avoid any clashes with other templating languages.

You can also use Genshi templates inline.  The syntax for this is:

   from megrok.genshi.components import GenshiMarkupTemplate, GenshiTextTemplate

   index = GenshiMarkupTemplate('<html>the html code</html>')
   index = GenshiMarkupTemplate('Text templates')

Or if you use files

   index = GenshiMarkupTemplate(filename='thefilename.html')
   index = GenshiMarkupTemplate(filename='thefilename.txt')


Authors
-------

- Lennart Regebro (regebro@gmail.com)
- Guido Wesdorp
