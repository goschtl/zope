import Products
import simplecontent

def initialize(context):

    context.registerClass(
        simplecontent.SimpleContent,
        constructors = (simplecontent.manage_addSimpleContentForm,
                        simplecontent.manage_addSimpleContent),
        )
