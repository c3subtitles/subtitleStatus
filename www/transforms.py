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

        for line in lines[1:]:
            if line.strip() == '':
                continue
            out += ' ' + line

    return out.replace('\n\n', '\n')


def pad_from_youtube(text):
    out = ""

    for chunk in chunks(text.replace('\r\n', '\n')):
        lines = chunk.splitlines()

        for line in lines[1:]:
            if line == '':
                continue
            if line[0] == '[' and line[-1] == ']':
                 # keep this as a separate line
                 out += '\n' + line + '\n'
            else:
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
    cs = chunks(sbv)
    sbv_timestamps = []
    sbv_chunks = []

    for chunk in cs:
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

        lines.append(("{},{}\n{}".format(timestamp_begin, timestamp, line.replace('\n', '<br/>'))))


    return '\n\n'.join(lines)


FILLER = re.compile(r'^\[(Füller, bitte in amara entfernen|Filler, please remove in amara)\]$', flags=re.IGNORECASE)
TIMESTAMP = re.compile(r'^\d+:\d{2}:\d{2}.\d{3},\d+:\d{2}:\d{2}.\d{3}$', flags=re.MULTILINE)
COMPONENTS = re.compile(r'^(?P<start_hours>\d+):(?P<start_minutes>\d{2}):(?P<start_seconds>\d{2}).(?P<start_milliseconds>\d{3}),(?P<end_hours>\d+):(?P<end_minutes>\d{2}):(?P<end_seconds>\d{2}).(?P<end_milliseconds>\d{3})$')


def align_transcript_sbv(transcript, sbv):
    transcript.replace("\r\n", "\n")
    sbv.replace("\r\n", "\n")

    transcript_blocks = transcript.split("\n\n")
    sbv_blocks = [{'timestamp': timestamp,
                   'block': block,
                   'lines': [line
                              for line in block.split("\n")
                              if not line.isspace() and line != ''],
                   } for (timestamp, block) in zip(TIMESTAMP.findall(sbv),
                                                   TIMESTAMP.split(sbv)[1:])
                  ]

    alignment = []
    for block in transcript_blocks:
        words = block.split()

        start = None
        sbv_block = None
        sbv_words = []
        dropped = 0

        while len(words) > 0:
            if len(sbv_words) == 0:
                sbv_block = sbv_blocks.pop(0)
                sbv_words = sbv_block['block'].split()
                dropped = 0

            if start is None:
                start = sbv_block['timestamp']

            assert words.pop(0) == sbv_words.pop(0)
            dropped += 1

        end = sbv_block['timestamp']
        this = start
        other = end

        if sbv_words:
            lines = sbv_block['lines']
            chars = 0.0
            total = sum([len(line) for line in lines])
            while dropped > 0:
                dropped -= len(lines[0].split())
                assert dropped >= 0
                chars += len(lines[0])
                lines.pop(0)

            assert chars <= total
            this, other = interpolate(start, end, chars / total)

            sbv_block = "\n".join(lines)
            sbv_blocks.insert(0, {'timestamp': other,
                                  'lines': lines,
                                  'block': sbv_block,
                                  })
            sbv_block = None
        elif start != end:
            this = "{},{}".format(start.split(",")[0], end.split(",")[1])

        block = "\n".join([line for line in block.split("\n") if not FILLER.match(line)])
        alignment.append("{}\n{}".format(this, block))

    return "\n\n".join(alignment)


def interpolate(start, end, percentage):
    def ms(components, prefix='start'):
        return (int(components['{}_milliseconds'.format(prefix)])
                + 1000 * (int(components['{}_seconds'.format(prefix)])
                          + 60 * (int(components['{}_minutes'.format(prefix)])
                                  + 60 * (int(components['{}_hours'.format(prefix)])))))

    def ts(ms):
        milliseconds = ms % 1000
        ms = ms // 1000
        seconds = ms % 60
        ms = ms // 60
        minutes = ms % 60
        ms = ms // 60
        hours = ms

        return "{:0d}:{:02d}:{:02d}.{:03d}".format(hours, minutes, seconds, milliseconds)

    start_match = COMPONENTS.match(start)
    end_match = COMPONENTS.match(end)

    start_ms = ms(start_match.groupdict())
    start_duration = ms(start_match.groupdict(), prefix='end') - start_ms
    end_ms = ms(end_match.groupdict(), prefix='end')
    end_duration = end_ms - ms(end_match.groupdict())

    midpoint = start_ms + start_duration + int(percentage * end_duration)
    assert start_ms <= midpoint <= end_ms

    this = "{},{}".format(ts(start_ms), ts(midpoint))
    other = "{},{}".format(ts(midpoint), ts(end_ms))

    return this, other
