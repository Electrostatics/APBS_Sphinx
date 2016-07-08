import asyncio
import logging
import os, urllib
import urllib.request

from sphinx.plugin import BasePlugin
#from .pdb import *



_log = logging.getLogger()



class RCSB(BasePlugin):
    '''Plugin for parsing PDB files.
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._data = None

        _log.info("RCSB plug-in initialized.")


    @classmethod
    def script_name(cls):
        return "get_RCSB"


    @classmethod
    def sinks(cls):
        return ['text']


    @classmethod
    def sources(cls):
        return ['pdb_file', 'text']


    @asyncio.coroutine
    def run(self):
        while True:
            file = None
            data = yield from self.read_data()
            if data:
                #_data = None
                #file = None
                for path in data['text']['lines']:
                    #_data = None
                    #file = None
                        #Doesn't work on Safari, need to use chrome
                    URLpath = "http://www.rcsb.org/pdb/cgi/export.cgi/" + path + \
                                  ".pdb?format=PDB&pdbId=" + path + "&compression=None"
                    print (URLpath)
                    try:
                        file = urllib.request.urlopen(URLpath)

                        if file.getcode() != 200 or 'nosuchfile' in file.geturl() :
                            raise IOError

                    except IOError:
                        print ("Error")
                        return None

                objects.append(file)
            print (objects)

            self._data = file
            yield from self.publish((self._data))
            yield from self.done()


    def xform_data(self, data, to_type):
        return data
