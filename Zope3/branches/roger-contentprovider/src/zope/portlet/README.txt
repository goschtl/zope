========
Portlets
========

Portlets...


Getting Started
---------------


Portlet
~~~~~~~

  >>> import os, tempfile
  >>> temp_dir = tempfile.mkdtemp()

  >>> portletFileName = os.path.join(temp_dir, 'portlet.pt')
  >>> open(portletFileName, 'w').write('''
  ...         <div class="box">
  ...           <tal:block replace="portlet/title" />
  ...         </div>
  ... ''')

  >>> class POrtletBase(object):
  ...     def title(self):
  ...         return 'Portlet Title'


Portlet Managers
~~~~~~~~~~~~~~~~


Cleanup
-------

  >>> import shutil
  >>> shutil.rmtree(temp_dir)

