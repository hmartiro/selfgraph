"""

"""

import yaml
import mailbox
import logging
from email.header import decode_header

from ..utils.format import format_basic, format_text, format_address


class EmailParser():

    MAX_LENGTH = 10000

    def __init__(self, email_file):

        self.email_file = email_file

    def get_payload_text(self, msg):
        """
        Return all plain text sections of this email's payload concatenated
        together, but with no formatting except truncation to a max length.

        """

        if msg.is_multipart():
            payload = msg.get_payload()
            logging.debug('Processing multipart message of {} parts'.format(len(payload)))
            return '\n'.join(self.get_payload_text(part) for part in payload)

        content_type = msg.get_content_type()
        logging.debug('Content type: {}'.format(content_type))

        if content_type == 'text/plain':

            charset = msg.get_content_charset()
            logging.debug('Charset: {}'.format(charset))

            payload = msg.get_payload(None, True)

            if charset:
                try:
                    payload = payload.decode(charset)
                except Exception as e:
                    logging.warning('Cannot decode payload, skipping: {}'.format(e))
                    return ''
            else:
                payload = str(payload)

            if len(payload) > self.MAX_LENGTH:
                logging.warning('Payload is too long ({}), truncating.'.format(len(payload)))
                payload = payload[:10000]

            logging.debug('Read plain text payload of length {}'.format(len(payload)))
            return payload
        else:
            logging.debug('Skipping, payload is not plain text.')
            return ''

    def decode_field(self, header):

        if not header:
            return header

        header_str = ''
        decoded_sections = decode_header(header)
        print(decoded_sections)
        for data, encoding in decoded_sections:

            if not data:
                continue

            header_str += ' '
            if isinstance(data, str):
                header_str += data
                print('Adding string: {}'.format(data))
                continue

            print('Decoding bytes {} using {}'.format(data, encoding))
            try:
                decoded = data.decode(encoding or 'utf-8')
            except LookupError:
                decoded = data.decode('utf-8')

            print('Decoded string: {}'.format(decoded))
            header_str += decoded

        print('Full header field: {}'.format(header_str))
        return header_str

    def parse(self):

        logging.info('Email file: {}'.format(self.email_file))

        out = []
        i = 0
        for msg in mailbox.mbox(self.email_file):

            logging.info('--------- Parsing message {} ---------'.format(i))

            msg_data = dict(type='email')
            msg_data['date'] = self.decode_field(msg['date'])
            msg_data['date'] = format_basic(msg_data['date'])

            for field in ['from', 'to', 'cc', 'bcc']:
                msg_data[field] = self.decode_field(msg[field])
                msg_data[field] = format_address(msg_data[field])
                logging.debug('{}: {}'.format(field, msg_data[field]))

            try:
                payload = format_text(self.get_payload_text(msg))
            except Exception as e:
                raise e

            subject = self.decode_field(msg['subject'])
            subject = format_text(subject)
            text = ' '.join([subject, payload])
            msg_data['text'] = text
            logging.debug(text)

            out.append(msg_data)
            i += 1

        return out

if __name__ == '__main__':

    import sys
    import pickle

    mbox_file = sys.argv[1]
    if len(sys.argv) > 2:
        out_file = '{}.pickle'.format(sys.argv[2])
    else:
        out_file = '{}.pickle'.format(mbox_file)
    ep = EmailParser('{}.mbox'.format(mbox_file))
    data = ep.parse()
    with open(out_file, 'wb') as f:
        f.write(pickle.dumps(data))
    #print(yaml.dump(data, width=10000))
