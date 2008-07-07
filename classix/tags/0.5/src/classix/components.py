from lxml import etree

class Element(etree.ElementBase):
    pass
    
class XMLParser(etree.XMLParser):
    def __init__(self, *args, **kw):
        super(XMLParser, self).__init__(*args, **kw)
        self.set_element_class_lookup(self._lookup)
