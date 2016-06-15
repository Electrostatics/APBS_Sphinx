from plugins.ParseIn.__init__ import TextEncoder
from plugins.ParseIn.__init__ import TextDecoder
from plugins.ParseIn.__init__ import JSONEncoder
from plugins.ParseIn.__init__ import CalcInput
import json
import asyncio
import sys

from sphinx.plugin import BasePlugin





class ParseIn(BasePlugin):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        _data = {}
        #self._data = {'reads':[], 'calc': [], 'prints'}

    @classmethod
    def script_name(cls):
        return 'parse_infile'

    @classmethod
    def sinks(cls):
        return ['text']

    @classmethod
    def sources(cls):
        return['in_file', 'text']





    @asyncio.coroutine
    def run(self):

        while True:
            data = yield from self.read_data()
            if data:
                result = []
                for line in data['text']['lines']:
                    # ex = ''
                    # ex +=line
                    result.append(line)


            else:
                break


            dec = TextDecoder()
            dec.feed(result)
            enc = TextEncoder()
            self._data = {enc.encode(dec.parse())}


            yield from self.publish(self._data)



        yield from self.done()





    def xform_data(self, data, to_type):

        # if to_type == 'text':
        #     lines = data.splitlines()
        #
        #     result = []
        #     for x in lines:
        #         data = ''
        #         data += x
        #
        #
        #         result.append(data)


        #return self._tm.new_text(lines=str(data))

        if to_type == 'text':
            return self._tm.new_text(lines=[str(data)])
