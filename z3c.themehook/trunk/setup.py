from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='z3c.themehook',
      version=version,
      description="Zope3 publication theme hook",
      long_description="""z3c.themehook provides a publisher hook for theming mechanisms.""",
      classifiers=[
          'Framework :: Zope3',
          'Programming Language :: Python',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
      keywords='Zope3 theming',
      author='Lennart Regebro',
      author_email='regebro@gmail.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zope'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
