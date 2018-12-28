def chunks(text):
    """Read `text`, splitting it at doubled linebreaks"""
    lines = []
    for line in text.split('\n'):
        lines.append(re.sub(' {2,}', ' ', line.strip()))
    return '\n'.join(lines).split('\n\n')


def pad_from_trint(text):
    out = ""

    for chunk in chunks(text):
        lines = chunk.split('\n')

        for line in lines[2:]:
            if line == '':
                continue
            out += ' ' + line

    return out.replace('\n\n', '\n')
