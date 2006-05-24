from setuptools import setup, find_packages

setup(
    name="zc.datetimewidget",
    version="0.5",
    install_requires=['zc.resourcelibrary >= 0.5',
                      'zc.i18n >= 0.5'],
    dependency_links=['http://download.zope.org/distribution/',],
  
    packages=find_packages('src', exclude=["*.tests", "*.ftests"]),
    
    package_dir= {'':'src'},
    
    namespace_packages=['zc'],

    package_data = {
    '': ['*.txt', '*.zcml', '*.gif', '*.js'],
    'zc.datetimewidget': ['resources/*.css',
                          'resources/*.js',
                          'resources/*.gif',
                          'resources/lang/*'],
    },

    zip_safe=False,
    author='Zope Project',
    author_email='zope3-dev@zope.org',
    description="""\
zc.datetimewidget has improved javascript based widgets for the entry of date
and datetime information.
""",
    license='ZPL',
    keywords="zope zope3",
    )
