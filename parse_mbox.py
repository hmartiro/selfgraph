"""

"""

import re
import sys
import yaml
import mailbox
from pprint import pprint
from collections import OrderedDict

class UnsortableList(list):
    def sort(self, *args, **kwargs):
        pass

class UnsortableOrderedDict(OrderedDict):
    def items(self, *args, **kwargs):
        return UnsortableList(OrderedDict.items(self, *args, **kwargs))

yaml.add_representer(
    UnsortableOrderedDict,
    yaml.representer.SafeRepresenter.represent_dict
)

class EmailParser():

    def __init__(self, email_file):

        self.email_file = email_file

    @staticmethod
    def format_field(field):

        f = re.sub('[\n\r\t\"]', '', field)
        f = f.split(',')
        f = [entry.strip() for entry in f]
        while '' in f:
            f.remove('')

        return f

    def parse(self):

        out = []
        for m in mailbox.mbox(self.email_file):

            date = m['date'] or ''
            frm = m['from'] or ''
            to = m['to'] or ''
            cc = m['cc'] or ''
            bcc = m['bcc'] or ''
            text = m['subject'] or ''

            to = self.format_field(to)
            cc = self.format_field(cc)
            bcc = self.format_field(bcc)

            text = re.sub('[\n\r\t]', '', text)

            d = UnsortableOrderedDict((
                ('type', 'email'),
                ('date', date),
                ('from', frm),
                ('to', to),
                ('cc', cc),
                ('bcc', bcc),
                ('text', text)
            ))
            out.append(d)

        return out

if __name__ == '__main__':

    print(sys.argv[1])
    mbox_file = sys.argv[1]

    ep = EmailParser(mbox_file)
    out = ep.parse()
    print(yaml.dump(out, width=10000))
