##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Program to extract internationalization markup from Python Code,
Page Templates and ZCML.

This tool will extract all findable message strings from all
internationalizable files in your Zope 3 product. It only extracts message ids
of the specified domain. It defaults to the 'zope' domain and the zope.app
package.

Note: The Python Code extraction tool does not support domain registration, so
      that all message strings are returned for Python code.

Usage: extract.py [options]
Options:
    -h / --help
        Print this message and exit.
    -d / --domain <domain>
        Specifies the domain that is supposed to be extracted (i.e. 'zope')
    -p / --path <path>
        Specifies the package that is supposed to be searched
        (i.e. 'zope/app')
"""
__id__ = "$Id: extract.py,v 1.11 2003/08/20 18:21:13 philikon Exp $"

import os, sys, fnmatch
import getopt
import time
import tokenize
import traceback
from pygettext import safe_eval, normalize, make_escapes

__meta_class__ = type


pot_header = '''\
##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
msgid ""
msgstr ""
"Project-Id-Version: %(version)s\\n"
"POT-Creation-Date: %(time)s\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: Zope 3 Developers <zope3-dev@zope.org>\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=CHARSET\\n"
"Content-Transfer-Encoding: ENCODING\\n"
"Generated-By: zope/app/translation_files/extract.py\\n"

'''

def usage(code, msg=''):
    # Python 2.1 required
    print >> sys.stderr, __doc__
    if msg:
        print >> sys.stderr, msg
    sys.exit(code)

class POTEntry:
    """This class represents a single message entry in the POT file."""

    def __init__(self, msgid, comments=None):
        self.msgid = msgid
        self.comments = comments or ''

    def addComment(self, comment):
        self.comments += comment + '\n'

    def addLocationComment(self, filename, line):
        self.comments += '#: %s:%s\n' %(filename, line)

    def write(self, file):
        file.write(self.comments)
        from zope.i18n.messageid import MessageID
        if isinstance(self.msgid, MessageID) and \
               self.msgid != self.msgid.default:
            default = self.msgid.default.strip()
            file.write('# Default: %s\n' % normalize(default))
        file.write('msgid %s\n' % normalize(self.msgid))
        file.write('msgstr ""\n')
        file.write('\n')

    def __cmp__(self, other):
        return cmp(self.comments, other.comments)


class POTMaker:
    """This class inserts sets of strings into a POT file."""
    
    def __init__ (self, output_fn, path):
        self._output_filename = output_fn
        self.path = path
        self.catalog = {}


    def add(self, strings, base_dir=None):
        for msgid, locations in strings.items():
            if msgid == '':
                continue
            if msgid not in self.catalog:
                self.catalog[msgid] = POTEntry(msgid)

            for filename, lineno in locations:
                if base_dir is not None:
                    filename = filename.replace(base_dir, '')
                self.catalog[msgid].addLocationComment(filename, lineno)
                

    def _getProductVersion(self):
        # First, try to get the product version
        fn = os.path.join(self.path, 'version.txt')
        if os.path.exists(fn):
            return open(fn, 'r').read().strip()
        # Second, try to find a Zope version
        import zope
        fn = os.path.join(os.path.dirname(zope.__file__), 'version.txt')
        if os.path.exists(fn):
            return open(fn, 'r').read().strip()
        else:
            return 'Zope 3 (unknown version)'


    def write(self):
        
        file = open(self._output_filename, 'w')
        file.write(pot_header % {'time': time.ctime(),
                                 'version': self._getProductVersion()})
        
        # Sort the catalog entries by filename
        catalog = self.catalog.values()
        catalog.sort()

        # Write each entry to the file
        for entry in catalog:
            entry.write(file)
            
        file.close()


class TokenEater:
    """This is almost 100% taken from pygettext.py, except that I removed all
    option handling and output a dictionary."""
    
    def __init__(self):
        self.__messages = {}
        self.__state = self.__waiting
        self.__data = []
        self.__lineno = -1
        self.__freshmodule = 1
        self.__curfile = None

    def __call__(self, ttype, tstring, stup, etup, line):
        self.__state(ttype, tstring, stup[0])

    def __waiting(self, ttype, tstring, lineno):
        if ttype == tokenize.NAME and tstring in ['_']:
            self.__state = self.__keywordseen

    def __suiteseen(self, ttype, tstring, lineno):
        # ignore anything until we see the colon
        if ttype == tokenize.OP and tstring == ':':
            self.__state = self.__suitedocstring

    def __suitedocstring(self, ttype, tstring, lineno):

        # ignore any intervening noise
        if ttype == tokenize.STRING:
            self.__addentry(safe_eval(tstring), lineno, isdocstring=1)
            self.__state = self.__waiting
        elif ttype not in (tokenize.NEWLINE, tokenize.INDENT,
                           tokenize.COMMENT):
            # there was no class docstring
            self.__state = self.__waiting

    def __keywordseen(self, ttype, tstring, lineno):
        if ttype == tokenize.OP and tstring == '(':
            self.__data = []
            self.__msgid = ''
            self.__lineno = lineno
            self.__state = self.__openseen
        else:
            self.__state = self.__waiting

    def __openseen(self, ttype, tstring, lineno):
        if ttype == tokenize.OP and tstring == ')':
            # We've seen the last of the translatable strings.  Record the
            # line number of the first line of the strings and update the list 
            # of messages seen.  Reset state for the next batch.  If there
            # were no strings inside _(), then just ignore this entry.
            if self.__data or self.__msgid:
                if self.__msgid:
                    msgid = self.__msgid
                    default = ''.join(self.__data)
                else:
                    msgid = ''.join(self.__data)
                    default = None
                self.__addentry(msgid, default)
            self.__state = self.__waiting
        elif ttype == tokenize.OP and tstring == ',':
            self.__msgid = ''.join(self.__data)
            self.__data = []
        elif ttype == tokenize.STRING:
            self.__data.append(safe_eval(tstring))

    def __addentry(self, msg, default=None, lineno=None, isdocstring=0):
        if lineno is None:
            lineno = self.__lineno

        if default is not None:
            from zope.i18n.messageid import MessageID
            msg = MessageID(msg, default=default)
        entry = (self.__curfile, lineno)
        self.__messages.setdefault(msg, {})[entry] = isdocstring

    def set_filename(self, filename):
        self.__curfile = filename
        self.__freshmodule = 1

    def getCatalog(self):
        catalog = {}
        # Sort the entries.  First sort each particular entry's keys, then
        # sort all the entries by their first item.
        reverse = {}
        for k, v in self.__messages.items():
            keys = v.keys()
            keys.sort()
            reverse.setdefault(tuple(keys), []).append((k, v))
        rkeys = reverse.keys()
        rkeys.sort()
        for rkey in rkeys:
            rentries = reverse[rkey]
            rentries.sort()
            for msgid, locations in rentries:
                catalog[msgid] = []
                
                locations = locations.keys()
                locations.sort()

                for filename, lineno in locations:
                    catalog[msgid].append((filename, lineno))

        return catalog

                    
def app_dir():
    try:
        import zope.app
    except ImportError:
        # Couldn't import zope.app, need to add something to the Python
        # path

        # Get the path of the src
        path = os.path.abspath(os.path.dirname(sys.argv[0]))
        while not path.endswith('src'):
            path = os.path.dirname(path)
        sys.path.insert(0, path)

        import zope.app

    dir = os.path.dirname(zope.app.__file__)

    return dir


def find_files(dir, pattern, exclude=()):
    files = []

    def visit(files, dirname, names):
        files += [os.path.join(dirname, name)
                  for name in fnmatch.filter(names, pattern)
                  if name not in exclude]
        
    os.path.walk(dir, visit, files)

    return files


def py_strings(dir, domain="zope"):
    """Retrieve all Python messages from dir that are in the domain."""
    eater = TokenEater()
    make_escapes(0)
    for filename in find_files(dir, '*.py', 
                               exclude=('extract.py', 'pygettext.py')):
        fp = open(filename)
        try:
            eater.set_filename(filename)
            try:
                tokenize.tokenize(fp.readline, eater)
            except tokenize.TokenError, e:
                print >> sys.stderr, '%s: %s, line %d, column %d' % (
                    e[0], filename, e[1][0], e[1][1])
        finally:
            fp.close()            
    # XXX: No support for domains yet :(
    return eater.getCatalog()


def zcml_strings(dir, domain="zope"):
    """Retrieve all ZCML messages from dir that are in the domain."""
    from zope.app._app import config
    import zope
    dirname = os.path.dirname
    site_zcml = os.path.join(dirname(dirname(dirname(zope.__file__))),
                             "site.zcml")
    context = config(site_zcml, execute=False)
    return context.i18n_strings.get(domain, {})


def tal_strings(dir, domain="zope", include_default_domain=False):
    """Retrieve all TAL messages from dir that are in the domain."""
    # We import zope.tal.talgettext here because we can't rely on the
    # right sys path until app_dir has run
    from zope.tal.talgettext import POEngine, POTALInterpreter
    from zope.tal.htmltalparser import HTMLTALParser
    engine = POEngine()

    class Devnull:
        def write(self, s):
            pass

    for filename in find_files(dir, '*.pt'):
        try:
            engine.file = filename
            p = HTMLTALParser()
            p.parseFile(filename)
            program, macros = p.getCode()
            POTALInterpreter(program, macros, engine, stream=Devnull(),
                             metal=False)()
        except: # Hee hee, I love bare excepts!
            print 'There was an error processing', filename
            traceback.print_exc()

    # See whether anything in the domain was found
    if not engine.catalog.has_key(domain):
        return {}
    # We do not want column numbers.
    catalog = engine.catalog[domain].copy()
    # When the Domain is 'default', then this means that none was found;
    # Include these strings; yes or no?
    if include_default_domain:
        catalog.update(engine.catalog['default'])
    for msgid, locations in catalog.items():
        catalog[msgid] = map(lambda l: (l[0], l[1][0]), locations)
    return catalog


def main(argv=sys.argv):
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            'hd:p:',
            ['help', 'domain=', 'path='])
    except getopt.error, msg:
        usage(1, msg)

    domain = 'zope'
    path = app_dir()
    include_default_domain = True
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage(0)
        elif opt in ('-d', '--domain'):
            domain = arg
            include_default_domain = False
        elif opt in ('-p', '--path'):
            if not os.path.exists(arg):
                usage(1, 'The specified path does not exist.')
            path = arg
            # We might not have an absolute path passed in.
            if not path == os.path.abspath(path):
                cwd = os.getcwd()
                # This is for symlinks. Thanks to Fred for this trick.
                if os.environ.has_key('PWD'):
                    cwd = os.environ['PWD']
                path = os.path.normpath(os.path.join(cwd, arg))

    # When generating the comments, we will not need the base directory info,
    # since it is specific to everyone's installation
    src_start = path.find('src')
    base_dir = path[:src_start]

    maker = POTMaker(domain+'.pot', path)
    maker.add(py_strings(path, domain), base_dir)
    maker.add(zcml_strings(path, domain), base_dir)
    maker.add(tal_strings(path, domain, include_default_domain), base_dir)
    maker.write()


if __name__ == '__main__':
    main()
