from setuptools import setup, find_packages

setup(
    name='grokdocs',
    install_requires=['docutils',
                      'zope.pagetemplate',
                      'zope.app.renderer',
                      'Pygments'
                      ],
    py_modules = ['grok2html', 'grokref.grokref2html'],
    entry_points="""
    [console_scripts]
    grok2html = grok2html:main
    grokref2html = grokref.grokref2html:main
    """
    )
