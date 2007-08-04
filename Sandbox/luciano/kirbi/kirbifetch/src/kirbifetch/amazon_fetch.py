#!/usr/bin/env python
# encoding: utf-8

try:
    from lxml import etree
except ImportError:
    try:
        import cElementTree as etree
    except ImportError:
        try:
            import elementtree.ElementTree as etree
        except ImportError:
            raise ImportError, "Failed to import ElementTree from any known place"

import httplib2
from urllib import quote
from StringIO import StringIO
from time import sleep

# XXX: figure out the best place to put the isbn.py module
# because it is used by kirbi and kirbifetch
from isbn import convertISBN13toISBN10

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
    ]

CREATOR_TAGS = ['Author', 'Creator']

AMAZON_INVALID_PARAM = 'AWS.InvalidParameterValue'


def nsPath(ns, path):
    parts = path.split('/')
    return '/'.join([ns+part for part in parts])

def parse(xml):
    tree = etree.parse(xml)
    raiz = tree.getroot()
    # get the XML namespace from the root tag
    ns = raiz.tag.split('}')[0] + '}'
    request = raiz.find(nsPath(ns,'Items/Request'))
    error_code = request.findtext(nsPath(ns,'Errors/Error/Code'))
    if error_code is None:
        items = raiz.findall(nsPath(ns,'Items/Item'))
        #TODO: treat multiple Item elements in Items
        item = items[0].find(ns+'ItemAttributes')
        book_dic = {}
        for field, tag in FIELD_MAP:
            elem = item.find(ns+tag)
            if elem is not None:
                book_dic[field] = elem.text
        creators = []
        for tag in CREATOR_TAGS:
            for elem in item.findall(ns+tag):
                if elem is None: continue
                role = elem.attrib.get('Role')
                if role:
                    creator = '%s (%s)' % (elem.text, role)
                else:
                    creator = elem.text
                creators.append(creator)
        if creators:
            book_dic['creators'] = creators
        return book_dic

    elif error_code == AMAZON_INVALID_PARAM:
        return None
    else:
        raise LookupError, error_code

class AmazonECS(object):

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
        return resp, content

    def itemLookup(self,itemId,response='ItemAttributes'):
        params = {  'Operation':'ItemLookup',
                    'ItemId':itemId,
                    'ResponseGroup':response
                 }
        url = self.buildURL(**params)
        return self.getFile(url)[1]

if __name__ == '__main__':
    import sys
    from pprint import pprint
    xml = file(sys.argv[1])
    dic = parse(xml)
    pprint(dic)

    from amazon_config import ACCESS_KEY_ID, ASSOCIATE_TAG

    ecs = AmazonECS(ACCESS_KEY_ID, ASSOCIATE_TAG)
    alice = '0393048470'
    gof = '0201633612'
    awpr = '0977616630'
    oss = '1565925823'
    dup = '0141000511'
    erro = '1231231239'
    print ecs.itemLookup(erro)

"""
NOTE: 0333647289 is a valid ISBN which generates a AWS.InvalidParameterValue
    from Amazon.com with message: "0333647289 is not a valid value for ItemId"
    The book is Virtual History: Alternatives and Counterfactuals
    by Niall Ferguson (Editor)
    Amazon.com does not have it but Amazon.co.uk does and
    Google query "isbn 0333647289" also found it here:
    http://www.alibris.com/search/search.cfm?qwork=7055972
"""
