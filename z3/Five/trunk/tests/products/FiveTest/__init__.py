from Products.Five import zcml
import Products

def initialize(context):
    zcml.process('configure.zcml', package=Products.FiveTest)

