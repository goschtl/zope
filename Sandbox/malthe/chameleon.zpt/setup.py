from setuptools import setup, find_packages

version = '1.0b6'

install_requires = [
    'setuptools',
    'zope.interface',
    'zope.component',
    'zope.security',
    'zope.configuration',
    'zope.i18n >= 3.5',
    'chameleon.core >=1.0b12',
    ]
test_requires = install_requires + [
    'zope.configuration',
    'zope.security'
    ]

setup(name='chameleon.zpt',
      version=version,
      description="Zope Page Template engine based on Chameleon",
      long_description=open("README.txt").read(),
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
      extras_require = {'test': test_requires},
      )
