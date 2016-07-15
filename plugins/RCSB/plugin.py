import logging
import os, urllib
import urllib.request

from sphinx.plugin import BasePlugin

_log = logging.getLogger()


class RCSB(BasePlugin):
    '''Plugin for fetching proteins from RCSB database.
    '''
    def __init__(self, file, **kwargs):
        super().__init__(**kwargs)

        self.protein = file

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



    async def run(self):

        protein = self.protein
        URLpath = "http://www.rcsb.org/pdb/cgi/export.cgi/" + protein + \
                                      ".pdb?format=PDB&pdbId=" + protein + "&compression=None"
        file = urllib.request.urlopen(URLpath)

        if file.getcode() != 200 or 'nosuchfile' in file.geturl() :
            err = "{} does not exist, or is not available".format(protein)
            _log.error(err)
            raise PDBDoesntExist(err)
            #Not sure how this error should be handled


        reads = file.read()
        s = reads.decode('utf-8')
        lines = s.split('\n')
        data = self._tm.new_text(lines=lines)
        await self.publish((data))
        await self.done()

    def xform_data(self, data, to_type):
        return data

class PDBDoesntExist(Exception):
    pass
