"""

"""

import re
import logging


def format_basic(s_in):
    return str(s_in or '').strip().lower()


def format_address(field):

    f = format_basic(field)
    f = re.sub('[\n\r\t\"\'\\\(\)=\?\-]', '', f)

    formatted = []
    for address in f.split(','):

        # Trim and lowercase
        address = address.strip().lower()

        # Change all whitespace to spaces
        address = re.sub('\s', ' ', address)

        formatted.append(address)

    while '' in formatted:
        formatted.remove('')

    return formatted


def format_text(text):
    """
    Format the given text into plain words.
    """

    text = format_basic(text)

    lines = []
    for line in text.splitlines():
        if re.match('^[ ]*[>]+ ', line):
            continue
        if re.match('^[ ]*[>]+$', line):
            continue
        if re.match('^  (from|sent|to|cc|subject|bcc|date):', line):
            continue
        if re.match('^[\W]*$', line):
            continue

        lines.append(line)

    text = ' '.join(lines)

    # Change all whitespace to spaces
    text = re.sub('\s', ' ', text)

    # Replace all links
    text = re.sub('[\S]*http[s]?://[\S]+', 'http', text)

    # Replace all forward message headers
    text = re.sub('on ([\w]+, )?[\w]+ [\d]+, [\d]+(,)? (at )?[\d]+:[\d]+(,)? .*? wrote:', 'forward', text)

    #Replace all email addresses (very crude)
    text = re.sub('[\S]+@[\S]+', 'email', text)

    # Replace all times
    text = re.sub('[\d]+((am|pm)|(:[\d]+(am|pm)?))', 'time', text)

    # Remove all apostrophes
    text = re.sub('\'', '', text)

    # Turn ALL non-word characters into whitespace
    text = re.sub('\W', ' ', text)

    # Turn underscores into whitespace
    text = re.sub('_', ' ', text)

    # Replace all digit-only tokens
    text = re.sub(' [\d ]+ ', ' number ', text)

    return text
