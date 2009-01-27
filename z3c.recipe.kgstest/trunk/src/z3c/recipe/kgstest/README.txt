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
... """)
>>> print system(buildout)
Installing kgstest.

>>> ls('parts')
