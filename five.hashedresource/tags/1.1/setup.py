import os
from setuptools import setup, find_packages


setup(
    name='five.hashedresource',
    version = '1.1',
    author='gocept gmbh & co. kg',
    author_email='sw@gocept.com',
    description='Provides URLs for resources that change whenever their content changes.',
    url='http://pypi.python.org/pypi/five.hashedresource',
    long_description= (
        open(os.path.join('src', 'five', 'hashedresource', 'README.txt')).read()
        + '\n\n'
        + open('CHANGES.txt').read()),
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Framework :: Zope2'],
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['five'],
    install_requires=[
        'setuptools',
        'z3c.hashedresource>1.0',
        'zope.component',
        'zope.publisher',
        'zope.traversing',
        ],
    include_package_data = True,
    zip_safe = False,
)
