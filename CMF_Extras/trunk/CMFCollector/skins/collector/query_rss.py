##Script (Python) "query_rss"
##Title: Return a given query as RSS
##parameters=REQUEST

REQUEST.RESPONSE.setHeader('Content-Type', 'application/rss+xml')

kw = REQUEST.form

options = {}

options['collector'] = {'url': context.absolute_url(),
                        'title': context.Title(),
                        'description': context.Description(),
                        'base': context.ZopeTime().HTML4(),
                        'frequency': 1,
                        'period': 'minute',
                       }


query = kw.copy()
query['portal_type'] = 'Collector Issue'

if 'sort_on' in query:
    del query['sort_on']

catalog = context.get_internal_catalog()
found = catalog.search(query, 'modified', True)

items = []
for item in found:
    items.append({'url': item.getURL(),
                  'title': '%s [%0d]' % (item.Title, item.action_number),
                  'description': item.Description,
                  'subjects': ('status:%s' % item.status,
                               'importance:%s' % item.importance,
                               'topic:%s' % item.topic,
                               'classification:%s' % item.classification,
                              ),
                  'creators': (item.submitter_id,),
                  'contributors': item.assigned_to,
                  'date': item.modified.HTML4(),
                 })

options['issues'] = tuple(items)

#options = toUnicode( options, ptool.getProperty('default_charset', None) )
return context.issues_as_rss(**options)
