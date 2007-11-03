from setuptools import setup, find_packages

version = '0.1'

setup(name='gzo.plonesmashtheme',
      version=version,
      description="A community generated theme for the Plone portion of the Grok web site",
      long_description="""\
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope plone theme grok',
      author='Grok Community',
      author_email='grok-dev@zope.org',
      url='http://svn.zope.org/repos/main/gzo.plonesmashtheme',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['gzo'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
