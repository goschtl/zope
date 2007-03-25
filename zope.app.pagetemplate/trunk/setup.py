from setuptools import setup, find_packages, Extension

setup(name='zope.app.pagetemplate',
      version='0.1',
      url='http://svn.zope.org/zope.app.pagetemplate',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',

      packages=find_packages('src'),
      package_dir={'': 'src'},

      namespace_packages=['zope', 'zope.app'],
      include_package_data=True,
      install_requires=[
          'setuptools',
          'zope.pagetemplate',
          ],
      extras_require={
          "test": [
              "zope.app.authentication",
              "zope.app.container",
              "zope.app.form",
              "zope.app.securitypolicy",
              "zope.app.zcmlfiles",
              ],
          },
      zip_safe=False,
      )
