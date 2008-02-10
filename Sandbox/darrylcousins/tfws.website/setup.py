import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='tfws.website',
    version='0.1',
    author='Darryl Cousins',
    author_email='darryl.cousins@tfws.org.nz',
    url='http://www.tfws.org.nz/mars',
    description="""\
This package uses ``martian`` and ``grok`` to build a simple web
application on the ``zope3`` framework.""",
    long_description=(
        read('src/tfws/website/README.txt') +
        read('CHANGES.txt')
        ),
    classifiers = ['Development Status :: 1 - Planning',
                    'Intended Audience :: Developers',
                    'License :: Other/Proprietary License',
                    'Programming Language :: Python',
                    'Operating System :: OS Independent',
                    'Topic :: Software Development :: Build Tools',
                    'Framework :: Zope3',
                    ],
    packages=find_packages(),
    namespace_packages=['tfws'],
    zip_safe=True,
      install_requires=['setuptools',
                        'lxml',
                        'grok',
                        'zope.app.file',
                        'z3c.etestbrowser',
                        'z3c.breadcrumb',
                        'z3c.configurator',
                        'z3c.form',
                        'z3c.formjs',
                        'z3c.formui',
                        'z3c.layer',
                        'z3c.pagelet',
                        'z3c.schema',
                        'z3c.template',
                        'z3c.testing',
                        'z3c.viewlet',
                        'z3c.zrtresource',
                        'z3c.formdemo',
                        'zc.resourcelibrary',
                        'zc.table',
                        'jquery.javascript',
                        'jquery.layer',
                        # Add extra requirements here
                        ],
      entry_points="""
      [paste.app_factory]
      main = tfws.website.application:application_factory
      """,
      )
