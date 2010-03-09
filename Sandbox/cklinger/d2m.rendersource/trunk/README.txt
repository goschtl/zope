Grok source renderers
=====================

First take on making the zope.app.render classes available from Grok templates.

* RestructuredText: template files with '.rst' extension
  
  renders a complete HTML page, including embedded stylesheet (default)
  or with a configurable external stylesheet


Installation
------------

Add 'd2m.rendersource' to the 'install_requires' list in your packages 'setup.py'.
Run buildout again.
Template reloading is available in developer mode only:
  add 'devmode on' to the 'zope.conf = ' line in your buildout.cfg
 

Configuration
-------------

To configure the stylesheet used with your template, add a method 'namespace' 
to your view class:: 

	class Overview(grok.View):
	
	    def namespace(self):
	        # compute the stylesheet path to the file inside the 'static' folder, 
	        # eg. 'grok.css'
	        stylesheet=self.static['grok.css']()
	        # enable absolut URL handling, disable embedding 
	        return {'settings_overrides': {'stylesheet': stylesheet,
	                                       'stylesheet_path': None,
	                                       'embed_stylesheet': 0,
	                                       'input_encoding': 'utf-8',
	                                       'output_encoding': 'utf-8',
	                                       }}

Other docutils related options can be added to the 'settings_overrides' 
dictionary. CF grok_overview.txt for more info on the namespace method.