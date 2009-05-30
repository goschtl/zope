==================
Keyword Extraction
==================

This package implements text keyword extraction by making use of a simple
Parts-Of-Speech (POS) tagging algorithm.

http://bioie.ldc.upenn.edu/wiki/index.php/Part-of-Speech


The POS Tagger
--------------

POS Taggers use a lexicon to mark words with a tag. A list of available tags
can be found at:

http://bioie.ldc.upenn.edu/wiki/index.php/POS_tags

Since words can have multiple tags, the determination of the correct tag is
not always simple. This implementation, however, does not try to infer
linguistic use and simply chooses the first tag in the lexicon.

  >>> from topia.postag import tag
  >>> tagger = tag.Tagger()
  >>> tagger
  <Tagger for english>

To get the tagger ready for its work, we need to initialize it. In this
implementation the lexicon is loaded.

  >>> tagger.initialize()

Now we are ready to rock and roll.

Tokenizing
~~~~~~~~~~

The first step of tagging is to tokenize the text into terms.

  >>> tagger.tokenize('This is a simple example.')
  ['This', 'is', 'a', 'simple', 'example', '.']

While most tokenizers ignore punctuation, it is important for us to keep it,
since we need it later for the keyword extraction. Let's now look at some more
complex cases:

- Quoted Text

  >>> tagger.tokenize('This is a "simple" example.')
  ['This', 'is', 'a', '"', 'simple', '"', 'example', '.']

  >>> tagger.tokenize('"This is a simple example."')
  ['"', 'This', 'is', 'a', 'simple', 'example', '."']

- Non-letters within words.

  >>> tagger.tokenize('Parts-Of-Speech')
  ['Parts-Of-Speech']

  >>> tagger.tokenize('amazon.com')
  ['amazon.com']

  >>> tagger.tokenize('Go to amazon.com.')
  ['Go', 'to', 'amazon.com', '.']

- Various punctuation.

  >>> tagger.tokenize('Quick, go to amazon.com.')
  ['Quick', ',', 'go', 'to', 'amazon.com', '.']

  >>> tagger.tokenize('Live free; or die?')
  ['Live', 'free', ';', 'or', 'die', '?']

- Tolerance to incorrect punctuation.

  >>> tagger.tokenize('Hi , I am here.')
  ['Hi', ',', 'I', 'am', 'here', '.']

- Possessive structures.

  >>> tagger.tokenize("my parents' car")
  ['my', 'parents', "'", 'car']
  >>> tagger.tokenize("my father's car")
  ['my', 'father', "'s", 'car']

- Numbers.

  >>> tagger.tokenize("12.4")
  ['12.4']
  >>> tagger.tokenize("-12.4")
  ['-12.4']
  >>> tagger.tokenize("$12.40")
  ['$12.40']

- Dates.

  >>> tagger.tokenize("10/3/2009")
  ['10/3/2009']
  >>> tagger.tokenize("3.10.2009")
  ['3.10.2009']

Okay, that's it.


Tagging
-------

The next step is tagging. Tagging is done in two phases. During the first
phase terms are assigned a tag by looking at the lexicon and the normalized
form is set to the term itself. In the second phase, a set of rules is applied
to each tagged term and the tagging and normalization is tweaked.

  >>> tagger('This is a simple example.')
  [['This', 'DT', 'This'],
   ['is', 'VBZ', 'is'],
   ['a', 'DT', 'a'],
   ['simple', 'JJ', 'simple'],
   ['example', 'NN', 'example'],
   ['.', '.', '.']]

So wow, this determination was dead on. Let's try a plural form noun and see
what happens:

  >>> tagger('These are simple examples.')
  [['These', 'DT', 'These'],
   ['are', 'VBP', 'are'],
   ['simple', 'JJ', 'simple'],
   ['examples', 'NNS', 'example'],
   ['.', '.', '.']]

So far so good. Let's now test the phase 2 rules.


Rules
~~~~~

- Correct Default Noun Tag

    >>> tagger('Ikea')
    [['Ikea', 'NN', 'Ikea']]
    >>> tagger('Ikeas')
    [['Ikeas', 'NNS', 'Ikea']]

- Verify proper nouns at beginning of sentence.

    >>> tagger('. Police')
    [['.', '.', '.'], ['police', 'NN', 'police']]
    >>> tagger('Police')
    [['police', 'NN', 'police']]
    >>> tagger('. Stephan')
    [['.', '.', '.'], ['Stephan', 'NNP', 'Stephan']]

- Normalize Plural Forms

    >>> tagger('examples')
    [['examples', 'NNS', 'example']]
    >>> tagger('stresses')
    [['stresses', 'NNS', 'stress']]
    >>> tagger('cherries')
    [['cherries', 'NNS', 'cherry']]

  Some cases that do not work:

    >>> tagger('men')
    [['men', 'NNS', 'men']]
    >>> tagger('feet')
    [['feet', 'NNS', 'feet']]
