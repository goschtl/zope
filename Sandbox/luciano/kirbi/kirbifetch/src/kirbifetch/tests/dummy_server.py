#!/usr/bin/env python

import sys
from SimpleXMLRPCServer import SimpleXMLRPCServer
from pprint import pprint

PORT = 8080

class Server(object):
    # pending will behave like an ordered set (no duplicates)
    pending = []

    def __init__(self, pending = None):
        if pending is not None:
            self.pending = pending

    def add_pending_isbns(self, isbns):
        print 'add%s' % isbns
        added = 0
        for isbn in isbns:
            if isbn not in self.pending:
                self.pending.append(isbn)
                added += 1
        return added
    
    def del_pending_isbns(self, isbns):
        print 'del%s' % isbns
        deleted = 0
        for isbn in isbns:
            if isbn in self.pending:
                self.pending.remove(isbn)
                deleted += 1
        return deleted
    
    def dump_pending_isbns(self, max=0):
        print 'dump%s' % self.pending
        if max == 0:
            max = len(self.pending)
        dump = self.pending[:max]
        self.pending = self.pending[max:]
        return dump
    
    def show_pending_isbns(self):
        print 'list%s' % self.pending
        return self.pending
    
    def add_books(self, books):
        pprint(books)
        return len(books)


if __name__=='__main__':
    if len(sys.argv) not in [2,3]:
        print 'usage: %s <filename> [<n>]' % sys.argv[0]
        print '  <filename> names a text file containing' 
        print '             ISBN-13 numbers, one per line'
        print '  <n> (optional) max ISBN numbers loaded'
        sys.exit()
        
    pending = file(sys.argv[1]).read().split()    
    if len(sys.argv) == 3:
        pending = pending[:int(sys.argv[2])]

    srv = Server(pending)

    xmlrpc = SimpleXMLRPCServer(("localhost", PORT))

    xmlrpc.register_instance(srv)

    print 'SimpleXMLRPCServer running on port %s...', PORT    
    xmlrpc.serve_forever()


