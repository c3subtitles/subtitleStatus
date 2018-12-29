#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

from wwww.transforms import timing_from_pad


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit("usage: ./{} transcript".format(sys.argv[0]))

    print

    transcript = []
    try:
        with open(sys.argv[1], 'r') as file:
            transcript = file.read()
    except IOError as err:
        sys.exit("Transcript not readable: {}").format(err)

    print(timing_from_pad(transcript))
