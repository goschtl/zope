from ocql.engine.runnablequery import RunnableQuery
from ocql.engine.queryoptimizer import QueryOptimizer
from ocql.engine.rewriter import Rewriter
from ocql.engine.queryparser import QueryParser
from ocql.engine.algebraoptimizer import AlgebraOptimizer
from ocql.engine.algebracompiler import AlgebraCompiler
from ocql.tests.database import TestMetadata
from ocql.tests import algebra


class EngineFactory:
    def __init__(self, engine):
        self.engine = engine

    def get_query_optimizer(self):
        return QueryOptimizer(self.engine)

    def get_rewriter(self):
        return Rewriter(self.engine)

    def get_query_parser(self):
        return QueryParser(self.engine)

    def get_algebra_optimizer(self):
        return AlgebraOptimizer(self.engine)

    def get_metadata(self):
        return TestMetadata(self.engine)

    def get_algebra_compiler(self):
        return AlgebraCompiler(self.engine)

    def get_algebra(self):
        return algebra

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
        algebra = self._compile_query(query)
        code = self._compile_algebra(algebra)
        return RunnableQuery(self, algebra, code)

    def _compile_query(self, query):
        return self.rewriter.rewrite(
                   self.query_optimizer.optimize(
                       self.query_parser.parse(query)
                   )
               )

    def _compile_algebra(self, alg):
        return self.algebra_compiler.compile(
                   self.algebra_optimizer.optimize(alg)
               )
