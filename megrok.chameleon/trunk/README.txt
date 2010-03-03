megrok.chameleon
****************

`megrok.chameleon` makes it possible to use chameleon templates in Grok. 

Currently support for chameleon genshi templates and chameleon zope
page templates is provided.

For more information on Grok and Chameleon templates see:

- http://grok.zope.org/
- http://chameleon.repoze.org/
- http://pypi.python.org/pypi/Chameleon
- http://pypi.python.org/pypi/chameleon.genshi

.. contents::

Requirements
============

- Chameleon templates (`Chameleon`).
- Chameleon genshi templates (`chameleon.genshi`).
- Grok v1.0a1 or later, or five.grok 1.0 or later.

Installation
============

To use Chameleon page templates with Grok all you need is to install
megrok.chameleon as an egg and include its ZCML. The best place to do
this is to make `megrok.chameleon` a dependency of your application by
adding it to your ``install_requires`` list in ``setup.cfg``. If you
used grokproject to create your application ``setup.py`` is located in the
project root. It should look something like this::

   install_requires=['setuptools',
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

If you use ``autoInclude`` in your ``configure.zcml``, you should not
have to do this latter step.

Then run ``bin/buildout`` again. You should now see buildout saying
something like::

   Getting distribution for 'megrok.chameleon'.
   Got megrok.chameleon 0.5.

That's all. You can now start using Chameleon page templates in your
Grok application.


Usage
=====

``megrok.chameleon`` supports the Grok standard of placing templates
in a templates directory, for example ``app_templates``, so you can
use Chameleon page templates by simply placing the Chameleon genshi
templates or Chameleon Zope page templates in the templates directory,
just as you would with regular ZPT templates.  Although chameleon
templates themselves do not have a standard for the file extensions
for templates, Grok needs to have an association between an
extension and a type so it knows which type of template each template
is.  `megrok.chameleon` defines the following extensions:

* ``.cpt`` (``Chameleon page template``) for Chameleon page templates

* ``.cg`` (``Chameleon genshi template``) for chameleon driven genshi
  templates

* ``.cgt`` (``Chameleon genshi text template``) for chameleon driven
  genshi text templates

You can also use Chameleon page templates inline.  The syntax for this
is::

   from megrok.chameleon.components import ChameleonPageTemplate
   index = ChameleonPageTemplate('<html>the html code</html>') 

Or if you use files::

   from megrok.genshi.components import ChameleonPageTemplateFile
   index = ChameleonPageTemplateFile(filename='thefilename.html')

