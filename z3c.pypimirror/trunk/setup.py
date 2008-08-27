from setuptools import setup, find_packages, find_packages


CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Zope Public License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
]

desc = open('README.txt').read().strip()
changes = open('CHANGES.txt').read().strip()
long_description = desc + '\n\nChanges\n=======\n\n'  + changes

setup(
    name='z3c.pypimirror',
    version='0.1.1',
    author='Daniel Kraft et al.',
    author_email='dk@d9t.de',
    description='A module for building a complete or a partial PyPI mirror',
    long_description=long_description,
    maintainer='Daniel Kraft et al.',
    maintainer_email='dk@d9t.de',
    classifiers=CLASSIFIERS,
    package_dir = {'': 'src'},
    namespace_packages=['z3c', 'z3c.pypimirror'],
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,
    package_data = {
        '': ['*.sample'],
    },
    install_requires = ['setuptools',
                        'zc.lockfile',
                        'BeautifulSoup'],
    extras_require = {
        'test': [ 'zc.buildout' ],
    },
    entry_points = dict(console_scripts=[
        'pypimirror = z3c.pypimirror.mirror:run',
        ])
    )
