from setuptools import setup, find_packages
import os

version = '2.0.0b3'

setup(name='zopyx.smartprintng.core',
      version=version,
      description="SmartPrintNG core engine",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='SmartPrintNG Zope Python',
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
          'zope.component',
          'zope.pagetemplate',
          'zope.app.testing',
          'zopyx.convert2',
          # -*- Extra requirements: -*-
      ],
      extras_require=dict(test=['pysqlite', 'zope.testing']),
      entry_points={'console_scripts': ['spng-demo=zopyx.smartprintng.core.demo.demo_app:main',
                                        'spng-demo2=zopyx.smartprintng.core.demo2.demo_app:main',
                         ]},
      )
