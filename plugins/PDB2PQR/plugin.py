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
import os

from sphinx.plugin import BasePlugin
from .main import mainCommand

__author__ = 'Keith T. Star <keith@pnnl.gov>'

_log = logging.getLogger()

class PDB2PQR(BasePlugin):
    '''Stuff PDB2PQR into Sphnx
    '''
    def __init__(self, opts={}, **kwargs):
        opt_schema_file = os.path.join(os.path.dirname(__file__), "options.json")

        # After instantiating the super class, self._opts will contain the options
        # passed to the plugin.
        super().__init__(opt_schema=opt_schema_file, options=opts, **kwargs)

        _log.info("PDB2PQR plug-in initialized.")


    @classmethod
    def script_name(cls):
        return "pdb2pqr"


    @classmethod
    def sinks(cls):
        return None


    @classmethod
    def sources(cls):
        return ['text']


    async def run(self):
        cmd = ['pdb2pqr-sphinx']
        print(self._opt_handler.get_misc('ff'))
        for k, v in self._opts.items():
            print('foo', k, v)
            if k != 'pdb':
                try:
                    misc = self._opt_handler.get_misc(k)
                    print(misc)
                    cmd.append(misc['cmd_opt'].format(v))
                except KeyError:
                    pass

            else:
                pdb = v

            print('cmd', cmd)


        cmd.append(pdb)
        print(cmd)
    
#        pqr = mainCommand(['pdb2pqr-sphinx', '-v', '--ff={}'.format(self._ff), self._pdb])

        pqr = mainCommand(cmd)

        await self.publish(self._tm.new_text({'lines': pqr.split('\n')}))
        await self.done()


    def xform_data(self, data, to_type):
        return data
