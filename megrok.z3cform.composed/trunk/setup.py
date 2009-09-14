from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='megrok.z3cform.composed',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='z3cform Grok Form',
      author='Souheil Chelfouh',
      author_email='trollfot@gmail.com',
      url='',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['megrok', 'megrok.z3cform'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'z3c.form',
          'megrok.z3cform.base',
          'grokcore.view',
          'grokcore.viewlet',
          'zope.component',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
