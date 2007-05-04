from setuptools import setup, find_packages

entry_points = """
"""

setup(
    name = 'zc.zodbactivitylog',
    version = '0.1',
    author = 'Jim Fulton',
    author_email = 'jim@zope.com',
    description = 'ZODB Activity Monitor that just logs',
    license = 'ZPL 2.1',
    
    packages = find_packages('src'),
    namespace_packages = ['zc'],
    package_dir = {'': 'src'},
    install_requires = 'setuptools',
    zip_safe = False,
    entry_points=entry_points,
    )
