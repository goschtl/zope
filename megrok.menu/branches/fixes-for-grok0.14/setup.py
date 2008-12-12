from setuptools import setup, find_packages

long_description = (open("README.txt").read()
                    + '\n\n' +
                    open("CHANGES.txt").read())

setup(name='megrok.menu',
      version='0.2dev',
      description="Grok extension to configure browser menus",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Programming Language :: Python',
                   'Environment :: Web Environment',
                   'Framework :: Zope3',
                   'License :: OSI Approved :: Zope Public License',
                   ],
      keywords='',
      author='Philipp von Weitershausen',
      author_email='philipp@weitershausen.de',
      url='http://pypi.python.org/pypi/megrok.menu',
      license='ZPL',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['megrok'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'martian',
          'grokcore.component',
          'grokcore.view',
          'grokcore.security',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
