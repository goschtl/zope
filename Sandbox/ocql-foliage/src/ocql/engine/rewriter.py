#
# Rewrites the Query Object to Algebra Object
#
# rewrite is moved to the Query object classes
# to their rewrite method
#


class Rewriter:
    def __init__(self, engine):
        self.engine = engine
    
    def rewrite(self, query):
        return query.rewrite(self.engine.algebra)