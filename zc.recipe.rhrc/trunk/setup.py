from setuptools import setup


entry_points = '''
[zc.buildout]
default=zc.recipe.rhrc:Recipe

[zc.buildout.uninstall]
default=zc.recipe.rhrc:uninstall
'''

name = 'zc.recipe.rhrc'
setup(
    name=name,
    entry_points=entry_points,
    package_dir = {'': 'src'},
    install_requires = "zc.buildout" # XXX Grrr should use tests_require
    )
