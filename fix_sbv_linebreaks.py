#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# File: .../fix_sbv_linebreaks.py
#
# This File fixes the Youtube Fuckup when youtube syncs an sbv-File and breaks
# the lines where it shouldn't.
#
# You will need the Transcript File and the sbv File
#==============================================================================

import sys


from www.transforms import fix_sbv_linebreaks


if __name__ == '__main__':
    # Check if enough arguments are given on the command line
    if len(sys.argv) < 3:
        sys.exit("Two files needed as input! Try again.")
    transcript_file = sys.argv[1]
    sbv_file = sys.argv[2]


    # Check if the sbv-filename fits
    if sbv_file[-4:] != ".sbv":
        sys.exit("The second file has to be the *.sbv file. Try again.")


    # Check the Transcript File and read it in an array
    transcript = ''
    try:
        with open(transcript_file, 'r') as f:
            transcript = f.read()
    except IOError as e:
        sys.exit("Transcript file is not readable or does not exist: {}".format(e))

    # Check the sbv file and read it into an array
    sbv = ''
    try:
        with open(sbv_file, 'r') as f:
            sbv = f.read()
    except IOError as e:
        sys.exit("SBV file is not readable or does not exist: {}".format(e))

    print(fix_sbv_linebreaks(transcript, sbv))
