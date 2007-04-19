from setuptools import setup, find_packages

setup(
    name = "z3c.extfile",
    version = "0.1",
    author = "Zope Contributors",
    author_email = "zope3-dev@zope.org",
    description = "Large file handling for zope3",
    license = "ZPL 2.1",
    keywords = "zope3 external file",
    url = 'http://svn.zope.org/z3c.extfile',
    classifiers = [
        'Development Status :: 3 - Alpha',
        "License :: OSI Approved :: Zope Public License",
        "Framework :: Zope :: UI"],
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    zip_safe = False,
    install_requires = [
        'setuptools',
        'zope.component',
        'zope.interface',
        'zope.publisher',
        'zope.schema',
        'zope.thread',
        'zope.app.wsgi',
        'zope.app.file',
        'ZODB3'],
    dependency_links = [
        'http://download.zope.org/distribution/'],
    )
