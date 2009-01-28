=====================
z3c.recipe.compattest
=====================

>>> cd(sample_buildout)
>>> write('buildout.cfg', """
... [buildout]
... parts = compattest
...
... [compattest]
... recipe = z3c.recipe.compattest
... include = z3c.recipe.compattest
... """)
>>> system(buildout).find('Installing compattest') != -1
True
>>> ls('bin')
- buildout
- compattest-z3c.recipe.compattest
- test-kgs
>>> cat('bin', 'compattest-z3c.recipe.compattest')
#!/...python...
...zope.dottedname...

>>> cat('bin', 'test-compat')
#!/...python...
...main(...compattest-z3c.recipe.compattest...
