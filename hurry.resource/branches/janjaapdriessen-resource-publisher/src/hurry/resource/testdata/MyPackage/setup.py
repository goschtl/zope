from setuptools import setup, find_packages

setup(name='mypackage',
      version='1.0dev',
      include_package_data=True,
      zip_safe=False,
      package_dir={'': 'src'},
      packages=find_packages('src'),
      install_requires=['setuptools', 'hurry.resource'],
      entry_points={
          'hurry.resource.libraries': [
              'foo = mypackage:foo',
          ]
      })
