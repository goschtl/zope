class Rewriter:
    def __init__(self, engine):
        self.engine = engine
    
    def rewrite(self, query):
        return query.rewrite(self.engine.algebra)