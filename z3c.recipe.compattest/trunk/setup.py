from setuptools import setup, find_packages


setup(name='z3c.recipe.compattest',
      version = '1.0dev',
      author='Grok Contributors',
      author_email='grok-dev@zope.org',
      description='Tool to create test environement for KGS.',
      long_description=open(
        os.path.join('src', 'z3c', 'recipe', 'compattest', 'README.txt')).read(),
      keywords = "zope3 setuptools egg kgs",
      classifiers = [
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Operating System :: OS Independent',
          'Framework :: Zope3'],
      url='',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['z3c', 'z3c.recipe'],
      install_requires=[
          'setuptools',
          'zc.buildout',
          'zc.recipe.testrunner',
          ],
      extras_require=dict(test=[
            'zope.dottedname',
          ]),
      entry_points = {
          'zc.buildout': ['default = z3c.recipe.compattest.recipe:Recipe'],
          },
      include_package_data = True,
      zip_safe = True,
      )
