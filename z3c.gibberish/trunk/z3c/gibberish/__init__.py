import sys, os, string, optparse, csv
from random import randint
from itertools import islice

parser = optparse.OptionParser(
    usage="usage: %prog [options] LINES COLUMN [COLUMN ...]",
    description=(
        "Generate lines of CSV consisting of random words from a "
        "dictionary.  "

        "The number of lines of CSV must be specified either as a "
        "single integer to specify a fixed number of lines or two "
        "integers separated by a dash to specify that a random "
        "number of lines between the two integers should be used.  "
        
        "The columns are specified in the same manner where the "
        "numbers represent the number of words in that column for a "
        "given line."))
parser.add_option(
    "-w", "--words",
    default=os.path.join('/', 'usr', 'share', 'dict', 'words'),
    help=("File containing the words to be chosen from "
          "[default: %default]"))

def get_num(range):
    range = [int(i) for i in range.split('-')]
    if len(range) == 2:
        return randint(*range)
    else:
        num, = range
        return num

def random_words(words):
    words = file(words)
    length = 0
    for line in words:
        length += 1
    words.seek(0)

    seek = words.seek
    while True:
        yield islice(words, randint(0, length-1), None
                     ).next().strip()
        seek(0)

def main(args=sys.argv[1:], out=sys.stdout):
    options, args = parser.parse_args(args)
    lines = get_num(args[0])
    columns = args[1:]

    words = random_words(options.words)
    csv.writer(out).writerows(
        [' '.join(islice(words, get_num(column)))
         for column in columns]
        for _ in xrange(lines))
