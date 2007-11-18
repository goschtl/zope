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

To use Genshi under Grok all you need is to install megrok.genshi as an egg 
and include it's zcml. The best place to do this is to make megrok.genshi
a dependency of your application by adding it to your install_requires
list in setup.cfg. If you used grokprojet to create your application setup.cfg
is located in the project root. It should look something like this::

   install_requires=['setuptools',
                     'grok',
                     'megrok.genshi',
                     # Add extra requirements here
                     ],

Then include megrok.genshi in your configure.zcml. If you used grokproject to
create your application it's at src/<projectname>/configure.zcml. Add the
include line after the include line for grok, but before the grokking of the
current package. It should look something like this::

      <include package="grok" />
      <include package="megrok.genshi" />  
      <grok:grok package="." />
  
Then run bin/buildout again. You should now see buildout saying something like::

   Getting distribution for 'megrok.genshi'.
   Got megrok.genshi 0.9.

That's all. You can now start using Genshi in your Grok application!


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

You can also use Genshi templates inline.  The syntax for this is::

   from megrok.genshi.components import GenshiMarkupTemplate, GenshiTextTemplate
   index = GenshiMarkupTemplate('<html>the html code</html>')
   index = GenshiMarkupTemplate('Text templates')

Or if you use files::

   from megrok.genshi.components import GenshiMarkupTemplate, GenshiTextTemplate
   index = GenshiMarkupTemplate(filename='thefilename.html')
   index = GenshiMarkupTemplate(filename='thefilename.txt')


Authors
-------

- Lennart Regebro (regebro@gmail.com)
- Guido Wesdorp
