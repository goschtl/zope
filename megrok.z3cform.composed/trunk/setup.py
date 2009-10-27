from os.path import join
from setuptools import setup, find_packages

name = 'megrok.z3cform.composed'
version = '0.1'
readme = open(join('src', 'megrok', 'z3cform', 'composed', 'README.txt')).read()
history = open(join('docs', 'HISTORY.txt')).read()

install_requires = [
    'setuptools',
    'z3c.form',
    'megrok.z3cform.base',
    'grokcore.view',
    'grokcore.viewlet',
    'grokcore.component',
    'zope.component',
    ]

tests_require = install_requires + [
    'zope.testing',
    'zope.app.testing',
    'zope.app.zcmlfiles',
    ]

setup(name=name,
      version=version,
      description="Composed forms for Grok, using z3c.form.",
      long_description = readme + '\n\n' + history,
      keywords='z3cform Grok Form',
      author='Souheil Chelfouh',
      author_email='trollfot@gmail.com',
      url='',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['megrok', 'megrok.z3cform'],
      include_package_data=True,
      zip_safe=False,
      tests_require = tests_require,
      install_requires = install_requires,
      extras_require = {'test': tests_require},
      test_suite="megrok.z3cform.composed",
      classifiers = [
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Framework :: Zope3',
          'Intended Audience :: Other Audience',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          ],
      )
