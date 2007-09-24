class AlgebraCompiler:
    """
    Actual compilation of the Algebra to Python is done
    in each Algebra class/object at the moment
    """
    def __init__(self, engine):
        self.engine = engine
    
    def get_algebra(self):
        pass
    
    def compile(self, alg):
        #print alg
        code = alg.compile()
        #print code
        return compile(code,'<string>','eval')