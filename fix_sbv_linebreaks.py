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


import os
import sys


def chunks(file):
    """Read `file`, splitting it at doubled linebreaks"""
    return file.read().replace('\r\n', '\n').split('\n\n')


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
    try:
        with open(transcript_file, 'r') as f:
            transcript_chunks = chunks(f)
    except IOError as e:
        sys.exit("Transcript file is not readable or does not exist: {}".format(e))

    # Check the sbv file and read it into an array
    try:
        with open(sbv_file, 'r') as f:
            chunks = chunks(f)
            sbv_timestamps = []
            sbv_chunks = []

            for chunk in chunks:
                parts = chunk.split('\n')
                sbv_timestamps.append(parts[0])
                sbv_chunks.append('\n'.join(parts[1:]))
    except IOError as e:
        sys.exit("SBV file is not readable or does not exist: {}".format(e))


    lines = []
    current_chunk = 0
    total_sbv_chunks = len(sbv_chunks)

    for chunk in transcript_chunks:
        if current_chunk >= total_sbv_chunks:
            sys.exit("Garbage at end of Transcript file.")

        # collect all the SBV chunks that form this chunk
        # we start at the timestamp of then first SBV chunk
        timestamp_begin, timestamp = sbv_timestamps[current_chunk].split(',')
        line = sbv_chunks[current_chunk]
        current_chunk += 1

        # append SBV chunks until we match the current transcript chunk
        while chunk != line and current_chunk < total_sbv_chunks:
            # separator may be a space or newline
            separator = chunk[len(line)]
            line += separator + sbv_chunks[current_chunk]
            # collect then timestamp, in case this is then last SBV chunk
            timestamp = sbv_timestamps[current_chunk].split(',')[1]
            current_chunk += 1

        lines.append(("{},{}\n{}".format(timestamp_begin, timestamp, line)))


    print('\n\n'.join(lines))
