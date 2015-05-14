# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python sw=4 ts=4 sts=4
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

from sphinx.plugin import BasePlugin

__author__ = 'Keith T. Star <keith@pnnl.gov>'

_log = logging.getLogger()

class ReadFile(BasePlugin):
	'''Plugin for reading a file
	This reads a text file, and yields a single line at a time.  We'll likely
	as not find that we need different sorts of readers.  The source type for
	this plugin should reflect the type of data that it produces.
	'''
	def __init__(self, file, **kwargs):
		self._file = file
		super().__init__(**kwargs)
		_log.info("ReadFile plug-in initialized.")


	@classmethod
	def script_name(cls):
		return "read_file"


	@classmethod
	def sources(cls):
		return [
			{'Type': 'text', }
		]


	@asyncio.coroutine
	# I don't know that this is necessary, so much as it proves pedagogical.
	def open(self):
		return open(self._file, 'r')


	@asyncio.coroutine
	def run(self):
		file = yield from self.open()
		for line in file:
			yield from self.publish(line)

		yield from self.done()
		file.close()
