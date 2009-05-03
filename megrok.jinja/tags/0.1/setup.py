from setuptools import setup, find_packages
import os

version = '0.1'

long_description = (open('README.txt').read() +
                    '\n\n' +
                    open('CHANGES.txt').read())

setup(name='megrok.jinja',
      version=version,
      description="Jinja2 templates integration in Grok",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Zope Public License',
                   'Programming Language :: Python :: 2.5',
                   'Operating System :: OS Independent',
                   'Topic :: Internet :: WWW/HTTP',
                   ],
      keywords='grok Jinja2',
      author='Santiago Videla',
      author_email='santiago.videla@gmail.com',
      url="http://svn.zope.org/megrok.jinja/",
      license='ZPL',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['megrok'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'grokcore.component',
          'grokcore.view',
          'grokcore.viewlet',
          'Jinja2',
          'simplejson',
          'pyyaml'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
