import grok

class DoctestDeclaredInSubpkg(grok.testing.FunctionalDocTest):
    grok.testing.file('doctest_in_subpkg.txt')

