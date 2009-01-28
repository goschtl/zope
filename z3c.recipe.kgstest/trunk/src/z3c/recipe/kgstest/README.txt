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
>>> system(buildout).find('Installing kgstest') != -1
True
>>> ls('bin')
- buildout
- kgstest-zope.dottedname
>>> cat('bin', 'kgstest-zope.dottedname')
#!/...python...
