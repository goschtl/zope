import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='grokadmin',
      version='0.1.0',
      description="GrokAdmin: The Grok administration and development UI",
      long_description=(
        read('README.txt')
        ),
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Development Status :: 1 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3 :: Grok'], 
      keywords="zope3 grok grokadmin",
      author="Uli Fouquet and lots of contributors from grok community",
      author_email="grok-dev@zope.org",
      url="http://svn.zope.org/Sandbox/ulif/grokadmin",
      license="ZPL 2.1",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      namespace_packages = ['grokadmin'],
      install_requires=['setuptools',
                        'grok',
                        'zope.component',
                        'zope.interface',
                        ],
      entry_points="""
      # Add entry points here
      """,
      )
