import constants

class Operation(tuple):
    """Represents an indexing operation."""

    op = None

    def __new__(cls, obj=None, attributes=None):
        inst = tuple.__new__(cls, (cls.op, obj, attributes))
        inst.obj = obj
        inst.attributes = attributes
        return inst

    def process(self, dispatcher):
        return NotImplemented("Should be implemented in subclass.")

class Add(Operation):
    op = constants.INDEX

    def process(self, dispatcher):
        dispatcher.index(self.obj, self.attributes)

class Modify(Operation):
    op = constants.REINDEX

    def process(self, dispatcher):
        dispatcher.reindex(self.obj, self.attributes)

class Delete(Operation):
    op = constants.UNINDEX

    def process(self, dispatcher):
        dispatcher.unindex(self.obj)
