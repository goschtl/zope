import os
from setuptools import setup, find_packages


setup(
    name='z3c.noop',
    version = '1.0',
    author='Wolfgang Schnerring',
    author_email='ws@gocept.com',
    description='z3c.noop provides traverser that simply skips a path element, so /foo/++noop++qux/bar is equivalent to /foo/bar.',
    url='http://pypi.python.org/pypi/z3c.noop',
    long_description= (
        open(os.path.join('src', 'z3c', 'noop', 'README.txt')).read()
        + '\n\n'
        + open('CHANGES.txt').read()),
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Framework :: Zope3'],
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['z3c'],
    install_requires=[
        'setuptools',
        'zope.component',
        'zope.interface',
        'zope.publisher',
        'zope.traversing',
        ],
    extras_require=dict(test=[
        'zope.app.testing',
        'zope.app.zcmlfiles',
        'zope.testing',
        ]),
    include_package_data = True,
    zip_safe = False,
)
