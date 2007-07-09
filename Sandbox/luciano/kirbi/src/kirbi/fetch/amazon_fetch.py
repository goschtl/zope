#!/usr/bin/env python

import httplib2
from urllib import quote
from lxml import etree
from StringIO import StringIO

class AmazonECS(object):

    xml_namespace = """http://webservices.amazon.com/AWSECommerceService/2005-10-05"""
    base_url = """http://ecs.amazonaws.com/onca/xml"""

    def __init__(self, AWSAccessKeyId, AssociateTag=None):
        self.base_params = { 'Service':'AWSECommerceService',
                             'AWSAccessKeyId':AWSAccessKeyId, }
        if AssociateTag:
            self.base_params['AssociateTag'] = AssociateTag
        self.httpcli = httplib2.Http('.cache')
                    
    def buildURL(self, **kw):
        query = []
        kw.update(self.base_params)
        for key, val in kw.items():
            query.append('%s=%s' % (key,quote(val)))
        return self.base_url + '?' + '&'.join(query)
        
    def fetchTree(self, url):
        resp, content = self.httpcli.request(url, 'GET')
        self.tree = etree.parse(StringIO(content))
        return resp, content
        
    def buildQPath(path, ns):
        """build a path with fully qualified tags"""
        ns = '{%s}' % ns
        parts = path.split('/')
        return ns+('/'+ns).join(parts)

    def itemLookup(self,itemId):
        params = {'Operation':'ItemLookup', 'ItemId':itemId}
        url = self.buildURL(**params)
        return self.fetchTree(url)
        
    def findAll(self,path):
        pass


def fetch(asin):
    params['asin'] = asin
    params['op'] = 'ItemLookup'
    print asin
    resp, content = h.request(URL % params, 'GET')
    tree = etree.parse(StringIO(content))
    # the tree root is the toplevel html element
    items = tree.findall(qPath('Items/Item/ItemAttributes',NS))
    for item in items:
        print item.find(qPath('Title',NS)).text
        for author in item.findall(qPath('Author',NS)):
            print 'author: ', author.text
        for creator in item.findall(qPath('Creator',NS)):
            print 'creator: ', creator.text
            


if __name__=='__main__':
    from amazon_config import ACCESS_KEY_ID, ASSOCIATE_TAG
    
    ecs = AmazonECS(ACCESS_KEY_ID, ASSOCIATE_TAG)
    alice = '0393048470'
    gof = '0201633612'
    awpr = '0977616630'
    oss = '1565925823'
    print ecs.itemLookup(alice)
    
    
    
