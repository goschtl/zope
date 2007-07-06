import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='mars.adapter',
    version='0.1',
    author='Darryl Cousins',
    author_email='darryl.cousins@tfws.org.nz',
    url='http://www.tfws.org.nz/martian',
    description="""\
Martian is a library that allows the embedding of configuration
information in Python code. Martian can then grok the system and
do the appropriate configuration registrations.

This package uses martian to define z3c.adapter macros""",
    long_description=(
        read('src/mars/adapter/README.txt')
        ),
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='ZPL',
    install_requires=['setuptools',
                      'martian',
                      'grok',
                     ],
)


