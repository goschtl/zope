from zope import interface
import re

# mimeTypeMatch holds regular expression for matching mime-types
MTM = 'mimeTypesMatch'
# mimeType holds the preferred mime type to be returned for this
# interface
MT = "mimeType"

class ITypedFile(interface.Interface):
    """A Type of a file"""

class IBinaryFile(ITypedFile):
    """Binary file"""
IBinaryFile.setTaggedValue(MTM,re.compile('application/octet-stream'))
IBinaryFile.setTaggedValue(MT,'application/octet-stream')

class IZIPFile(IBinaryFile):
    """Zip file"""
IZIPFile.setTaggedValue(MTM,re.compile('application/x-zip'))
IZIPFile.setTaggedValue(MT,'application/x-zip')

class ITARFile(IBinaryFile):
    """Binary file"""
ITARFile.setTaggedValue(MTM,re.compile('application/x-tar'))
ITARFile.setTaggedValue(MT,'application/x-tar')

class IBZIP2File(IBinaryFile):
    """BZIP2  file"""
IBZIP2File.setTaggedValue(MTM,re.compile('application/x-bzip2'))
IBZIP2File.setTaggedValue(MT,'application/x-bzip2')

class IGZIPFile(IBinaryFile):
    """Binary file"""
IGZIPFile.setTaggedValue(MTM,re.compile('application/x-gzip'))
IGZIPFile.setTaggedValue(MT,'application/x-gzip')

class ITextFile(ITypedFile):
    """text files"""
ITextFile.setTaggedValue(MTM,re.compile('^text/.+$'))
ITextFile.setTaggedValue(MT,'text/plain')

class IImageFile(ITypedFile):
    """image files"""
IImageFile.setTaggedValue(MTM,re.compile('^image/.+$'))

class IPDFFile(IBinaryFile):
    """pdf files"""
IPDFFile.setTaggedValue(MTM,re.compile('application/pdf'))
IPDFFile.setTaggedValue(MT,'application/pdf')

class IJPGFile(IImageFile, IBinaryFile):
    """jpeg file"""
IJPGFile.setTaggedValue(MTM,re.compile('image/jpe?g'))
IJPGFile.setTaggedValue(MT,'image/jpeg')

class IPNGFile(IImageFile, IBinaryFile):
    """png file"""
IPNGFile.setTaggedValue(MTM,re.compile('image/png'))
IPNGFile.setTaggedValue(MT,'image/png')

class IGIFFile(IImageFile, IBinaryFile):
    """gif file"""
IGIFFile.setTaggedValue(MTM,re.compile('image/gif'))
IGIFFile.setTaggedValue(MT,'image/gif')

class IVideoFile(IBinaryFile):
    """video file"""
IVideoFile.setTaggedValue(MTM,re.compile('^video/.+$'))

class IQuickTimeFile(IVideoFile):
    """Quicktime Video File Format"""
IQuickTimeFile.setTaggedValue(MTM,re.compile('video/quicktime'))
IQuickTimeFile.setTaggedValue(MT,'video/quicktime')

class IAVIFile(IVideoFile):
    """Quicktime Video File Format"""
IAVIFile.setTaggedValue(MTM,re.compile('video/x-msvideo'))
IAVIFile.setTaggedValue(MT,'video/x-msvideo')

class IMPEGFile(IVideoFile):
    """MPEG Video File Format"""
IMPEGFile.setTaggedValue(MTM,re.compile('video/mpe?g'))
IMPEGFile.setTaggedValue(MT,'video/mpeg')

class IMP4File(IQuickTimeFile):
    """IMP4File IPod Video File Format"""
IMP4File.setTaggedValue(MTM,re.compile('video/mp4'))
IMP4File.setTaggedValue(MT,'video/mp4')

class IFLVFile(IVideoFile):
    """Macromedia Flash FLV Video File Format"""
IFLVFile.setTaggedValue(MTM,re.compile('video/x-flv'))
IFLVFile.setTaggedValue(MT,'video/x-flv')

class IASFFile(IVideoFile):
    """Windows Media File Format"""
IASFFile.setTaggedValue(MTM,re.compile('video/x-ms-asf'))
IASFFile.setTaggedValue(MT,'video/x-ms-asf')

class IAudioFile(ITypedFile):
    """audio file"""
IAudioFile.setTaggedValue(MTM,re.compile('^audio/.+$'))

class IAudioMPEGFile(IAudioFile):
    """audio file"""
IAudioMPEGFile.setTaggedValue(MTM,re.compile('audio/mpeg'))
IAudioMPEGFile.setTaggedValue(MT,'audio/mpeg')

class IHTMLFile(ITextFile):
    """HTML file"""
IHTMLFile.setTaggedValue(MTM,re.compile('text/html'))
IHTMLFile.setTaggedValue(MT,'text/html')

class IXMLFile(ITextFile):
    """XML File"""
IXMLFile.setTaggedValue(MTM,re.compile('text/xml'))
IXMLFile.setTaggedValue(MT,'text/xml')
