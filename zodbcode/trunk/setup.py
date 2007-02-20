from setuptools import setup, find_packages, Extension

setup(name='zodbcode',
      version='0.1dev',
      url='http://svn.zope.org/zodbcode',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',

      packages=find_packages('src'),
      package_dir = {'': 'src'},
      include_package_data = True,

      zip_safe = False,
      )

