from setuptools import setup

name = 'zc.recipe.rhrc'
setup(
    name=name,
    entry_points='[zc.buildout]\ndefault=%s:Recipe' % name,
    package_dir = {'': 'src'},
    install_requires = "zc.buildout" # XXX Grrr should use tests_require
    )
