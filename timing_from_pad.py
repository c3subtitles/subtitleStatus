#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import re
import textwrap

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit("usage: ./{} transcript".format(sys.argv[0]))

    transcript = []
    try:
        with open(sys.argv[1], 'r') as file:
            for line in file:
                if line == '':
                    continue
                elif line[0] == '*' and line[-1] == '*':
                    transcript.append(line)
                else:
                    transcript.extend(textwrap.fill(line, width=42).split('\n'))
    except IOError as err:
        sys.exit("Transcript not readable: {}").format(err)

    chunks = ["\n".join([transcript[i], transcript[i + 1], '']) for i in range(0, len(transcript), 2)]

    print("\n".join(chunks))
