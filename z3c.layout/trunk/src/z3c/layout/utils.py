import sys
import os

from urlparse import urlparse

def dotted_name(path):
    """Determine dotted name to path from the set of Python packages."""

    syspaths = sorted(
        sys.path, key=lambda syspath: root_length(syspath, path), reverse=True)

    syspath = syspaths[0]
    
    path = os.path.normpath(path)
    if not path.startswith(syspath):
        return None
    
    path = path[len(syspath):]
    
    # convert path to dotted filename
    if path.startswith(os.path.sep):
        path = path[1:]
        
    return path

def root_length(a, b):
    return b.startswith(a) and len(a) or 0

def rebase(tree, prefix):
    """Rebase resources.

    Parse through an lxml tree, adding the ``prefix`` to all tag
    attributes that point to URL-relative layout resources:

    Tag        Attribute
    -----------------------------
    img        src
    
    >>> from z3c.layout.utils import rebase
    >>> import lxml

    >>> html = '''\
    ... <html>
    ...   <head>
    ...      <link href="some/url" />
    ...   </head>
    ...   <body>
    ...      <img src="some/url" />
    ...      <img src="http://host/some/url" />
    ...   </body>
    ... </html>'''

    >>> tree = lxml.etree.fromstring(html)
    >>> rebase(tree, '++foo++')
    >>> print lxml.etree.tostring(tree, pretty_print=True)
    <html>
      <head>
         <link href="++foo++/some/url"/>
      </head>
      <body>
         <img src="++foo++/some/url"/>
         <img src="http://host/some/url"/>
      </body>
    </html>
    
    """

    for xpath, attribute in (('.//img', 'src'),
                             ('.//head/link', 'href')):
        for element in tree.findall('%s[@%s]' % (xpath, attribute)):
            value = element.get(attribute)
            protocol, host = urlparse(value)[:2]

            # rebase if host is trivial
            if not host:
                element.set(attribute, '%s/%s' % (prefix, value))
