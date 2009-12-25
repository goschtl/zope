from setuptools import setup, find_packages
import os

version = '0.1.5'

setup(name='zope.z2release',
      version=version,
      description="Zope 2 release helper",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      url='',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zope'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points=dict(console_scripts=[
        'z2_kgs=zope.z2release.cli:main'
        ]),
      )
