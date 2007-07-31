#!/usr/bin/env python
# encoding: utf-8

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

try:
    from lxml import etree
except ImportError:
    try:
        import cElementTree as etree
    except ImportError:
        try:
            import elementtree.ElementTree as etree
        except ImportError:
            print "Failed to import ElementTree from any known place"

FIELD_MAP = [
    # Book schema -> Amazon ECS element
    ('title', 'Title'),
    ('isbn13', 'EAN'),
    ('edition', 'Edition'),
    ('publisher', 'Publisher'),
    ('issued', 'PublicationDate'),
    ]

CREATOR_TAGS = ['Author', 'Creator']


AMAZON_INVALID_PARAM = 'AWS.InvalidParameterValueXX'


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

if __name__ == '__main__':
    import sys
    from pprint import pprint
    xml = file(sys.argv[1])
    dic = parse(xml)
    pprint(dic)
