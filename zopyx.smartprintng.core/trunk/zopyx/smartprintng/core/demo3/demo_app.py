##########################################################################
# zopyx.smartprintng.core - High-quality export of Zope content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, 2008, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################


import os

package_home = os.path.dirname(__file__)


def demo_convert():
    from zopyx.smartprintng.core.highlevel import convert

    flyer = os.path.join(package_home, 'flyer.html')
    filename = convert(context=None, html=flyer, converter='pdf-prince')
    return filename        

if __name__ == '__main__':

    filename = demo_convert()
    print filename
