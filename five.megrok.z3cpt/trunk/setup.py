from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='five.megrok.z3cpt',
      version=version,
      description="Grok support for z3c.pt in Zope 2",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zope2 z3c pt grok',
      author='Sylvain Viollon',
      author_email='sylvain@infrae.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['five', 'five.megrok'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'five.pt',
          'five.grok',
          ],
      )
