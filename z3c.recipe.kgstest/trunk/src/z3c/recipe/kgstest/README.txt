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
... include = z3c.recipe.kgstest
... """)
>>> system(buildout).find('Installing kgstest') != -1
True
>>> ls('bin')
- buildout
- kgstest-z3c.recipe.kgstest
>>> cat('bin', 'kgstest-z3c.recipe.kgstest')
#!/...python...
...zope.dottedname...
