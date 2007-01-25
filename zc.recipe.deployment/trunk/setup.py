from setuptools import setup, find_packages

name = 'zc.recipe.deployment'
setup(
    name = name,
    version = '0.1dev',
    author = 'Jim Fulton',
    author_email = 'jim@zope.com',
    description = 'ZC Buildout recipe for deployment configuration',
    license = 'ZPL 2.1',
    keywords = 'zope3',
    url = 'http://svn.zope.org/' + name,
    
    install_requires = ['setuptools'],
    entry_points = '[zc.buildout]\ndefault=%s:Recipe' % name,
    package_dir = {'': 'src'},
    packages = find_packages('src'),
    namespace_packages = ['zc', 'zc.recipe']
    )

