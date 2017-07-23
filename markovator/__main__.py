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
    parser.add_argument('-o', '--order',
            dest='order',
            action='store',
            type=int,
            default=3,
            help='Chaining order')
    parser.add_argument('-c', '--by-char',
            dest='bychar',
            action='store_true',
            help='Split by character rather than by word')
    args = parser.parse_args()

    sentences = []
    with open_utf8(args.textfile) as fp:
        sentences = fp.readlines()

    sa = []
    if args.bychar:
        sa = (list(s.strip()) for s in sentences)
    else:
        sa = (s.strip().split() for s in sentences)
    m = Markovator(sa, order=args.order)
    for i in range(args.num):
        a = m.generate()
        if args.bychar:
            print(u''.join(m.generate()))
        else:
            print(u' '.join(m.generate()))

