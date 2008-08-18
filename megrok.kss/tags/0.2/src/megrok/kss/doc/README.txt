
How to add KSS support to your grok app
=======================================
 
- current megrok.kss depends on kss.core trunk::

    http://codespeak.net/svn/kukit/kss.core/trunk

- install it as a develop egg in your buildout

- add megrok.kss egg to your setup.py

- add following code to your app configure.zcml

:: 

  <include package="megrok.kss" />

  AFTER

:: 

  <include package="grok" />

  and BEFORE

:: 

  <grok:grok package="." />

- include the reference to kss js files in your application templates

:: 

   <tal:kss_javascript replace="structure context/@@kss_javascript" />

- include a kinetic stylesheet with code like

:: 

   <link tal:attributes="href static/app.kss" rel="kinetic-stylesheet" type="text/kss" />


- create a KSSAction view with code like::
   
        from megrok.kss import KSSAction
        
        class AppKSS(KSSAction):

            def welcome(self):
                core = self.getCommandSet('core')
                core.replaceHTML('#click-me', '<p>ME GROK KISSED !</p>')

- you can use @@kss_devel_mode/ui url to access the UI that sets up the devel
  mode.
