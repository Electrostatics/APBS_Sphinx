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

import logging

from sphinx.plugin import BasePlugin

__author__ = 'Keith T. Star <keith@pnnl.gov>'

_log = logging.getLogger()

def define_types(tm):
    '''Define a type to store force field data
    '''
    tm.add_raw_type('force_field',
                    { 'type': 'object',
                      'patternProperties': {
                          "^[A-Z]+[A-Z0-9']*$": { 'type': 'object',
                                                  'patternProperties': {
                                                      "^[A-Z]+[A-Z0-9']*$": { 'type': 'object',
                                                                              'properties': {
                                                                                  'charge': { 'type': 'number' },
                                                                                  'radius': { 'type': 'number' },
                                                                                  'group':  { 'type': 'string' }
                                                                              },
                                                                              'additionalProperties': False }
                                                  },
                                                  'additionalProperties': False }
                      },
                      'additionalProperties': False })


class ParseAMBER(BasePlugin):
    '''Plugin for parsing AMBER files.
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._ff = {}

        _log.info("ParseAMBER plug-in initialized.")


    @classmethod
    def script_name(cls):
        return "parse_amber"


    @classmethod
    def sinks(cls):
        return ['force_field', 'text']


    @classmethod
    def sources(cls):
        return ['text']


    async def run(self):
        while True:
            data = await self.read_data()
            if data:
                for line in data['text']['lines']:
                    if not line.startswith('#'):
                        residue, atom, charge, radius, group = line.split()
                        if not residue in self._ff:
                            self._ff[residue] = {}

                        self._ff[residue][atom] = {'charge': charge,
                                                   'radius': radius,
                                                   'group': group}

            else:
                break

        # It's best to wait until the entire file is read.  We could work around
        # this, but it's just easier not to try.  These aren't very long anyway.
        await self.publish(self._ff)
        await self.done()


    def xform_data(self, data, to_type):
        if to_type == 'force_field':
            return self._tm.new_force_field(data)

        elif to_type == 'text':
            txt = []
            for residue, atoms in data.items():
                txt.append(residue + ':')

                for atom, info in atoms.items():
                    txt.append('\t {}: charge {}, radius {}, group {}'.format(atom,
                                                                             info['charge'],
                                                                             info['radius'],
                                                                             info['group']))

            return self._tm.new_text(lines=txt)
