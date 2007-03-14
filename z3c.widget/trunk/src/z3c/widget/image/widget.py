from zope.app.form.browser.widget import SimpleInputWidget
from zope.app.file.image import Image
from zope.lifecycleevent import ObjectCreatedEvent, ObjectModifiedEvent
import zope.event

template = u"""
   <div class="z3cImageWidget">
     Image Widget
     <input type="file" name="%(id)s" id="%(id)s" />
     <input type="checkbox" name="%(id)s.delete" value="true" /> delete image
   </div>
"""

class ImageWidget(SimpleInputWidget):
    pass

    def __call__(self):
        return template % {
            'id' : self.name
            }

    def _getFormInput(self):
        filedata = self.request.get(self.name)
        delete = self.request.has_key(self.name+'.delete')
        if delete:
            return None
        else:
            if not filedata:
                return self.context.get(self.context.context)
            else:
                fileObj = Image(filedata)
                zope.event.notify(ObjectCreatedEvent(fileObj))
                return fileObj
        
    def _toFieldValue(self, input):
        return input

