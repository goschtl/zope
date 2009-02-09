""" stx2rst -- convert structured text to restructured text.

Usage:  stx2rst [OPTIONS]

Options include:

o '--input' / '-i'      Open the named file for input 
                        if not passed, use stdin).

o '--output' / '-o'     Open the named file for output 
                        if not passed, use stdout).
"""
import getopt
import sys

from docutils.writers import UnfilteredWriter
from zope.structuredtext.document import Document
from zope.structuredtext.stng import structurize
from stxutils.restify import restify

def usage(msg='', rc=1):
    print __doc__
    if msg:
        print
        print msg
    print
    sys.exit(rc)

def main(argv=None):

    input = sys.stdin
    output = sys.stdout

    if argv is None:
        argv = sys.argv[1:]

    try:
        opts, args = getopt.gnu_getopt(argv, 'i:o:h?',
                                            ['--input=',
                                             '--output=',
                                             '--help',
                                            ])
    except getopt.GetoptError:
        usage()

    if args:
        usage('No arguments allowed!')

    for k, v in opts:
        if k in ('-h', '-?', '--help'):
            usage(rc=2)
        elif k in ('-i', '--input'):
            input = open(v, 'r')
        elif k in ('-o', '--output'):
            output = open(v, 'w')
        else:
            usage()

    raw = input.read()
    st = structurize(raw)
    doc = Document()(st)
    rst = restify(doc)
    output.write(rst)


if __name__ == '__main__':
    import sys
    main(sys.argv)
