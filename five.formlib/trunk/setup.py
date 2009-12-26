from setuptools import setup

version = '1.0'

setup(name='five.formlib',
      version=version,
      url='http://pypi.python.org/pypi/five.formlib',
      license='ZPL 2.1',
      description='zope.formlib integration for Zope 2',
      author='Zope Foundation',
      author_email='zope-dev@zope.org',
      long_description=open("README.txt").read() + "\n" + 
                       open("CHANGES.txt").read(),
      classifiers=[
          'Environment :: Web Environment',
          'Framework :: Zope2',
          'License :: OSI Approved :: Zope Public License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Internet :: WWW/HTTP :: Site Management',
      ],
      keywords='zope zope2 five formlib',
      packages=['five', 'five.formlib'],
      package_dir = {'': 'src'},
      namespace_packages=['five',],
      include_package_data = True,
      extras_require=dict(
          test=[]
          ),
      install_requires=[
        'Zope2',
        'setuptools',
        'zope.formlib',
        'zope.app.form',
      ],
      zip_safe = False,
      )
