from Products.Five import zcml
import Products
import simplecontent

def initialize(context):
    zcml.process('configure.zcml', package=Products.FiveTest)

    context.registerClass(
        simplecontent.SimpleContent,
        constructors = (simplecontent.manage_addSimpleContentForm,
                        simplecontent.manage_addSimpleContent),
        )
