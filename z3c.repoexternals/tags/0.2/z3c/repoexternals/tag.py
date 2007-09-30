#!/usr/bin/python

import sys, re, optparse
import pysvn

usage = "usage: %prog [options] externals"
parser = optparse.OptionParser(usage=usage)

external = re.compile(
    r'^(\s*#?\s*)([^#\s]+)(\s*)(.*?)(\s*)(\S+)(\s*)$')

def run(externals):
    client = pysvn.Client()
    external_match = external.match
    for line in externals:
        match = external_match(line)
        if match is not None and client.is_url(match.group(6)):
            try:
                info = client.info(match.group(2))
            except pysvn.ClientError:
                info = None
            if info is not None:
                yield match.expand(
                    r'\1\2\3-r %s%s\6\7' % (info.revision.number,
                                            match.group(5) or ' '))
            else:
                yield line
        else:
            yield line

def main():
    options, args = parser.parse_args()

    if len(args) != 1:
        parser.error("requires externals")

    externals, = args
    if externals == '-':
        externals = sys.stdin
    else:
        externals = file(externals)

    for line in run(externals):
        print line,

if __name__ == '__main__':
    main()
