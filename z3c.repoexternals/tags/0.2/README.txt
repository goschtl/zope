=================
z3c.repoexternals
=================

Use the --help option for usage details::

  usage: repoexternals [options] url_or_path
  
  Recursively retrieves subversion directory listings from the url or
  path and matches directories against a previous set of svn:externals
  if provided then against regular expressions and generates
  qualifying svn:externals lines.  The defaults generate a set of
  svn:externals for all the trunks in a repository and keeps them up
  to date with the repository as new trunks are added when the
  previous externals are provided thereafter.
  
  options:
    -h, --help            show this help message and exit
    -v, --verbose         Output logging to stdandard error. Set twice
                          to log debugging mesages.
    -p FILE, --previous=FILE
                          If provided, only URLs in the repository not
                          included in the previous externals will be
                          included. If the filename is '-', use
                          standard input.  Valid svn:externals lines
                          beginning with one comment character, '#',
                          will also affect output.  This is useful,
                          for example, to prevent lengthy recursions
                          into directories that are known not to
                          contain any desired matches.  The file is
                          read completely and closed before anything
                          is output, so it is safe to append output to
                          the previous file:
                          "repoexternals -p EXTERNALS.txt http://svn.foo.org/repos/main >>EXTERNALS.txt".
    -i REGEXP, --include=REGEXP
                          Directory names matching this python regular
                          expression will be included in output and
                          will not be descended into.
                          [default: (?i)^((.*)/.+?|.*)/trunk$]
    -e REGEXP, --exclude=REGEXP
                          Directory names matching this python regular
                          expression will be excluded from output and
                          will not be descended into. Include
                          overrides exclude.  [default:
                          (?i)^.*/(branch(es)?|tags?|releases?|vendor|bundles?|sandbox|build|dist)$]
    -m TEMPLATE, --matched-template=TEMPLATE
                          The result of expanding previous file URL
                          matches with the include regular expression
                          through this template is added to the set of
                          previous URLs excluded from output and
                          descending.  The default will add the
                          parents of trunks to the set of previous
                          URLs excluded.  [default: \1]
    -t TEMPLATE, --parent-template=TEMPLATE
                          The result of expanding previous file URL
                          matches with the include regular expression
                          through this template is removed from the
                          set of matched previous URLs excluded from
                          output and descending. The default ensures
                          that directories containing trunks within a
                          directory that contains a trunk are not
                          excluded.  [default: \2]
    -d INT, --depth=INT   The maximum directory depth to descend to.
                          WARNING: large values can greatly increase
                          run time.  [default: 5]
    -s INT, --pool-size=INT
                          The number of concurrent svn clients.
                          WARNING: large values can DOS the
                          repository.  [default: 5]
