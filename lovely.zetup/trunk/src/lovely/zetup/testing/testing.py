
app = {
    'logging': 'logging.cfg',
    'zcml': 'ftesting.zcml',
    'features':['devmode'],
    }

testsite = {
    'factory': 'zope.app.content.Folder',
    'settings':{'testing.option1': 1},
    'configurators':
    {'testconfigurator.one':
     {'someunicode':u'noreply@example.com',
      'alist':['server1:11211', 'server2:11211']},
     'testconfigurator.two':
     {'astring':'Value of Name',
      'afloat':1.0}
     },
    }

sites = {
    u'testsite':testsite,
    u'secondsite':testsite,
    }
