from setuptools import setup, find_packages

setup(name='z3c.evalexception',
      version = '2.0',
      license='ZPL 2.1',
      description="Paste's interactive exception debugger for Zope 3",
      author='Philipp von Weitershausen',
      author_email='philipp@weitershausen.de',
      long_description=open('README.txt').read(),
      classifiers = ['Development Status :: 5 - Production/Stable',
                     'Environment :: Web Environment',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: Zope Public License',
                     'Programming Language :: Python',
                     'Operating System :: OS Independent',
                     'Topic :: Internet :: WWW/HTTP',
                     'Framework :: Zope3',
                     'Framework :: Paste',
                     ],

      packages=find_packages(),
      namespace_packages=['z3c'],
      install_requires=['setuptools', 'Paste', 'zope.security'],
      zip_safe=True,
      entry_points="""
      [paste.filter_app_factory]
      main = z3c.evalexception:zope_eval_exception
      ajax = z3c.evalexception:zope_eval_exception
      pdb = z3c.evalexception:post_mortem_debug
      """
      )
