##Script (Python) "meta_rdf"
##Title: Return collector metadata as RDF
##parameters=REQUEST

REQUEST.RESPONSE.setHeader('Content-Type', 'application/xml')
catalog = context.get_internal_catalog()

options = {'collector_url': context.absolute_url(),
           'status': catalog.uniqueValuesFor('status'),
           'supporters': context.supporters,
           'topic': context.topics,
           'classification': context.classifications,
           'importance': context.importances,
          }

return context.meta_rdf_template(**options)
