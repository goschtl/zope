from setuptools import setup


entry_points = '''
[zc.buildout]
default=zc.recipe.rhrc:Recipe

[zc.buildout.uninstall]
default=zc.recipe.rhrc:uninstall
'''

name = 'zc.recipe.rhrc'
setup(
    name = name,
    version = '0.1dev',
    author = 'Jim Fulton',
    author_email = 'jim@zope.com',
    description = 'ZC Buildout recipe for Redhat RC scripts',
    license = 'ZPL 2.1',
    keywords = 'zope3',
    
    entry_points=entry_points,
    package_dir = {'': 'src'},
    install_requires = "zc.buildout" # XXX Grrr should use tests_require
    )
