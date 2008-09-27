from setuptools import setup, find_packages
import sys
version = '1.0a4'

install_requires = [
    'setuptools',
    'zope.interface',
    'zope.component',
    'zope.i18n >= 3.5',
    'PDIS_XPath',
    ]

if sys.version_info[:3] < (2,5,0):
    install_requires.append('elementtree')

setup(name='chameleon.core',
      version=version,
      description="Attribute language template compiler",
      long_description=open("README.txt").read() + open("CHANGES.txt").read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: XML",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Malthe Borch and the Zope Community',
      author_email='zope-dev@zope.org',
      url='',
      license='BSD',
      namespace_packages=['chameleon'],
      packages = find_packages('src'),
      package_dir = {'':'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      extras_require={'lxml':['lxml>=2.1.1']},
      )
