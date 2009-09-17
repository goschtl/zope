from setuptools import setup, find_packages

version = '0.1'

setup(name='gzo.plonepolicy',
      version=version,
      description="Plone policy package for Plone portion of the Grok web site.",
      long_description="""\
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone zope grok',
      author='Kevin Teague',
      author_email='kevin@bud.ca',
      url='http://svn.zope.org/repos/main/gzo.plonepolicy',
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
