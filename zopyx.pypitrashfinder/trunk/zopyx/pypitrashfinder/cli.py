import sys
from xmlrpclib import Server

def main():

    prefix = ''
    if len(sys.argv) > 1:
        prefix = sys.argv[1]

    server = Server('http://pypi.python.org/pypi')
    packages = server.list_packages()
    if prefix:
        packages = [p for p in packages if p.startswith(prefix)]

    num_packages = len(packages)

    for i, package in enumerate(packages):
        print 'Processing %r (%d/%d)' % (package, i+1, num_packages)

        versions = server.package_releases(package)
        versions.sort()
        for version in versions:
            print '  ', version
            urls = server.release_urls(package, version)

            import pdb; pdb.set_trace() 

            # PyPI hosted packages
            if urls:
                for url in urls:
                    print '    ', url['url']

            # externally hosted packages
            else:
                metadata = server.release_data(package, version)
                download_url = metadata['download_url']
                if download_url == 'UNKNOWN':
                    print 'CRAP: %s==%s - no release files, no valid download_url' % (package, version)




if __name__ == '__main__':
    main()
