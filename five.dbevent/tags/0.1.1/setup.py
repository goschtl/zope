from setuptools import setup, find_packages
import os

version = '0.1.1'

setup(name='five.dbevent',
      version=version,
      description="ZODB Database startup events backported to Zope 2",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Zope2"],
      keywords='zope2 zodb',
      author='Godefroid Chapelle and Jean-Francois Roche',
      author_email='zope-dev@zope.org',
      url='http://pypi.python.org/pypi/five.dbevent',
      license='ZPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['five'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.monkeypatcher'])
