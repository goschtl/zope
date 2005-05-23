# BBB: for Zope 2.7
class BBBTransaction:

    def begin(self):
        get_transaction().begin()

    def commit(self, sub=False):
        get_transaction().commit(sub)

    def abort(self, sub=False):
        get_transaction().abort(sub)

transaction = BBBTransaction()
