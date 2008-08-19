from setuptools import setup, find_packages
import sys, os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('src', 'z3c', 'vcsync', 'README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n'
    )

setup(name='z3c.vcsync',
      version='0.15',
      description="Synchronize object data with a version control system",
      long_description=long_description,
      package_dir={'': 'src'},
      packages=find_packages('src'),
      author="Martijn Faassen",
      author_email="faassen@startifact.com",
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'grok',
        'py == 0.9.1',
      ],
      license="ZPL 2.1",
      entry_points="""
      # -*- Entry points: -*-
      """,
      keywords = "zope3 grok web svn synchronization",
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
      )
