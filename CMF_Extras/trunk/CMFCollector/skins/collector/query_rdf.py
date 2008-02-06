##Script (Python) "query_rdf"
##Title: Return a given query as RDF
##parameters=REQUEST

REQUEST.RESPONSE.setHeader('Content-Type', 'application/xml')

kw = REQUEST.form

options = {}

query = kw.copy()
query['portal_type'] = 'Collector Issue'

if 'sort_on' not in query:
    query['sort_on'] = 'getId'

if 'supporters' in query:
    query['assigned_to'] = query['supporters']
    del query['supporters']

catalog = context.get_internal_catalog()
found = catalog.search(query_request=query, sort_index='modified', reverse=True)

items = []
for item in found:
    info = {'url': item.getURL(),
            # dc namespace
            'title': item.Title,
            'description': item.Description,
            'subjects': (),
            'creators': (item.submitter_id,),
            'contributors': item.assigned_to,
            'date': item.modified.HTML4(),
            # cmfcollector namespace
            'number': int(item.getId),
            'responses': item.action_number,
            'status': item.status,
            'importance': item.importance,
            'topic': item.topic,
            'classification': item.classification,
           }
    items.append(info)

options['issues'] = tuple(items)

options['supporters'] = catalog.supporters
options['status'] = catalog.uniqueValuesFor('status')
options['topic'] = catalog.topics
options['classification'] = catalog.classifications
options['importance'] = catalog.importances

return context.issues_as_rdf(**options)
