#!/usr/bin/env python
# encoding: utf-8

from lxml import etree
from twisted.internet import reactor
from twisted.web import xmlrpc, client
from os import path

import source_amazon as amazon

from pprint import pprint

KEEP_FILES = True
# directory where XML files will be saved (include trailing slash)

POLL_INTERVAL = 1 # minimum seconds to wait between calls to fetch.poll

class Fetch(object):
    
    def __init__(self, xmlrpc_url, poll, callback, source):
        self.pollServer = xmlrpc.Proxy(xmlrpc_url)
        self.pollMethod = poll
        self.callback = callback
        self.source = source
        
    def poll(self):
        deferred = self.pollServer.callRemote(self.pollMethod)
        deferred.addCallback(self.polled).addErrback(self.pollError)
    
    def polled(self, isbns):
        print 'polled: ', ' '.join(isbns)
        i = 0
        if isbns:
            # fetch max_ids_per_request, and one request per second
            for i, start in enumerate(range(0,len(isbns),
                                            self.source.max_ids_per_request)):
                end = start + self.source.max_ids_per_request
                reactor.callLater(i, self.downloadItemsPage, isbns[start:end])
        reactor.callLater(i+POLL_INTERVAL, self.poll)
            
    def pollError(self, error):
        print 'Error in deferred poll call:', error
        # if there was an error, wait a bit longer to try again
        reactor.callLater(POLL_INTERVAL*4, self.poll)
            
    def downloadItemsPage(self, isbns):
        url = self.source.buildMultipleBookDetailsURL(isbns)
        deferred = client.getPage(url)
        deferred.addCallback(self.downloadedItemsPage, isbns)
        deferred.addErrback(self.downloadError, url)
          
    def downloadedItemsPage(self, xml, isbns):
        book_list = self.source.parseMultipleBookDetails(xml)
        deferred = self.pollServer.callRemote(self.callback, book_list)
        deferred.addCallback(self.uploaded).addErrback(self.uploadError)
        for book in book_list:
            url = book.get('image_url')
            if url:
                filename = book.get('isbn13',book['source_item_id'])
                filename += '.' + url.split('.')[-1]
                deferred = client.getPage(url)
                deferred.addCallback(self.downloadedImage, filename)
                deferred.addErrback(self.downloadError, url)
                
        if KEEP_FILES:
            filename = '_'.join(isbns)+'.xml'
            out = file(path.join(self.source.name,filename), 'w')
            out.write(xml.replace('><','>\n<'))
            out.close()

    
    def downloadedImage(self, bytes, filename):
        # XXX: find a proper way to calculate the static image dir
        dest = '../../..'
        dest = path.join(dest,'src','kirbi','static','covers','large'
                            ,filename)
        print 'saving: ', dest
        out = file(dest, 'wb')
        out.write(bytes)
        out.close()

    def downloadError(self, error, url):
        print 'Error in deferred download (url=%s): %s' % (url, error)

    def uploaded(self, number):
        print 'books uploaded:', number

    def uploadError(self, error):
        print 'Error in deferred upload:', error


if __name__ == '__main__':
    xmlrpc_url = 'http://localhost:8080/RPC2'
    poll_method = 'dump_pending_isbns'
    callback = 'add_books'
    fetcher = Fetch(xmlrpc_url, poll_method, callback, amazon.Source())
    reactor.callLater(0, fetcher.poll)
    print 'reactor start'
    reactor.run()
    print 'reactor stop'

