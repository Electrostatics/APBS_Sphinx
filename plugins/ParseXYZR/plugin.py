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

class ParseXYZR(BasePlugin):
    '''Plugin for parsing "xyzr" files.
    This plugin parses files that contain atomic data where each row is an
    atom.  The first three columns are it's X, Y, and Z positions in space,
    the fourth column is it's radius, and the fifth column is it's charge.
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._data = {}

        _log.info("ParseXYZR plug-in initialized.")


    @classmethod
    def script_name(cls):
        return "parse_xyzr"


    @classmethod
    def sinks(cls):
        return ['text']


    @classmethod
    def sources(cls):
        return ['apbs_atom', 'text']


    async def run(self):
        seq = 1
        while True:
            data = await self.read_data()
            if data:
                for line in data['text']['lines']:
                    x, y, z, r, c = line.split()
                    self._data = {'id': '?',
                                  'label_alt_id': '?',
                                  'label_asym_id': '?',
                                  'label_atom_id': '?',
                                  'label_comp_id': '?',
                                  'label_entity_id': '?',
                                  'label_seq_id': seq,
                                  'type_symbol': '?',
                                  'auth_asym_id': '?',
                                  'Cartn_x': float(x),
                                  'Cartn_y': float(y),
                                  'Cartn_z': float(z),
                                  'radius': float(r),
                                  'charge': float(c)}
                    seq += 1

                    await self.publish(self._data)

            else:
                break

        await self.done()


    def xform_data(self, data, to_type):
        if to_type == 'apbs_atom':
            return self._tm.new_apbs_atom(data)

        elif to_type == 'text':
            return self._tm.new_text(lines=[str(data)])
