import os
from setuptools import setup, find_packages


setup(
    name='five.hashedresource',
    version = '0.1dev',
    author='Sebastian Wehrmann',
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
        'z3c.noop',
        'zope.app.publisher',
        'zope.component',
        'zope.interface',
        'zope.publisher',
        ],
    extras_require=dict(test=[
        'zope.app.testing',
        'zope.app.zcmlfiles',
        'zope.security',
        'zope.site',
        'zope.testbrowser',
        ]),
    include_package_data = True,
    zip_safe = False,
)
