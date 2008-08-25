from setuptools import setup, find_packages

long_description = (open("README.txt").read()
                    + '\n\n' +
                    open("CHANGES.txt").read())

setup(name='megrok.storm',
      version='0.1',
      description="Grok extension to deal with storm Libraray ",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Programming Language :: Python',
                   'Environment :: Web Environment',
                   'Framework :: Zope3',
                   'License :: OSI Approved :: Zope Public License',
                   ],
      keywords='',
      author='Christian Klinger',
      author_email='cklinger@novareto.de',
      url='http://pypi.python.org/pypi/megrok.storm',
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
          'grok',  # just for the ViewGrokker
	  'storm',
	  'pysqlite',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
