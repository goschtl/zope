megrok.chameleon
================

`megrok.chameleon` makes it possible to use chameleon templates in Grok. 

For more information on Grok and Genshi see:

- http://grok.zope.org/
- http://pypi.python.org/pypi/chameleon.zpt

Requirements
------------

- Chameleon templates (`chameleon.zpt`)  Tested with v 1.0b9.
- Grok v1.0a1 or later.  Tested with 1.0a1.

Installation
------------

To use Chameleon page templates with Grok all you need is to install
megrok.chameleon as an egg and include it's zcml. The best place to do
this is to make `megrok.chameleon` a dependency of your application by
adding it to your ``install_requires`` list in ``setup.cfg``. If you
used grokprojet to create your application ``setup.py`` is located in the
project root. It should look something like this::

   install_requires=['setuptools',
                     'grok',
                     'megrok.chameleon',
                     # Add extra requirements here
                     ],

Then include ``megrok.chameleon`` in your ``configure.zcml``. If you
used grokproject to create your application it's at
``src/<projectname>/configure.zcml``. Add the include line after the
include line for grok, but before the grokking of the current
package. It should look something like this::

      <include package="grok" />
      <include package="megrok.chameleon" />  
      <grok:grok package="." />
  
Then run ``bin/buildout`` again. You should now see buildout saying
something like::

   Getting distribution for 'megrok.chameleon'.
   Got megrok.genshi 0.1.

That's all. You can now start using Chameleon page templates in your
Grok application!


Usage
-----

``megrok.chameleon`` supports the Grok standard of placing templates
in a templates directory, for example ``app_templates``, so you can
use Chameleon page templates by simply placing the Genshi templates in
the templates directory, just as you would with ZPT templates.
Although Genshi itself doesn't have a standard for the file extensions
for Genshi templates, Grok needs to have an association between an
extension and a type so it knows which type of template each template
is.  `megrok.chameleon` defines the extension .cpt (``Chameleon page
template``) for Chameleon page templates.

You can also use Chameleon page templates inline.  The syntax for this
is::

   from megrok.chameleon.components import ChameleonPageTemplate
   index = ChameleonPageTemplate('<html>the html code</html>') 

Or if you use files::

   from megrok.genshi.components import ChameleonPageTemplateFile
   index = ChameleonPageTemplateFile(filename='thefilename.html')

