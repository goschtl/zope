from setuptools import setup

name = 'zc.recipe.deployment'
setup(
    name=name,
    entry_points='[zc.buildout]\ndefault=%s:Recipe' % name,
    package_dir = {'': 'src'},
    )

