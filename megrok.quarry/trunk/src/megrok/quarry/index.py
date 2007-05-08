from grok.index import IndexDefinition
from zc.catalog.catalogindex import ( SetIndex,
                                      ValueIndex,
                                      DateTimeValueIndex,
                                      DateTimeSetIndex )


class Set(IndexDefinition):
    index_class = SetIndex


class Value(IndexDefinition):
    index_class = ValueIndex


class DatetimeValue(IndexDefinition):

    @property
    def index_class(self):
        #import pdb; pdb.set_trace()
        return DateTimeValueIndex

class DatetimeSet(IndexDefinition):

    # DatetimeSet generates an error
    # when index_class is set directly
    # I set up this method for debugging
    # and as soon as I did it worked :)
    # YMMV
    
    @property
    def index_class(self):
        #import pdb; pdb.set_trace()
        return DateTimeSetIndex

