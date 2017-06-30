# -*- coding: utf-8 -*-

from . import Markovator

if __name__ == '__main__':
    import argparse, sys, codecs 

    def open_utf8(fn):
        if sys.version_info >= (3, 0, 0):
            return open(fn)
        else:
            return codecs.open(fn, encoding='utf-8')

    parser = argparse.ArgumentParser()
    parser.add_argument('textfile',
            type=str,
            help='File containing one input "sentence" per line')
    parser.add_argument('num',
            type=int,
            nargs='?',
            default=1,
            help='Number of sentences to generate')
    args = parser.parse_args()

    sentences = []
    with open_utf8(args.textfile) as fp:
        sentences = fp.readlines()

    m = Markovator((s.strip().split() for s in sentences))
    for i in range(args.num):
        print(u' '.join(m.generate()))

