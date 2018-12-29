#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

from www.transforms import pad_from_trint


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit("usage: ./{} transcript.sbv".format(sys.argv[0]))

    transcript = []
    try:
        with open(sys.argv[1], 'r') as file:
            transcript = file.read()
    except IOError as err:
        sys.exit("Transcript not readable: {}").format(err)

    print(pad_from_trint(transcript))
