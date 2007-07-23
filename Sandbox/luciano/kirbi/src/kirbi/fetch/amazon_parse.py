#!/usr/bin/env python

import httplib2
from urllib import quote
from lxml import etree
from StringIO import StringIO
from time import sleep

"""
NOTE: 0333647289 is a valid ISBN which generates a AWS.InvalidParameterValue
    from Amazon.com with message: "0333647289 is not a valid value for ItemId"
    The book is Virtual History: Alternatives and Counterfactuals
    by Niall Ferguson (Editor)
    Amazon.com does not have it but Amazon.co.uk does and
    Google query "isbn 0333647289" also found it here:
    http://www.alibris.com/search/search.cfm?qwork=7055972
"""

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
        
    def getFile(self, url):
        # Amazon.com ECS agreement imposes a limit of one request per second
        sleep(1)
        resp, content = self.httpcli.request(url, 'GET')
        self.tree = etree.parse(StringIO(content))
        return resp, content
        
    def buildQPath(path, ns):
        """build a path with fully qualified tags"""
        ns = '{%s}' % ns
        parts = path.split('/')
        return ns+('/'+ns).join(parts)

    def itemLookup(self,itemId,response='ItemAttributes'):
        params = {  'Operation':'ItemLookup', 
                    'ItemId':itemId,
                    'ResponseGroup':response
                 }
        url = self.buildURL(**params)
        return self.getFile(url)[1]
        
    def findAll(self,path):
        pass            


if __name__=='__main__':
    from amazon_config import ACCESS_KEY_ID, ASSOCIATE_TAG
    
    ecs = AmazonECS(ACCESS_KEY_ID, ASSOCIATE_TAG)
    alice = '0393048470'
    gof = '0201633612'
    awpr = '0977616630'
    oss = '1565925823'
    dup = '0141000511'
    print ecs.itemLookup(oss)
    
    
    
