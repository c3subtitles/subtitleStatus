import re
import textwrap


def chunks(text):
    """Read `text`, splitting it at doubled linebreaks"""
    lines = []
    for line in text.splitlines():
        lines.append(re.sub(' {2,}', ' ', line.strip()))
    return '\n'.join(lines).split('\n\n')


def groups(transcript):
    result = []
    current = []

    for line in transcript.splitlines():
        if line.strip() == '':
            result.append(list(current))
            current = []
        else:
            current.append(re.sub(' {2,}', ' ', line.strip()))

    if current:
        result.append(current)
    return result


def sbv_from_srt(transcript):
    subtitles = groups(transcript)
    result = ''

    for subtitle in subtitles:
        group = [subtitle[1].replace(' --> ', ',')]
        group += subtitle[2:]
        group += ['', '']
        result += '\n'.join(group)

    return result


def pad_from_trint(text):
    out = ""
    text = sbv_from_srt(text.replace('\r\n', '\n'))

    for chunk in chunks(text):
        lines = chunk.splitlines()

        for line in lines[2:]:
            if line.strip() == '':
                continue
            out += ' ' + line

    return out.replace('\n\n', '\n')


def timing_from_pad(text):
    transcript = []
    for line in text.splitlines():
        if line == '':
            continue
        elif line[0] == '*' and line[-1] == '*':
            transcript.append(line)
        else:
            transcript.extend((l.strip()
                               for l in textwrap.fill(line, width=42).splitlines()))

    length = len(transcript)
    odd = False

    if length % 2 == 1:
        length -= 1
        odd = True

    chunks = ["\n".join([transcript[i], transcript[i + 1], ''])
              for i in range(0, length, 2)]

    if odd:
        chunks.append(transcript[-1])

    return '\n'.join(chunks).replace('\n\n\n', '\n\n').strip()


def fix_sbv_linebreaks(transcript, sbv):
    transcript_chunks = chunks(transcript)
    chunks = chunks(sbv)
    sbv_timestamps = []
    sbv_chunks = []

    for chunk in chunks:
        parts = chunk.splitlines()
        sbv_timestamps += [parts[0]] * (len(parts) - 1)
        sbv_chunks += parts[1:]

    lines = []
    current_chunk = 0
    total_sbv_chunks = len(sbv_chunks)

    for chunk in transcript_chunks:
        if current_chunk >= total_sbv_chunks:
            raise ValueError("Garbage at end of Transcript file.")

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
            # collect the timestamp, in case this is then last SBV chunk
            timestamp = sbv_timestamps[current_chunk].split(',')[1]
            current_chunk += 1

        lines.append(("{},{}\n{}".format(timestamp_begin, timestamp, line)))


    return '\n\n'.join(lines)
