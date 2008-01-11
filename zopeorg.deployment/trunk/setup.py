from setuptools import setup, find_packages

version = '1.0dev'

setup(name='zopeorg.deployment',
      version=version,
      description="Deployment package for www.zope.org",
      long_description="""\
""",
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Wichert Akkerman',
      author_email='wichert@wiggy.net',
      url='http://svn.plone.org/svn/plone/plone.example',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zopeorg'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          "zopeorg.theme",
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
