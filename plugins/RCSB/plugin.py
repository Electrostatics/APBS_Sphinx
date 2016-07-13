import asyncio
import logging
import os, urllib
import urllib.request

from sphinx.plugin import BasePlugin

_log = logging.getLogger()

LINE_COUNT = 100

class RCSB(BasePlugin):
    '''Plugin for parsing PDB files.
    '''
    def __init__(self, file, **kwargs):
        super().__init__(**kwargs)

        self.path = file

        _log.info("RCSB plug-in initialized.")


    @classmethod
    def script_name(cls):
        return "get_RCSB"


    @classmethod
    def sinks(cls):
        return ['text']


    @classmethod
    def sources(cls):
        return ['text']



    @asyncio.coroutine
    def run(self):

        path = self.path
        URLpath = "http://www.rcsb.org/pdb/cgi/export.cgi/" + path + \
                                      ".pdb?format=PDB&pdbId=" + path + "&compression=None"
        file = urllib.request.urlopen(URLpath)

        if file.getcode() != 200 or 'nosuchfile' in file.geturl() :
            print ("Error")
            #Not sure how this error should be handled


        reads = file.read()

        s = reads.decode('utf-8')
        lines = s.split('\n')
        data = self._tm.new_text(lines=lines)

        yield from self.publish((data))

        yield from self.done()

    def xform_data(self, data, to_type):

        return data
