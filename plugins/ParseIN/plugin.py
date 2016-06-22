from plugins.ParseIN.apbs.parser.__init__ import TextEncoder
from plugins.ParseIN.apbs.parser.__init__ import TextDecoder
from plugins.ParseIN.apbs.parser.__init__ import JSONEncoder
from plugins.ParseIN.apbs.parser.__init__ import CalcInput
import json
import asyncio
import sys

from sphinx.plugin import BasePlugin

# from apbs import parser
# import apbs.calculation

# Turn in_file into pipeline file:
# First:
#  Read the read section's files.
#  e.g., diel_x_map = read_file(x) ...
#        diel_map = process_diel(diel_x_map, diel_y_map, etc.)
#
# Second:
#  Pass data to solver


# def define_types(tm):

#     tm.define_type('charge_file',{})
#     tm.define_type('diel_files', {})
#     tm.define_type(...)


#     tm.define_type('in_file' {
#         'type': 'object',
#         'properties': {
#             'charge_file': {
#                 'type': 'object',
#                 'properties': {
#                     'format':,
#                     'file'

#                 }
#             },
#             'diel_files': {
#                 'type': 'object',
#                 'properties': {
#                     'format':,
#                     'x_file':,
#                     'y_file':,
#                     'z_file':

#                 }
#             }

#             'read': {
#                 'type': 'object',
#                 'properties': {
#                     'file_type': # can be 'charge', 'diel', 'kappa', etc.,
#                     'format': # gz or dx
#                     'files': # an array
#                 }
#             },
#             'calcs': {
#                 'type': 'object',
#                 'properties': {}
#             },
#             'prints': {
#                 'type': 'object',
#                 'properties': {}
#             }
#         }
#     })






class ParseIN(BasePlugin):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._data = None


    @classmethod
    def script_name(cls):
        return 'parse_infiles'

    @classmethod
    def sinks(cls):
        return ['text']

    @classmethod
    def sources(cls):
        return['in_file', 'text']





    @asyncio.coroutine
    def run(self):
        infile = []
        while True:
            data = yield from self.read_data()
            if data:
                for line in data['text']['lines']:
                    infile.append(line)



            else:
                break


        # dec = TextDecoder()
        # dec.feed(result)
        # enc = TextEncoder()
        # self._data = dec.parse()

        #parser = apbs.parser.TextDecoder()
        parser = TextDecoder()
        parser.feed(infile)
        #parser.parse()
        self._data = parser.parse()
        vars(parser.apbs_input)



        yield from self.publish(self._data)



        yield from self.done()





    def xform_data(self, data, to_type):


        if to_type == 'text':
            return self._tm.new_text(lines=[str(data)])


        elif to_type == 'in_file':

            infile_dict = {'read': {}, 'calcs': {}, 'prints': {}}

            return self._tm.new_in_file(infile_dict)
