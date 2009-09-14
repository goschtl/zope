from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='megrok.z3cform.layout',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Grok Form Templates Layout',
      author='Souheil Chelfouh',
      author_email='trollfot@gmail.com',
      url='',
      license='GPL',
      package_dir={'': 'src'},
      packages=find_packages('src', exclude=['ez_setup']),
      namespace_packages=['megrok', 'megrok.z3cform'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'megrok.z3cform.base',
          'megrok.pagetemplate',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
