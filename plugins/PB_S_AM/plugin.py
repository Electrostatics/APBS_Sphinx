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

from .pbam_sph import PBAM_Solver

__author__ = 'Lisa Felberg <lisa.felberg@pnnl.gov>'

_log = logging.getLogger()

def run_pbam(molecules):
    '''Start the pbam process.
    We have to instantiate the solver, and then run 'run_pbam' in the
    same process.
    '''
    # TODO: All of the following belong in a configuration file.
    solver = PBAM_Solver(runname='tst', runtype='energyforce',
                         temp=300.0, epsilons=80.00, 
                         epsiloni=1.5, salt=0.01
                         )

    result = solver.run_solv(molecules)

    del solver
    return result


class PB_S_AM(BasePlugin):
    '''Plugin for running pbam flow
    '''
    def __init__(self, **kwargs):
        self._molecules = []

        super().__init__(**kwargs)
        _log.info("PBAM plug-in initialized.")


    @classmethod
    def script_name(cls):
        return "pbam"


    @classmethod
    def sinks(cls):
        return ['apbs_atom']


    @classmethod
    def sources(cls):
        return ['text']


    @asyncio.coroutine
    def run(self):
        try:
            # Collect all of the atoms that are available.
            while True:
                data = yield from self.read_data()
                if data:
                    value = data['apbs_atom']
                    self._molecules.append({
                        'pos': (
                            value['Cartn_x'],
                            value['Cartn_y'],
                            value['Cartn_z']
                        ),
                        'radius': value['radius'],
                        'charge': value['charge']
                    })
                else:
                    break

            # Run Geoflow in a separate process
            result = yield from self.runner.run_as_process(run_pbam,
                    {'atoms': self._molecules})

            yield from self.publish(self._tm.new_text(lines=[str(result)]))

            yield from self.done()
        except Exception as e:
            _log.exception('Unhandled exception:')


    def xform_data(self, data, to_type):
        return data

