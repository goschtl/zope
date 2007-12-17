;-*-Doctest-*-
=============
z3c.gibberish
=============

Generate CSV files containing random words from a dictionary

Get the script from the buildout::

    >>> import os
    >>> gibberish = os.path.join(
    ...     reduce(lambda path, _: os.path.dirname(path),
    ...            range(3), __file__), 'bin', 'gibberish')

Print the help::

    >>> from zc.buildout.testing import system
    >>> print system(gibberish+' --help'),
    usage: gibberish [options] LINES COLUMN [COLUMN ...]
    <BLANKLINE>
    Generate lines of CSV consisting of random words from a
    dictionary.  The number of lines of CSV must be specified either
    as a single integer to specify a fixed number of lines or two
    integers separated by a dash to specify that a random number of
    lines between the two integers should be used.  The columns are
    specified in the same manner where the numbers represent the
    number of words in that column for a given line.
    <BLANKLINE>
    options:
      -h, --help            show this help message and exit
      -w WORDS, --words=WORDS
                            File containing the words to be chosen
                            from [default: /usr/share/dict/words]

Make a simple file with one line and one column containing one word::

    >>> import StringIO, csv
    >>> result = list(csv.reader(StringIO.StringIO(
    ...     system(gibberish+' 1 1'))))
    >>> len(result)
    1
    >>> len(result[0])
    1
    >>> len(result[0][0].split())
    1

Make sure that the newline is stripped::

    >>> result[0][0][-1] != '\n'
    True

With two words in the column::

    >>> import StringIO, csv
    >>> result = list(csv.reader(StringIO.StringIO(
    ...     system(gibberish+' 1 2'))))
    >>> len(result)
    1
    >>> len(result[0])
    1
    >>> len(result[0][0].split())
    2

With a random number of words in the column::

    >>> import StringIO, csv
    >>> result = list(csv.reader(StringIO.StringIO(
    ...     system(gibberish+' 1 1-10'))))
    >>> len(result)
    1
    >>> len(result[0])
    1
    >>> 1 <= len(result[0][0].split()) <= 10
    True

With 10 lines::

    >>> import StringIO, csv
    >>> result = list(csv.reader(StringIO.StringIO(
    ...     system(gibberish+' 10 2'))))
    >>> len(result)
    10
    >>> len(result[0])
    1
    >>> len(result[0][0].split())
    2

With a random number of lines::

    >>> import StringIO, csv
    >>> result = list(csv.reader(StringIO.StringIO(
    ...     system(gibberish+' 1-10 2'))))
    >>> 1 <= len(result) <= 10
    True
    >>> len(result[0])
    1
    >>> len(result[0][0].split())
    2

With two columns::

    >>> import StringIO, csv
    >>> result = list(csv.reader(StringIO.StringIO(
    ...     system(gibberish+' 1 2 3'))))
    >>> len(result)
    1
    >>> len(result[0])
    2
    >>> len(result[0][0].split())
    2
    >>> len(result[0][1].split())
    3
