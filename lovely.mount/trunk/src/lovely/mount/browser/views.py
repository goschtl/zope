from zope.app.container.interfaces import IContained
from zope.formlib import form
from lovely.mount import interfaces
from zope.lifecycleevent import ObjectCreatedEvent
from lovely.mount.container import MountpointContainer
from  zope import event

class AddMountpoint(form.AddForm):
    form_fields=form.Fields(IContained['__name__'], interfaces.IMountpointContainer['dbName'])
    
    def create(self, data):
        name = data.get('__name__')
        self.request.form['add_input_name'] = name
        container = MountpointContainer(data.get('dbName'))
        container.__name__ = name
        return container

        
class EditMountpoint(form.EditForm):
    form_fields=form.Fields(interfaces.IMountpointContainer['dbName'])