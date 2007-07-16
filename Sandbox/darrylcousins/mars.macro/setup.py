import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='mars.macro',
    version='0.1',
    author='Darryl Cousins',
    author_email='darryl.cousins@tfws.org.nz',
    url='http://www.tfws.org.nz/mars',
    description="""\
This package uses ``martian`` and ``grok`` to register template macros
for applications built on the ``zope`` framework.""",
    long_description=(
        read('src/mars/macro/README.txt')
        ),
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='ZPL',
    dependency_links = ['http://download.zope.org/distribution'],
    extras_require = dict(
                test=['zope.app.testing',
                      'zope.testbrowser',
                      'z3c.template',
                      'mars.template',
                      'mars.layer',
        ]
                ),
    install_requires = [
        'setuptools',
        'grok',
        'z3c.macro',
        ],
)
