from setuptools import setup, find_packages

name = 'zc.z3monitor'
setup(
    name = name,
    version = '0.1',
    author = 'Jim Fulton',
    author_email = 'jim@zope.com',
    description = 'Zope 3 Monitor',
    license = 'ZPL 2.1',
    keywords = 'zope3',
    
    packages = find_packages('src'),
    namespace_packages = ['zc'],
    package_dir = {'': 'src'},
    install_requires = ['setuptools', 'zc.ngi'],
    zip_safe = False,
    )
