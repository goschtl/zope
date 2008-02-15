========================
Image Processing Adapter
========================

  >>> from z3c.image import testing
  >>> from z3c.image.proc.adapter import ProcessableImage
  >>> from z3c.image.proc.interfaces import IProcessableImage
  >>> image = testing.getTestImage('flower.jpg')
  >>> image.contentType
  'image/jpeg'

  >>> image.getImageSize()
  (103, 118)

In order to do some processing we have to register the adapter

  >>> from zope import component
  >>> component.provideAdapter(ProcessableImage)

  >>> pimg = IProcessableImage(image)

Let us rotate the image
  >>> pimg.rotate(90)

To get a processed image we call the process method

  >>> res = pimg.process()
  >>> res
  <z3c.image.image.VImage object at ...>

  >>> res.getImageSize()
  (118, 103)

The command queue stays when processed is called, but it is always
called on the same original image. To reset the command queue, use the
reset method. If no processing is done the original context is returned.

  >>> pimg.reset()
  >>> pimg.process() is image
  True

Resizing is also possible.

  >>> pimg.resize([20,30])
  >>> res = pimg.process()
  >>> res.getImageSize()
  (20, 30)

You can append another command to the processing. The commands are
processed in the order they have been aplied.

  >>> pimg.rotate(90)
  >>> res = pimg.process()
  >>> res.getImageSize()
  (30, 20)

Also another image can be pasted into the image.

Note: paste changes the original image

  >>> pimg.reset()
  >>> data = testing.readTestImage('locked.png')
  >>> from PIL import Image
  >>> from StringIO import StringIO
  >>> img = Image.open(StringIO(data))
  >>> pimg.paste(img, (0, 0), img)
  >>> res = pimg.process()

Also the PNG and GIF filetypes are supported.

  >>> image = testing.getTestImage('locked.png')
  >>> image.contentType
  'image/png'
  >>> image.getImageSize()
  (128, 128)
  >>> pimg = IProcessableImage(image)
  >>> pimg.resize([80,80])
  >>> res = pimg.process()
  >>> res.getImageSize()
  (80, 80)

  >>> image = testing.getTestImage('hiring.gif')
  >>> image.contentType
  'image/gif'
  >>> image.getImageSize()
  (199, 183)
  >>> pimg = IProcessableImage(image)
  >>> pimg.resize([80,80])
  >>> res = pimg.process()
  >>> res.getImageSize()
  (80, 80)

Cache Handling
==============

The adapter uses a RamCache instance to cache results.

  >>> from z3c.image.proc.adapter import imgCache

We have to take private methods to get to the objects, because the
getStatistics implementation does not allow to get the size of
unpickleable objects.

  >>> sorted(imgCache._getStorage()._data.keys())
  [<zope.app.file.image.Image object at ...>,
   <zope.app.file.image.Image object at ...>,
   <zope.app.file.image.Image object at ...>]

To demonstrate caching we now invalidate first and process another.

  >>> imgCache.invalidateAll()
  >>> sorted(imgCache._getStorage()._data.keys())
  []
  >>> image = testing.getTestImage('hiring.gif')
  >>> pimg = IProcessableImage(image)
  >>> pimg.rotate(90)
  >>> res = pimg.process()
  >>> res.getImageSize()
  (183, 199)

Now let us change the data of the image.

  >>> import os
  >>> path = os.path.join(testing.dataDir,'flower.jpg')
  >>> image.data = file(path,'rb').read()
  >>> image.getImageSize()
  (103, 118)

And now we do the same processing again

  >>> pimg = IProcessableImage(image)
  >>> pimg.rotate(90)
  >>> res = pimg.process()
  >>> res.getImageSize()
  (183, 199)

The cache is invalidated when a modified event is fired. To
demonstrate this we need to set up event handling

  >>> from zope.component import eventtesting
  >>> eventtesting.setUp()
  >>> from zope.lifecycleevent import ObjectModifiedEvent

When we now fire the event, the result changes.

  >>> from zope.event import notify
  >>> notify(ObjectModifiedEvent(image))
  >>> pimg = IProcessableImage(image)
  >>> pimg.rotate(90)
  >>> res = pimg.process()
  >>> res.getImageSize()
  (118, 103)


