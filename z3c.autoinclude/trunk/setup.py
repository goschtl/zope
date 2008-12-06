from setuptools import setup, find_packages

long_description = (open('README.txt').read()
                    + '\n\n' +
                    open('CHANGES.txt').read())

setup(name='z3c.autoinclude',
      version='0.2.3dev',
      description="Automatically include ZCML for dependencies.",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Ethan Jucovy, Robert Marianski, Martijn Faassen',
      author_email='zope-dev@zope.org',
      url='',
      license='Public Domain',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.dottedname',
	  'zope.interface',
	  'zope.configuration',
	  'zope.schema',
          'zc.buildout',
          # -*- Extra requirements: -*-
      ],
      extras_require={'test': ['zc.buildout',]},
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
