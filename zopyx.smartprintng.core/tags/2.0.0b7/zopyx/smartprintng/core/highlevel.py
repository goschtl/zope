##########################################################################
# zopyx.smartprintng.core - High-quality export of Zope content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, 2008, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################


"""
Highlevel API for 3rd-party applications
"""

from resources import getResourcesFor
from renderer import Renderer
from zopyx.convert2.registry import availableConverters
from zopyx.convert2.convert import Converter


def convert(context,
            html='',
            resource_name=None,
            aggregator_name=None,
            styles=[],
            transformations=[],
            transformation_options={},
            template_options={},
            converter=None,
            destination_filename=None
            ):


    # Try to aggregate content for the current context object
    if aggregator_name:
        from aggregation import aggregateHTML
        aggregated_html = aggregateHTML(context, aggregator_name)
        if aggregated_html:
            html = aggregated_html

    # Lookup the Resource by name
    resource = getResourcesFor(context, resource_name)

    if not converter in resource.for_converters:
        raise ValueError('Converter "%s" is not supported for the resource" %s"' % 
                         (converter, resource_name))

    if converter not in availableConverters():
        raise ValueError('Converter "%s" is not available (%s)' % 
                         (converter, availableConverters()))

    # Render the contents to a full HTML file
    renderer = Renderer(context)
    renderer.render(html=html,
                    resource=resource,
                    styles=styles,
                    transformations=transformations,
                    transformation_options=transformation_options,
                    template_options=template_options)

    # save in-memory HTML to the filesystem
    output_filename = renderer.save()

    # now runn the external converter machinery
    c = Converter(output_filename)
    fn = c.convert(converter, output_filename=destination_filename)
    return fn
