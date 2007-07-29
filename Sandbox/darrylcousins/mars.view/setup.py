import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='mars.view',
    version='0.1',
    author='Darryl Cousins',
    author_email='darryl.cousins@tfws.org.nz',
    url='http://www.tfws.org.nz/mars',
    description="""\
This package uses ``martian`` and ``grok`` to register views
for applications built on the ``zope`` framework.""",
    long_description=(
        read('src/mars/view/README.txt') +
        read('CHANGES.txt')
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
                      'mars.layer',
                      'mars.template',
        ]
                ),
    install_requires = [
        'setuptools',
        'grok',
        'z3c.template',
        'z3c.pagelet',
        ],
)
