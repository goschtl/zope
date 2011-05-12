import os
from setuptools.extension import Extension
from setuptools import setup, find_packages

# generic helpers primarily for the long_description
try:
    import docutils
except ImportError:
    def validateReST(text):
        return ''
else:
    import docutils.utils
    import docutils.parsers.rst
    import StringIO
    def validateReST(text):
        doc = docutils.utils.new_document('validator')
        # our desired settings
        doc.reporter.halt_level = 5
        doc.reporter.report_level = 1
        stream = doc.reporter.stream = StringIO.StringIO()
        # docutils buglets (?)
        doc.settings.tab_width = 2
        doc.settings.pep_references = doc.settings.rfc_references = False
        doc.settings.trim_footnote_reference_space = None
        # and we're off...
        parser = docutils.parsers.rst.Parser()
        parser.parse(text, doc)
        return stream.getvalue()

def text(*args, **kwargs):
    # note: distutils explicitly disallows unicode for setup values :-/
    # http://docs.python.org/dist/meta-data.html
    tmp = []
    for a in args:
        if a.endswith('.txt'):
            f = open(os.path.join(*a.split('/')))
            tmp.append(f.read())
            f.close()
            tmp.append('\n\n')
        else:
            tmp.append(a)
    if len(tmp) == 1:
        res = tmp[0]
    else:
        res = ''.join(tmp)
    out = kwargs.get('out')
    if out is True:
        out = 'TEST_THIS_REST_BEFORE_REGISTERING.txt'
    if out:
        f = open(out, 'w')
        f.write(res)
        f.close()
        report = validateReST(res)
        if report:
            print report
            raise ValueError('ReST validation error')
    return res
# end helpers; below this line should be code custom to this package

methodwrapper = Extension(
    name='zc.twist._methodwrapper',
    sources=[os.path.join('src','zc','twist','_methodwrapper.c')],
    )

setup(
    name='zc.twist',
    version='1.3.2dev',
    packages=find_packages('src'),
    url='http://pypi.python.org/pypi/zc.twist',
    package_dir={'':'src'},
    namespace_packages=['zc'],
    zip_safe=False,
    author='Zope Project',
    author_email='zope-dev@zope.org',
    description=open('README.txt').read(),
    long_description=text(
        "src/zc/twist/README.txt",
        '=======\nChanges\n=======\n\n',
        "CHANGES.txt", out=True),
    license='ZPL',
    install_requires=[
        'ZODB3',
        'Twisted>=8.0.1', # 8.0 was setuptools compatible
        'zope.component',
        'setuptools',
        'zope.testing',
        ],
    include_package_data=True,
    ext_modules=[methodwrapper],
    )
