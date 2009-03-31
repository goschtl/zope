megrok.cheetah
==============

megrok.cheetah makes it possible to use Cheetah templates in Grok.

For more information about Grok and Cheetah visit:

- http://grok.zope.org/
- http://www.cheetahtemplate.org/

Requirements
------------

- Grok v1.0a or later. Tested with Grok v1.0a.
- Cheetah v2.0.1 or later. Tested with Cheetah v2.0.1

Installation
------------

To use the Cheetah templates within Grok, megrok.cheetah must be first
installed as an egg, and its ZCML included. After using grokproject,
amend the setup.py to look like this:

    install_requires=[''setuptools',
                      'grok',
                      'megrok.cheetah',
                      # Add extra requirements here
                      ],

Then include megrok.cheetah in your configure.zcml. It should look 
something like this:

    <configure xmlns="http://namespaces.zope.org/zope"
               xmlns:grok="http://namespaces.zope.org/grok">
      <include package="grok" />
      <include package="megrok.cheetah"/>
      <grok:grok package="." />
    </configure>

Rerun buildout (bin/buildout), giving you something like:

    Getting distribution for 'megrok.cheetah'.
    Got megrok.cheetah 0.1

That's it. You can now place Cheetah templates (with the .tmpl extension)
into any template directory used within your project. 

Usage
-----

megrok.cheetah allows you to use the standard pattern of placing
templates into a specially named directory (e.g. app_templates).
megrok.cheetah uses the special file extension of '.tmpl' to distinguish
Cheetah templates from others. 

You can use Cheetah templates inline:

    from megrok.cheetah.components import CheetahTemplate
    index = CheetahTemplate('<html>ME BASH CHEETAH</html>')

Or from a file:

    from megrok.cheetah.components import CheetahTemplate
    index = CheetahTemplate(filename='thefilename.html')

In addition, megrok.cheetah has support for compiled Cheetah templates. 
To use this, you must compile your Cheetah template to suppress its
default of automatically calling callables in the namespace that it 
is passed. You accomplish this using the ``compiler-settings`` 
directive:
    
    #compiler-settings
        useAutocalling = False
    #end compiler-settings

within your template to be compiled. If you do not include this,
you will experience problems. 

Authors
-------

- Paul A. Wilson

Thanks
------

- Lennart Regebro & Guido Wesdorp (for megrok.genshi)
