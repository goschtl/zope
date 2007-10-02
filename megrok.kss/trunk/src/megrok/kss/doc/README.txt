
(- add kss.core egg to your buildout)

- add following code to your app configure.zcml

:: 

  <include package="megrok.kss" />

  AFTER

:: 

  <include package="grok" />

- add following references to kss js files in your application templates

:: 

   <tal:kss_javascript replace="structure context/@@kss_javascript" />

- include a kinetic stylesheet with code like

:: 

   <link tal:attributes="href static/app.kss" rel="kinetic-stylesheet" type="text/kss" />


- you can use @@kss_devel_mode/ui url to access the UI that sets up the devel
  mode.
