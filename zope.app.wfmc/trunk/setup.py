from setuptools import setup, find_packages

setup(
    name = '',
    version = '0.1',
    author = 'Jim Fulton',
    author_email = 'jim@zope.com',
    description = '',
    license = 'ZPL 2.1',
    
    packages = find_packages('src'),
    namespace_packages = ['zope', 'zope.app'],
    package_dir = {'': 'src'},
    install_requires = ['setuptools'],
    zip_safe = False,
    )
