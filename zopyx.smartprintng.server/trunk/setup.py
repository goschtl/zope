from setuptools import setup, find_packages
import os

version = '0.1.2'

setup(name='zopyx.smartprintng.server',
      version=version,
      description="ZOPYX SmartPrintNG Server",
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
      namespace_packages=['zopyx', 'zopyx.smartprintng'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'twisted',
          'uuid',
          'zopyx.convert2',
          # -*- Extra requirements: -*-
      ],
      entry_points=dict(
          console_scripts=['smartprintng_server=zopyx.smartprintng.server.cli:main']
      )
      )
