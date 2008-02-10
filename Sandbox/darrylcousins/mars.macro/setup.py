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
        read('mars/macro/README.txt') +
        read('CHANGES.txt')),
    classifiers = ['Development Status :: 1 - Planning',
                    'Intended Audience :: Developers',
                    'License :: Other/Proprietary License',
                    'Programming Language :: Python',
                    'Operating System :: OS Independent',
                    'Topic :: Software Development :: Build Tools',
                    'Framework :: Zope3',
                    ],
    packages=find_packages(),
    namespace_packages=['mars'],
    zip_safe=True,
    license='ZPL',
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
