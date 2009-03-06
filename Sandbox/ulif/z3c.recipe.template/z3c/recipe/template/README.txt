Detailed Description
********************

Lets create a minimal `buildout.cfg` file::

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = template
  ... offline = true
  ...
  ... [template]
  ... recipe = z3c.recipe.template
  ... input = template.in
  ... output = template
  ... ''')

We create a template file::

  >>> write('template.in',
  ... '''#
  ... My template knows about buildout path:
  ...   ${buildout:directory}
  ... ''')

Now we can run buildout::

  >>> print system(join('bin', 'buildout')),
  Installing template.

The template was indeed created::

  >>> cat('template')
  #
  My template knows about buildout path:
  .../sample-buildout

