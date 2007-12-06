from setuptools import setup, find_packages

version = '0.1'

setup(name='zopeorg.theme',
      version=version,
      description="Plone 3.0 visual theme for zope.org project",
      long_description="""\
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zope plone theme',
      author='Denis Mishunov',
      author_email='denis@webcouturier.com',
      url='http://zope.org',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zopeorg'],
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
