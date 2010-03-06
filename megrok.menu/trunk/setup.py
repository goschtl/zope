from setuptools import setup, find_packages

long_description = (
    open("README.txt").read() + '\n\n' + open("CHANGES.txt").read())

test_requires = []

setup(name='megrok.menu',
      version='0.5dev',
      description="Grok extension to configure browser menus",
      long_description=long_description,
      keywords='',
      author='The Grok community',
      author_email='grok-dev@zope.org',
      url='http://pypi.python.org/pypi/megrok.menu',
      license='ZPL',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['megrok'],
      include_package_data=True,
      zip_safe=False,
      extras_require={'test': [
          'zope.component',
          'zope.interface',
          'zope.principalregistry',
          'zope.security',
          'zope.securitypolicy',
          'zope.site',
          'zope.testing',
          ]},
      install_requires=[
          'grokcore.component',
          'grokcore.security',
          'grokcore.view',
          'grokcore.viewlet',
          'martian',
          'setuptools',
          'zope.browsermenu',
          'zope.configuration',
          'zope.publisher',
      ],
      classifiers=[
          'Programming Language :: Python',
          'Environment :: Web Environment',
          'Framework :: Zope3',
          'License :: OSI Approved :: Zope Public License',
          ],
      )
