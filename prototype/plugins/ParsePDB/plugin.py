# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python ff=unix sw=4 ts=4 sts=4 et:
# APBS -- Adaptive Poisson-Boltzmann Solver
#
#  Nathan A. Baker (nathan.baker@pnnl.gov)
#  Pacific Northwest National Laboratory
#
#  Additional contributing authors listed in the code documentation.
#
# Copyright (c) 2010-2016 Battelle Memorial Institute. Developed at the
# Pacific Northwest National Laboratory, operated by Battelle Memorial
# Institute, Pacific Northwest Division for the U.S. Department of Energy.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# Neither the name of the developer nor the names of its contributors may be
# used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.
#}}}

import asyncio
import logging

from sphinx.plugin import BasePlugin
from .pdb import *

__author__ = 'Keith T. Star <keith@pnnl.gov>'

_log = logging.getLogger()

def define_types(tm):
    '''Define a new Type

    We need a type to hold a PDB file -- at least the interesting bits.  This
    is purposely sparse in the interest in time and efficiency.  Our purpose
    is not to convert to mmCIF, and we'll add more if necessary.
    '''
    tm.define_type('pdb_file',
                   { 'idCode': {'$ref': '#/definitions/entry/properties/id'},
                     'atoms' : {
                         'type': 'array',
                         'items' : {'$ref': '#/definitions/atom_site'}}})


class ParsePDB(BasePlugin):
    '''Plugin for parsing PDB files.
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._pdb = {'idCode': None, 'atoms': []}
        
        _log.info("ParsePDB plug-in initialized.")


    @classmethod
    def script_name(cls):
        return "parse_pdb"


    @classmethod
    def sinks(cls):
        return ['text']


    @classmethod
    def sources(cls):
        return ['pdb_file', 'text']


    @asyncio.coroutine
    def run(self):
        while True:
            data = yield from self.read_data()
            if data:
                for line in data['text']['lines']:
                    record_type, record_data = parsePDBRecord(line)

                    if record_type == 'HEADER':
                        self._pdb['idCode'] = record_data.idCode

                    elif record_type == 'COMPND':
                        # TODO: This is defined piecemeal across multiple lines. It
                        # maps MOL_ID to ATOM entries -- somehow.  It's not clear
                        # how it manages this from the specification.
                        pass
                        
                    elif record_type == 'ATOM' or record_type == 'HETATM':
                        atom = {'group_PDB': record_type,
                                'id': str(record_data.serial),
                                'type_symbol': record_data.name,
                                'label_alt_id': record_data.altLoc,
                                'Cartn_x': record_data.x,
                                'Cartn_y': record_data.y,
                                'Cartn_z': record_data.z,
                                'occupancy': record_data.occupancy,
                                'B_iso_or_equiv': record_data.tempFactor,
                                'label_seq_id': record_data.resSeq,
                                'label_comp_id': record_data.resName,
                                'label_asym_id': record_data.chainID,
                                'auth_asym_id': record_data.chainID, # Why?  Is this correct?
                                'label_atom_id': record_data.name,
                                'label_entity_id': "1"} # TODO: Fix this.  See COMPND, above.
                        if record_data.charge:
                            atom['pdbx_formal_charge'] = record_data.charge
                            
                        self._pdb['atoms'].append(atom)
                                
            else:
                break

        # We need to wait until the entire PDB file is read before we can publish.
        self._tm.new_pdb_file(self._pdb)
        yield from self.publish((self._pdb))
        yield from self.done()


    def xform_data(self, data, to_type):
        record_type, record_data = data

        if to_type == 'pdb_file':
            return self._tm.new_pdb(data)

        elif to_type == 'text':
            lines = ['id: ' + data['idCode'] + '\n']
            for a in data['atoms']:
                atom = ''
                for x, y in a.items():
                    atom += x + ': ' + str(y) + '\t'

                lines.append(atom + '\n')

            return self._tm.new_text(lines=lines)
