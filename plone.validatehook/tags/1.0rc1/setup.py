from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='plone.validatehook',
      version=version,
      description="Zope 2 publisher validation hook",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Wichert Akkerman',
      author_email='wichert@wiggy.net',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
#          'zope.event',
#          'zope.interface',
#          'zope.component',
      ],
      entry_points="""
      """,
      )

