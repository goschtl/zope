from setuptools import setup, find_packages
import os

version = '0.0.3'

long_description = (
    open('README.txt').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='collective.zestreleaser.aftercheckoutaction',
      version=version,
      description="Execute a user defined shell action after clean checkout",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Patrick Gerken',
      author_email='gerken@starzel.de',
      url='https://github.com/do3cc/collective.zestreleaser.aftercheckoutaction',
      license='bsd',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['collective', 'collective.zestreleaser'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zest.releaser>=3.12',
          # -*- Extra requirements: -*-
      ],
      entry_points="""

      # -*- Entry points: -*-
      [zest.releaser.releaser.after_checkout]
      action=collective.zestreleaser.aftercheckoutaction:action
      """,
      )
