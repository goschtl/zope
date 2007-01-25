from setuptools import setup, find_packages


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
    packages = find_packages('src'),
    namespace_packages = ['zc', 'zc.recipe'],
    package_dir = {'': 'src'},
    extras_require = dict(test="zc.buildout"),
    install_requires = 'setuptools',
    zip_safe = False,
    )
