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


