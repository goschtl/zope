from setuptools import setup, find_packages

setup(
    name = "lovely.flvplayer",
    version = "0.1",
    author = "Lovely Systems",
    author_email = "office@lovelysystems.com",
    description = "Flash Player for Zope 3",
    license = "ZPL 2.1",
    keywords = "zope3 flv flash player video",
    url='http://svn.zope.org/lovely.flvplayer',
    classifiers = [
        'Development Status :: 3 - Alpha',
        "License :: OSI Approved :: Zope Public License",
        "Framework :: Zope :: UI",
        ],
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['lovely'],
    install_requires = ['zope.i18nmessageid'],
    zip_safe=False,
    )
