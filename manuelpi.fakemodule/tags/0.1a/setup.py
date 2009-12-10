import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('src', 'manuelpi', 'fakemodule', 'README.txt')
    + '\n' +
    read('CHANGES.txt')
    )

name='manuelpi.fakemodule'

setup(
    name=name,
    version='0.1a',
    url='http://www.python.org/pypi/'+name,
    license='ZPL 2.1',
    description='Module support in doctests',
    long_description=long_description,
    classifiers=['Intended Audience :: Developers',
                 'License :: OSI Approved :: Zope Public License',
                 'Programming Language :: Python',
                ],
    author='Paul Wilson',
    author_email='paulalexwilson@gmail.com',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['manuelpi',],
    include_package_data = True,
    install_requires=['setuptools', 'manuel'],
    zip_safe = False,
    )
