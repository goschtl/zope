from setuptools import setup, find_packages
import os

version = '0.1'

install_requires = [
    'setuptools',
    'grokcore.component',
    'grokcore.viewlet',
    'grokcore.view >= 1.1',
    'grokcore.formlib',
    'z3c.form',
    'megrok.layout >= 0.6',
    'megrok.pagetemplate',
    ]


test_requires = install_requires + ['grok >= 0.14',]


setup(name='megrok.z3cform.base',
      version=version,
      description="megrok extension for z3cform",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Christian Klinger',
      author_email='cklinger@novareto.de',
      url='',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['megrok', 'megrok.z3cform'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      extras_require={'test': test_requires,},
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
