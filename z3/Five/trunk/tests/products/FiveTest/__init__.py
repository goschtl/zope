import Products
import simplecontent
import fancycontent

def initialize(context):

    context.registerClass(
        simplecontent.SimpleContent,
        constructors = (simplecontent.manage_addSimpleContentForm,
                        simplecontent.manage_addSimpleContent),
        )

    context.registerClass(
	fancycontent.FancyContent,
	constructors = (fancycontent.manage_addFancyContent,)
	)
