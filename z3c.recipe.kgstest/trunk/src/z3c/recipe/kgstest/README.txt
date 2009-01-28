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
... include = z3c.recipe.kgstest
... """)
>>> system(buildout).find('Installing kgstest') != -1
True
>>> ls('bin')
- buildout
- kgstest-z3c.recipe.kgstest
- test-kgs
>>> cat('bin', 'kgstest-z3c.recipe.kgstest')
#!/...python...
...zope.dottedname...

>>> cat('bin', 'test-kgs')
#!/...python...
...main(...kgstest-z3c.recipe.kgstest...
