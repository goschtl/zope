from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='five.megrok.layout',
      version=version,
      description="A grok layout component package for Zope 2",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Zope2",
        ],
      keywords='layout grok zope2',
      author='Sylvain Viollon and Vincent Fretin',
      author_email='grok-dev@zope.org',
      url='http://svn.zope.org/five.megrok.layout/',
      license='ZPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['five', 'five.megrok'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'five.grok',
          'grokcore.view >= 1.12.1',
          'megrok.layout >= 0.8',
      ],
      )
