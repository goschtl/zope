from setuptools import setup, find_packages
import os

version = '1.0.1'

setup(name='z3c.boston',
      version=version,
      description="A version of the zope.app.boston skin which support pagelets.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zope3 pagelet form skin',
      author='Kevin Gill and the Zope Community',
      author_email='zope-dev@zope.org',
      url='http://pypi.python.org/pypi/z3c.boston',
      license='ZPL 2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'zope.app.boston',
          'z3c.pagelet',
          'z3c.formui',
          'z3c.layer',
          'jquery.layer',
          'z3c.template',
          'z3c.viewlet',
          'z3c.form',
          'z3c.formjs',
          'z3c.zrtresource',
          'jquery.javascript',
          'jquery.layer',
      ],
      extras_require = dict(
          test = [
            'zope.app.testing',
            'zope.testbrowser',
            'zope.app.dtmlpage',
            'zope.app.onlinehelp',
            'zope.app.securitypolicy',
            'zope.app.zcmlfiles'
          ]
      ),
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
