MEGROK.QUARRY
=============

author :: Kevin M. Smith

Grok is an rapid application development framework built on top of the enterprise 
class Zope3's component architecture. http://grok.zope.org

As of 0.9dev, Grok has no way of associating different views with different skins.
MEGROK.QUARRY is an implementation of skins, layers and template re-use. It is
useable today and based on discussions from the mailing list. It is hoped these 
new directives and grokkers will be considered for inclusion in the core one day.

Change Log
----------

* 0.1 initial checkin

Current Enhancements
--------------------

* quarry.template directive enhancement

* quarry.View (a skin-aware version of grok.View)

* quarry.layer directive

* quarry.Layer grokker

* quarry.Skin grokker

* quarry.ViewletManager, quarry.Viewlet (based Lennart Regebro's megrok.viewlet)

* quarry.viewletmanager directive


Template Sharing and Reuse
--------------------------

Currently only inline pagetemplates are accessible via grok.template.

	  >>> class Painting(grok.View):
	  ...     grok.template('cavepainting')

	  >>> cavepainting = grok.PageTemplate("""
	  ... <html><body><h1>GROK PAINT MAMMOTH!</h1></body</html>
	  ... """)

This works fine, but you can only access templates located in the same 
module, which limits template re-use.

Using quarry.template, any template from any module may be accessed. Note,
grok.View needs to be replaced with quarry.View, since grok.View has no notion
of quarry.template.

	   >>> class Painting(quarry.View):
	   ...    quarry.template('myproject.shared.cavepainting')

myproject/shared.py

	  >>> cavepainting = grok.PageTemplate("""
	  ... <html><body><h1>GROK PAINT MAMMOTH!</h1></body</html>
	  ... """)

Also works with grok.PageTemplateFile

	  >>> cavepainting = grok.PageTemplateFile(os.path.join('shared', 
	  ...                             'cavepainting.pt'))

And plain strings
   
	  >>> cavepainting = """
	  ... <html><body><h1>GROK PAINT MAMMOTH!</h1></body</html>
	  ... """

Even docstrings

	 >>> class Painting(quarry.View):
	 ...     """<html><body><h1>GROK PAINT MAMMOTH!</h1></body</html>
	 ...     """
	 ...     quarry.template('myproject.app.Painting.__doc__')


Skins, layers and grok, oh my!
------------------------------

As mentioned, Grok 0.9dev has no notion of skins or layers. The quarry.View
grokker recognizes the quarry.layer directive. This directive is both a 
module level and class level driective.
	
First let us define an admin skin, and a public skin.

	>>> class AdminLayer(quarry.Layer, IDebugLayer):
	...     pass

	>>> class Admin(quarry.Skin):
	...     grok.name('admin') # default, accessible as ++skin++admin
	...     grok.layer(AdminLayer)

	>>> class PublicLayer(quarry.Layer):
	...     pass

	>>> class Public(quarry.Skin):
	...    grok.name('public') # default name, accessible as ++skin++public
	...    grok.layer(PublicLayer) # must pass interface     

In our app, we associate layers to views as follows

       >>> from skin import AdminLayer

       >>> class AdminPanel(quarry.View):
       ...     grok.layer(AdminLayer)

Or we can associate layers at a module level

      >>> grok.layer(PublicLayer)

      >>> class MyPublicView(quarry.View):
      ...     # defaults to PublicLayer

      
Viewlets
--------

Since I'd been hoping Grok would be template neutral to better compete with
the other frameworks, I've been very resistant to Zope Page Templates. I've
even come up with multiple scenarios to avoid using macros.  But this is all
nice and good but once you get hooked on ZPT's power, it's hard to deal with
other templating options.

Both quarry.ViewletManager and quarry.Viewlet are base on Lennart Regebro's
megrok.viewlet. 

In this version both quarry.Viewlet and quarry.ViewletManager have been 
fashioned to be more grok.View-like. This means you can use quarry.template,
view.url(), static, and any  other methods you might find on a regular view.

Also the quarry.viewletmanager directive has been added to associate viewlet
with viewletmanager.

     >>> from megrok import quarry

     >>> class MyView(quarry.View):
     ...    """<html metal:use-macro="context/@@public/page">
     ...       <body>
     ...       <metal:block fill-slot="pagecontent">
     ...       <span tal:replace="structure provider:body" />
     ...       </metal:block>
     ...       </body></html>
     ...    """
     ...    quarry.template('myproject.app.MyView.__doc__')

     >>> class MenuManager(quarry.ViewletManager):
     ...    grok.context(MyView) # associate viewletmanager with a view
     ...    grok.name('body') #fill tal-namespace 'provide:body'
     
     >>> class Menu10(quarry.Viewlet):
     ...    quarry.viewletmanager(MenuManager)
     ...    def render(self):
     ...        return "Fish Tacos"

     >>> class Menu20(quarry.Viewlet):
     ...    quarry.viewletmanager(MenuManager)	
     ...    def render(self)l
     ...        return "Buffalo Wings"

     >>> class Menu30(quarry.Viewlet):
     ...    """<i>Side of Blue Cheese </i>"""
     ...    quarry.viewletmanager(MenuManager)
     ...    quary.template('myproject.app.Menu30.__doc__')

The quarry.ViewletManager automatically sorts by viewlet class name. So
Menu10 appears first and Menu30 appears last.


install
-------

* checkout via subversion
* add megrok.quarry-meta to zcml of buildout instance


Todo
----

* better documentation
* quarry.TALNamespace
* tests, tests, tests, currently they are intertwined in a seperate project
* currently grok.Layer inherits from IDefaultBrowserLayer, don't do this


Thank You
---------

The entire Grok team and Zope3 communities for making web programming
fun again.





