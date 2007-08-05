#!/usr/bin/env python
# encoding: utf-8

from lxml import etree
from twisted.internet import reactor
from twisted.web import xmlrpc, client

from urllib import quote
from time import sleep
import sys
from StringIO import StringIO

"""
Structure of the AmazonECS XML response:

ItemLookupResponse
    OperationRequest
        (...)
    Items
        Request
            IsValid
            ItemLookupRequest
                ItemId
                ResponseGroup
            (Errors)
                (Error)
                    (Code)
                    (Message)
        (Item)
            (ItemAttributes)
                (Author)
                (Creator Role=...)

Notes:
- Errors element occurs when ISBN is non-existent;
        in that case, Code contains the string "AWS.InvalidParameterValue"
- Author element is not always present
- Author element may be duplicated with the same content,
        except for whitespace; for example: ISBN=0141000511
"""

FIELD_MAP = [
    # Book schema -> Amazon ECS element
    ('title', 'Title'),
    ('isbn13', 'EAN'),
    ('edition', 'Edition'),
    ('publisher', 'Publisher'),
    ('issued', 'PublicationDate'),
    ('subject', 'DeweyDecimalNumber'),
    ]

CREATOR_TAGS = ['Author', 'Creator']

AMAZON_CODE_NO_MATCH = 'AWS.ECommerceService.NoExactMatches'

# if True, processed XML files will be saved
KEEP_FILES = True
# directory where XML files will be saved (include trailing slash)
SAVE_DIR = 'amazon_xml/'

ITEMS_PER_REQUEST = 3  # maximum from Amazon is 10


def test_parse(xml):
    xml = file(sys.argv[1])
    dic = parse(xml)
    pprint(dic)

class AmazonECS(object):

    base_url = """http://ecs.amazonaws.com/onca/xml"""

    def __init__(self, AWSAccessKeyId, AssociateTag=None):
        self.base_params = { 'Service':'AWSECommerceService',
                             'AWSAccessKeyId':AWSAccessKeyId, }
        if AssociateTag:
            self.base_params['AssociateTag'] = AssociateTag
        self.xml = ''
        self.http_response = {}

    def buildURL(self, **kw):
        query = []
        kw.update(self.base_params)
        for key, val in kw.items():
            query.append('%s=%s' % (key,quote(val)))
        return self.base_url + '?' + '&'.join(query)

    def itemLookup(self,itemId,response='ItemAttributes'):
        params = {  'Operation':'ItemLookup',
                    'ItemId':itemId,
                    'ResponseGroup':response
                 }
        return self.buildURL(**params)

    def itemSearch(self,query,response='ItemAttributes'):
        params = {  'Operation':'ItemSearch',
                    'SearchIndex':'Books',
                    'Power':query,
                    'ResponseGroup':response
                 }
        return self.buildURL(**params)
    
    def isbnSearch(self, isbns):
        query = 'isbn:' + ' or '.join(isbns)
        return self.itemSearch(query)

    def nsPath(self, path):
        parts = path.split('/')
        return '/'.join([self.ns+part for part in parts])
    
    def parse(self):
        xml = StringIO(self.xml)
        tree = etree.parse(xml)
        root = tree.getroot()
        # get the XML namespace from the root tag
        self.ns = root.tag.split('}')[0] + '}'
        request = root.find(self.nsPath('Items/Request'))
        error_code = request.findtext(self.nsPath('Errors/Error/Code'))
        if error_code is None:
            book_list = []
            for item in root.findall(self.nsPath('Items/Item/ItemAttributes')):
                book_dic = {}
                for field, tag in FIELD_MAP:
                    elem = item.find(self.ns+tag)
                    if elem is not None:
                        book_dic[field] = elem.text
                creators = []
                for tag in CREATOR_TAGS:
                    for elem in item.findall(self.ns+tag):
                        if elem is None: continue
                        role = elem.attrib.get('Role')
                        if role:
                            creator = '%s (%s)' % (elem.text, role)
                        else:
                            creator = elem.text
                        creators.append(creator)
                if creators:
                    book_dic['creators'] = creators
                book_list.append(book_dic)
            return book_list
    
        elif error_code == AMAZON_CODE_NO_MATCH:
            return []
        else:
            raise EnvironmentError, error_code
        
def getPending(pac):
    return pac.callRemote('list_pending_isbns').addCallback(gotPending)

def gotPending(isbns):
    print 'get: ', ' '.join(isbns)
    i = 0
    if isbns:
        # fetch at most 10 isbns per request, and one request per second
        for i, start in enumerate(range(0,len(isbns),ITEMS_PER_REQUEST)):
            end = start + ITEMS_PER_REQUEST
            reactor.callLater(i, getAmazonXml, isbns[start:end])
    reactor.callLater(i+1, getPending, pac)

def getAmazonXml(isbns):
    print 'fetch:', ' '.join(isbns)


    
def gotAmazonXml(xml):
    
    pac.callRemote('del_pending_isbns',isbns).addCallback(deletedPending)
    if KEEP_FILES:
        name = '_'.join(isbns)+'.xml'
        out = file(SAVE_DIR+name,'w')
        out.write(response.replace('><','>\n<'))
        out.close()
    return response

def deletedPending(n):
    print 'deleted:', n


if __name__ == '__main__':
    from amazon_config import ACCESS_KEY_ID, ASSOCIATE_TAG
    
    pac = xmlrpc.Proxy('http://localhost:8080/RPC2')


    reactor.callLater(1, checkPending, pac)
    print 'reactor start'
    reactor.run()
    print 'reactor stop'
