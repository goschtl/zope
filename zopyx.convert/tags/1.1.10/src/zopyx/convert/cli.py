##########################################################################
# zopyx.convert - XSL-FO related functionalities
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import tempfile
from optparse import OptionParser
from convert import Converter
from config import supported_formats

from zopyx.convert import availableFormats

def convert(options, args):

    if options.test_mode:

        import pkg_resources
        print 'Entering testmode'

        for fn in ('test1.html', 'test2.html', 'test3.html'):
            tmpf = tempfile.mktemp() 
            open(tmpf + '.html', 'wb').write(pkg_resources.resource_string('zopyx.convert.tests.data', fn))

            for format in availableFormats():
                print '%s: %s.html -> %s.%s' % (format, tmpf, tmpf, format)
                C = Converter(tmpf + '.html', verbose=True)
                output_filename = C(format, output_filename=tmpf + '.' + format)

    elif options.show_converters:
        print 'Available converters: %s' % ','.join(availableFormats())

    else:

        for fn in args:
            C = Converter(fn, verbose=options.verbose)
            output_filename = C(options.format, output_filename=options.output_filename)
            print 'Generated file: %s' % output_filename
   

def main():

    parser = OptionParser()
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
                      default=False, help='verbose on')

    parser.add_option('-f', '--format', dest='format',
                      help='|'.join(supported_formats))

    parser.add_option('-l', '--list-converters', action='store_true', dest='show_converters',
                      default=False, help='show all available converters')

#    parser.add_option('-c', '--check-converters', action='store_true', dest='check_converters',
#                      default=False, help='check all available converters')

    parser.add_option('-o', '--output', dest='output_filename',
                      help='output filename')

    parser.add_option('-t', '--test', dest='test_mode', action='store_true',
                      help='test converters')
    (options, args) = parser.parse_args()
    convert(options, args)


if __name__ == '__main__':
    main()
