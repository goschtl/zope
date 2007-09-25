from ocql.engine.runnablequery import RunnableQuery

class EngineFactory:
    def __init__(self, engine):
        self.engine = engine
        
    def get_query_optimizer(self):
        from ocql.engine.queryoptimizer import QueryOptimizer
        return QueryOptimizer(self.engine)
    
    def get_rewriter(self):
        from ocql.engine.rewriter import Rewriter
        return Rewriter(self.engine)
    
    def get_query_parser(self):
        from ocql.engine.queryparser import QueryParser
        return QueryParser(self.engine)

    def get_algebra_optimizer(self):
        from ocql.engine.algebraoptimizer import AlgebraOptimizer
        return AlgebraOptimizer(self.engine)
    
    def get_metadata(self):
        from testdb import TestMetadata
        return TestMetadata(self.engine)
        
    def get_algebra_compiler(self):
        from ocql.engine.algebracompiler import AlgebraCompiler
        return AlgebraCompiler(self.engine)
    
    def get_algebra(self):
        import testalgebra
        return testalgebra
    
class OCQLEngine:
    def __init__(self):
        factory = EngineFactory(self)
        
        self.metadata = factory.get_metadata()
        self.algebra_compiler = factory.get_algebra_compiler() 
        self.algebra_optimizer = factory.get_algebra_optimizer()
        self.query_parser = factory.get_query_parser() 
        self.query_optimizer = factory.get_query_optimizer()
        self.rewriter = factory.get_rewriter()
        
        self.algebra = factory.get_algebra()
    
    def compile(self, query):
        return RunnableQuery(self, self._compile_query(query))

    def _compile_query(self, query):
        return self.rewriter.rewrite(
                   self.query_optimizer.optimize(
                       self.query_parser.parse(query)
                   )
               )

    def compile_algebra(self, alg):
        return self.algebra_compiler.compile(
                   self.algebra_optimizer.optimize(alg)
               )
