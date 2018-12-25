# -*- coding: utf-8 -*-

import sys, random
from collections import defaultdict, deque

CACHE_DELIM = '\v'
TERMINATOR = '\f'

class Markovator:
    """
    Data is a list (corpus) of lists (sentences) of strings (words)
      example = [
          [ "Lorem", "ipsum", "dolor", "sit", "amet.", ],
          [ "Consectetur", "adipisicing", "elit.", ],
          [ "Sed", "do", "eiusmod", "tempor,", "incididunt", "labore.", ],
      ]
    
    Filter is a function `f(word)` that returns True if the word is okay to
    include in the corpus, and False if it should be excluded.
      example = lambda word: not word.upper().startswith('L')

    Order determines the length of the trailing chain during generation.

    Verbose gives you debug output to console. Higher values give more output.
    """

    def __init__(self, data, filter=None, order=2, verbose=0):
        self.cache = defaultdict(lambda: defaultdict(int))
        self.corpus = self._cleanse_corpus(data)
        self.order = order
        self.verbose = verbose

        if len(self.corpus) == 0:
            return

        for sentence in self.corpus:
            tokens = deque([TERMINATOR,]*self.order, self.order)
            for word in sentence:
                if filter and not filter(word):
                    if self.verbose:
                        sys.stderr.write('Filter rejected input word [%s]\n'%word)
                    continue
                self.cache[tuple(tokens)][word] += 1
                tokens.append(word)
            self.cache[tuple(tokens)][TERMINATOR] += 1

    def _cleanse_corpus(self, data):
        """
        Corpus data *should* be a 2-D array, but if the user passed in either
        a single string or a 1D list of strings, try to split things up.
        """
        if not data:
            return []
        tt = str
        if sys.version_info < (3, 0):
            tt = basestring
        if isinstance(data, tt):
            return [a.split() for a in data.split('\n')]
        else:
            rv = []
            for a in data:
                if isinstance(a, tt):
                    rv.append(a.split())
                else:
                    rv.append(a)
            return rv

    def _pick(self, t):
        opts = self.cache[t]
        tot = sum(opts.values())
        pik = random.uniform(0, tot)
        top = 0
        for o,c in opts.items():
            top += c
            if top >= pik:
                return o

        # shouldn't get here
        sys.stderr.write('ERROR: couldn\'t pick from [%s][%s]: [%d] [%d] [%d]\n'%(t, opts, tot, pik, top))
        return random.choice(opts.keys()) # panic pick

    def _chain(self):
        tokens = deque([TERMINATOR,]*self.order, self.order)
        rv = []
        nextword = self._pick(tuple(tokens))
        while nextword != TERMINATOR:
            rv.append(nextword)
            tokens.append(nextword)
            nextword = self._pick(tuple(tokens))
        return rv

    def generate(self, filter=None, retries=20):
        """
        Generate a sequence.

        Returns a list of words, which can be `join()`ed for a textual
        sentence.

        Filter is a function f(sentence) that returns True if the given
        generated sequence should be kept, and False if we should reject it and
        try again. If no filter is specified, the default filter checks to see
        that we haven't exactly recreated an entry from the input corpus.

        Retries is the number of filter-failure retries that will be attempted
        before giving up. If the retry limit is exceeded, the last attempt wil
        be returned, even if it's bad.
        """
        if not self.cache:
            if self.verbose:
                sys.stderr.write('No data to generate from\n')
            return ''

        if not filter:
            filter = lambda s: s not in self.corpus

        rv = []
        faili = 0
        rv = self._chain()
        if retries > 0:
            while not filter(rv) and faili < retries:
                if self.verbose > 1:
                    sys.stderr.write('Filter rejected [%s] (%d)\n'%(' '.join(rv), faili))
                faili += 1
                rv = self._chain()
        if faili >= retries and self.verbose:
            sys.stderr.write('Too many retries [%s]\n'%(' '.join(rv)))
        return rv

