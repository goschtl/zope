#!/usr/bin/env python

import sys
from SimpleXMLRPCServer import SimpleXMLRPCServer

PORT = 8080

def list_pending_isbns():
    return pending

def del_pending_isbns(isbns):
    deleted = 0
    for isbn in isbns:
        if isbn in pending:
            pending.remove(isbn)
            deleted += 1
    return deleted

if __name__=='__main__':
    if len(sys.argv) != 2:
        print 'usage: %s <filename>' % sys.argv[0]
        print '  <filename> names a text file containing' 
        print '             ISBN-13 numbers, one per line'
        sys.exit()

    pending = file(sys.argv[1]).read().split()

    server = SimpleXMLRPCServer(("localhost", PORT))
    server.register_introspection_functions()

    server.register_function(list_pending_isbns)
    server.register_function(del_pending_isbns)

    print 'SimpleXMLRPCServer running on port %s...', PORT    
    server.serve_forever()


