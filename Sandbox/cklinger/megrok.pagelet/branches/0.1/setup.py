from setuptools import setup, find_packages

long_description = (open("README.txt").read()
                    + '\n\n' +
                    open("CHANGES.txt").read())

setup(name='megrok.pagelet',
      version='0.1',
      description="z3c.template / z3c.layout support for Grok",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Programming Language :: Python',
                   'Environment :: Web Environment',
                   'Framework :: Zope3',
                   'License :: OSI Approved :: Zope Public License',
                   ],
      keywords='',
      author='',
      author_email='',
      url='http://pypi.python.org/pypi/megrok.pagelet',
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
	  'z3c.template',
          'grok',  # just for the ViewGrokker
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
