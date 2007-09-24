class AlgebraCompiler:
    """
    Common compiler methods
    """
    def __init__(self, engine):
        self.engine = engine
    
    def get_algebra(self):
        pass
    
    def compile(self, alg):
        print alg
        #from pub.dbgpclient import brk; brk()

        code = alg.compile()
        print code
        return compile(code,'','eval')