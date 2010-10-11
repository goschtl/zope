from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='z3c.taskqueue_ui',
      version=version,
      description="UI (views) for z3c.taskqueue",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'z3c.taskqueue',
          'z3c.table',
      ],
      extras_require=dict(test=['zope.app.testing',
                                  'zope.testing',
                                  'zope.app.securitypolicy',
                                  'zope.app.zcmlfiles',
                                  'zope.app.authentication',
                                  'zope.app.component',
                                  'zope.app.folder',
                                  'zope.login',
                                  'zope.securitypolicy',
                                  'zope.testbrowser',
                                  ]),
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
