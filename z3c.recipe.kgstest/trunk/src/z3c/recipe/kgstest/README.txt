==================
z3c.recipe.kgstest
==================

>>> cd(sample_buildout)
>>> write('buildout.cfg', """
... [buildout]
... parts = kgstest
...
... [kgstest]
... recipe = z3c.recipe.kgstest
... exclude = .*
... include = zope.dottedname
... """)
>>> print system(buildout)
Installing kgstest.
>>> ls('bin')
- buildout
- kgstest-zope.dottedname
