# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python ff=unix noet sts=0 sw=4 ts=4 :
# APBS -- Adaptive Poisson-Boltzmann Solver
#
#  Nathan A. Baker (nathan.baker@pnnl.gov)
#  Pacific Northwest National Laboratory
#
#  Additional contributing authors listed in the code documentation.
#
# Copyright (c) 2010-2015 Battelle Memorial Institute. Developed at the
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
import simplejson as json

from sphinx.plugin import BasePlugin

from .geoflow import Geoflow_Solver

__author__ = 'Keith T. Star <keith@pnnl.gov>'

_log = logging.getLogger()


def run_geoflow(atoms):
	'''Start the geoflow process.
	We have to instantiate the solver, and then run 'process_molecule' in the
	same process.  There isn't much point in making this a method of the
	plugin class.  At least not that I can see now.  There may however be a
	better way to do this in the future.
	'''
	# TODO: All of the following belong in a configuration file.  I like the
	# idea of a geoflow config building module.  It would assist the user
	# with the meaning of the various values, as well as tracking, naming and
	# locating the configs the user has created.
	solver = Geoflow_Solver(pres_i=0.008, gama_i=0.0001, npiter=1,
			ngiter=1, tauval=1.40, prob=0.0, ffmodel=1, sigmas=1.5828,
			epsilonw=0.1554, vdwdispersion=0, extvalue=1.90, iadi=0,
			alpha=0.50, tol=1e-4, tottf=3.5, dcel=0.25, maxstep=20,
			epsilons=80.00, epsilonp=1.5, radexp=1, crevalue=0.01,
			density=0.03346)

	result = solver.process_molecule(atoms)

	del solver
	return result


class Geoflow(BasePlugin):
	'''Plugin for running geometric flow
	'''
	def __init__(self, **kwargs):
		self._atoms = []

		super().__init__(**kwargs)
		_log.info("Geoflow plug-in initialized.")


	@classmethod
	def script_name(cls):
		return "geoflow"


	@classmethod
	def sinks(cls):
		return [{'Type': 'atom/position-size'}]


	@classmethod
	def sources(cls):
		return [
			{'Type': 'text'}
		]


	@asyncio.coroutine
	def run(self):
		try:
			# Collect all of the atoms that are available.
			while True:
				data = yield from self._queue.get()
				if data:
					self._atoms.append(json.loads(data))
				else:
					break

			# Run Geoflow in a separate process
			result = yield from self.runner.run_as_process(run_geoflow,
					{'atoms': self._atoms})

			yield from self.publish(json.dumps(result))
			yield from self.done()
		except Exception as e:
			_log.exception('Unhandled exception:')
